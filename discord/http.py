"""
The MIT License (MIT)

Copyright (c) 2015-present Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

import asyncio
import datetime
import logging
import ssl
from collections import deque
from typing import (
    Any,
    Callable,
    ClassVar,
    Coroutine,
    Dict,
    List,
    NamedTuple,
    Optional,
    Sequence,
    TYPE_CHECKING,
    Type,
    TypeVar,
    Union,
)
from urllib.parse import quote as _uriquote

import aiohttp

from . import utils
from .errors import (
    HTTPException,
    RateLimited,
    Forbidden,
    NotFound,
    LoginFailure,
    DiscordServerError,
    GatewayNotFound,
    CaptchaRequired,
)
from .file import _FileBase, File
from .utils import MISSING

if TYPE_CHECKING:
    from typing_extensions import Self

    from .channel import (
        TextChannel,
        DMChannel,
        PartialMessageable,
    )
    from .message import Attachment, Message
    from .flags import MessageFlags
    from .enums import InteractionType
    from .embeds import Embed

    from .types import (
        application,
        command,
        channel,
        interactions,
        message,
        oauth2,
        read_state,
        user,
    )
    from .types.snowflake import Snowflake

    from types import TracebackType

    T = TypeVar("T")
    BE = TypeVar("BE", bound=BaseException)
    Response = Coroutine[Any, Any, T]
    MessageableChannel = Union[
        TextChannel,
        DMChannel,
        PartialMessageable,
    ]

INTERNAL_API_VERSION = 9
CIPHERS = (
    "TLS_GREASE_5A",
    "TLS_AES_128_GCM_SHA256",
    "TLS_AES_256_GCM_SHA384",
    "TLS_CHACHA20_POLY1305_SHA256",
    "ECDHE-ECDSA-AES128-GCM-SHA256",
    "ECDHE-RSA-AES128-GCM-SHA256",
    "ECDHE-ECDSA-AES256-GCM-SHA384",
    "ECDHE-RSA-AES256-GCM-SHA384",
    "ECDHE-ECDSA-CHACHA20-POLY1305",
    "ECDHE-RSA-CHACHA20-POLY1305",
    "ECDHE-RSA-AES128-SHA",
    "ECDHE-RSA-AES256-SHA",
    "AES128-GCM-SHA256",
    "AES256-GCM-SHA384",
    "AES128-SHA",
    "AES256-SHA",
)

_log = logging.getLogger(__name__)


async def json_or_text(response: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
    text = await response.text(encoding="utf-8")
    try:
        if response.headers["content-type"] == "application/json":
            return utils._from_json(text)
    except KeyError:
        # Thanks Cloudflare
        pass

    return text


async def _gen_session(
    session: Optional[aiohttp.ClientSession],
) -> aiohttp.ClientSession:
    connector = None
    if session:
        connector = session.connector

    original = getattr(connector, "_ssl", None)
    if isinstance(original, ssl.SSLContext):
        ctx = original
    else:
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

    if session is not None and original is not None:
        if isinstance(original, bool) and not original:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        elif isinstance(original, aiohttp.Fingerprint):
            return session  # Cannot continue

    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.maximum_version = ssl.TLSVersion.TLSv1_3
    ctx.set_ciphers(":".join(CIPHERS))
    ctx.options |= ssl.OP_NO_SSLv2
    ctx.options |= ssl.OP_NO_SSLv3
    ctx.options |= ssl.OP_NO_COMPRESSION
    ctx.set_ecdh_curve("prime256v1")

    if connector is not None:
        connector._ssl = ctx  # type: ignore # Private attribute assignment
    else:
        connector = aiohttp.TCPConnector(limit=0, ssl=ctx)

    if session is not None:
        session._connector = connector
    else:
        session = aiohttp.ClientSession(connector=connector)
    return session


class MultipartParameters(NamedTuple):
    payload: Optional[Dict[str, Any]]
    multipart: Optional[List[Dict[str, Any]]]
    files: Optional[Sequence[File]]

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BE]],
        exc: Optional[BE],
        traceback: Optional[TracebackType],
    ) -> None:
        if self.files:
            for file in self.files:
                file.close()


def handle_message_parameters(
    content: Optional[str] = MISSING,
    *,
    username: str = MISSING,
    avatar_url: Any = MISSING,
    tts: bool = False,
    nonce: Optional[Union[int, str]] = MISSING,
    flags: MessageFlags = MISSING,
    file: _FileBase = MISSING,
    files: Sequence[_FileBase] = MISSING,
    embed: Optional[Embed] = MISSING,
    embeds: Sequence[Embed] = MISSING,
    attachments: Sequence[Union[Attachment, _FileBase]] = MISSING,
    message_reference: Optional[message.MessageReference] = MISSING,
    mention_author: Optional[bool] = None,
    channel_payload: Dict[str, Any] = MISSING,
) -> MultipartParameters:
    if files is not MISSING and file is not MISSING:
        raise TypeError("Cannot mix file and files keyword arguments.")
    if embeds is not MISSING and embed is not MISSING:
        raise TypeError("Cannot mix embed and embeds keyword arguments.")

    if file is not MISSING:
        files = [file]

    if attachments is not MISSING and files is not MISSING:
        raise TypeError("Cannot mix attachments and files keyword arguments.")

    payload: Any = {"tts": tts}
    if embeds is not MISSING:
        if len(embeds) > 10:
            raise ValueError("embeds has a maximum of 10 elements.")
        payload["embeds"] = [e.to_dict() for e in embeds]

    if embed is not MISSING:
        if embed is None:
            payload["embeds"] = []
        else:
            payload["embeds"] = [embed.to_dict()]

    if content is not MISSING:
        if content is not None:
            payload["content"] = str(content)
        else:
            payload["content"] = None

    if nonce is MISSING:
        payload["nonce"] = utils._generate_nonce()
    elif nonce:
        payload["nonce"] = nonce

    if message_reference is not MISSING:
        payload["message_reference"] = message_reference

    if avatar_url:
        payload["avatar_url"] = str(avatar_url)
    if username:
        payload["username"] = username

    if flags is not MISSING:
        payload["flags"] = flags.value

    if attachments is MISSING:
        attachments = files
    else:
        files = [a for a in attachments if isinstance(a, _FileBase)]

    if attachments is not MISSING:
        file_index = 0
        attachments_payload = []
        for attachment in attachments:
            if isinstance(attachment, _FileBase):
                attachments_payload.append(attachment.to_dict(file_index))
                file_index += 1
            else:
                attachments_payload.append(attachment.to_dict())

        payload["attachments"] = attachments_payload

    if channel_payload is not MISSING:
        payload = {
            "message": payload,
        }
        payload.update(channel_payload)

    # Legacy uploading
    multipart = []
    to_upload = [file for file in files if isinstance(file, File)] if files else None
    if to_upload:
        multipart.append({"name": "payload_json", "value": utils._to_json(payload)})
        payload = None
        for index, file in enumerate(to_upload):
            multipart.append(
                {
                    "name": f"files[{index}]",
                    "value": file.fp,
                    "filename": file.filename,
                    "content_type": "application/octet-stream",
                }
            )

    return MultipartParameters(payload=payload, multipart=multipart, files=to_upload)


def _gen_accept_encoding_header():
    return "gzip, deflate, br" if aiohttp.http_parser.HAS_BROTLI else "gzip, deflate"  # type: ignore


class Route:
    BASE: ClassVar[str] = f"https://discord.com/api/v{INTERNAL_API_VERSION}"

    def __init__(
        self,
        method: str,
        path: str,
        *,
        metadata: Optional[str] = None,
        **parameters: Any,
    ) -> None:
        self.path: str = path
        self.method: str = method
        # Metadata is a special string used to differentiate between known sub rate limits
        # Since these can't be handled generically, this is the next best way to do so.
        self.metadata: Optional[str] = metadata
        url = self.BASE + self.path
        if parameters:
            url = url.format_map(
                {
                    k: _uriquote(v) if isinstance(v, str) else v
                    for k, v in parameters.items()
                }
            )
        self.url: str = url

        # Major parameters
        self.channel_id: Optional[Snowflake] = parameters.get("channel_id")
        self.guild_id: Optional[Snowflake] = parameters.get("guild_id")

    @property
    def key(self) -> str:
        """The bucket key is used to represent the route in various mappings."""
        if self.metadata:
            return f"{self.method} {self.path}:{self.metadata}"
        return f"{self.method} {self.path}"

    @property
    def major_parameters(self) -> str:
        """Returns the major parameters formatted a string.

        This needs to be appended to a bucket hash to constitute as a full rate limit key.
        """
        return "+".join(
            str(k)
            for k in (
                self.channel_id,
                self.guild_id,
            )
            if k is not None
        )


class Ratelimit:
    """Represents a Discord rate limit.

    This is similar to a semaphore except tailored to Discord's rate limits. This is aware of
    the expiry of a token window, along with the number of tokens available. The goal of this
    design is to increase throughput of requests being sent concurrently rather than forcing
    everything into a single lock queue per route.
    """

    __slots__ = (
        "limit",
        "remaining",
        "outgoing",
        "reset_after",
        "expires",
        "dirty",
        "_last_request",
        "_max_ratelimit_timeout",
        "_loop",
        "_pending_requests",
        "_sleeping",
    )

    def __init__(self, max_ratelimit_timeout: Optional[float]) -> None:
        self.limit: int = 1
        self.remaining: int = self.limit
        self.outgoing: int = 0
        self.reset_after: float = 0.0
        self.expires: Optional[float] = None
        self.dirty: bool = False
        self._max_ratelimit_timeout: Optional[float] = max_ratelimit_timeout
        self._loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        self._pending_requests: deque[asyncio.Future[Any]] = deque()
        # Only a single rate limit object should be sleeping at a time.
        # The object that is sleeping is ultimately responsible for freeing the semaphore
        # for the requests currently pending.
        self._sleeping: asyncio.Lock = asyncio.Lock()
        self._last_request: float = self._loop.time()

    def __repr__(self) -> str:
        return (
            "<RateLimitBucket"
            f" limit={self.limit} remaining={self.remaining} pending_requests={len(self._pending_requests)}>"
        )

    def reset(self):
        self.remaining = self.limit - self.outgoing
        self.expires = None
        self.reset_after = 0.0
        self.dirty = False

    def update(
        self, response: aiohttp.ClientResponse, *, use_clock: bool = False
    ) -> None:
        headers = response.headers
        self.limit = int(headers.get("X-Ratelimit-Limit", 1))

        if self.dirty:
            self.remaining = min(
                int(headers.get("X-Ratelimit-Remaining", 0)), self.limit - self.outgoing
            )
        else:
            self.remaining = int(headers.get("X-Ratelimit-Remaining", 0))
            self.dirty = True

        reset_after = headers.get("X-Ratelimit-Reset-After")
        if use_clock or not reset_after:
            utc = datetime.timezone.utc
            now = datetime.datetime.now(utc)
            reset = datetime.datetime.fromtimestamp(
                float(headers["X-Ratelimit-Reset"]), utc
            )
            self.reset_after = (reset - now).total_seconds()
        else:
            self.reset_after = float(reset_after)

        self.expires = self._loop.time() + self.reset_after

    def _wake_next(self) -> None:
        while self._pending_requests:
            future = self._pending_requests.popleft()
            if not future.done():
                future.set_result(None)
                break

    def _wake(self, count: int = 1, *, exception: Optional[RateLimited] = None) -> None:
        awaken = 0
        while self._pending_requests:
            future = self._pending_requests.popleft()
            if not future.done():
                if exception:
                    future.set_exception(exception)
                else:
                    future.set_result(None)
                awaken += 1

            if awaken >= count:
                break

    async def _refresh(self) -> None:
        error = (
            self._max_ratelimit_timeout
            and self.reset_after > self._max_ratelimit_timeout
        )
        exception = RateLimited(self.reset_after) if error else None
        async with self._sleeping:
            if not error:
                await asyncio.sleep(self.reset_after)

        self.reset()
        self._wake(self.remaining, exception=exception)

    def is_expired(self) -> bool:
        return self.expires is not None and self._loop.time() > self.expires

    def is_inactive(self) -> bool:
        delta = self._loop.time() - self._last_request
        return delta >= 300 and self.outgoing == 0 and len(self._pending_requests) == 0

    async def acquire(self) -> None:
        self._last_request = self._loop.time()
        if self.is_expired():
            self.reset()

        if self._max_ratelimit_timeout is not None and self.expires is not None:
            # Check if we can pre-emptively block this request for having too large of a timeout
            current_reset_after = self.expires - self._loop.time()
            if current_reset_after > self._max_ratelimit_timeout:
                raise RateLimited(current_reset_after)

        while self.remaining <= 0:
            future = self._loop.create_future()
            self._pending_requests.append(future)
            try:
                await future
            except:
                future.cancel()
                if self.remaining > 0 and not future.cancelled():
                    self._wake_next()
                raise

        self.remaining -= 1
        self.outgoing += 1

    async def __aenter__(self) -> Self:
        await self.acquire()
        return self

    async def __aexit__(
        self, type: Type[BE], value: BE, traceback: TracebackType
    ) -> None:
        self.outgoing -= 1
        tokens = self.remaining - self.outgoing
        # Check whether the rate limit needs to be pre-emptively slept on
        # Note that this is a Lock to prevent multiple rate limit objects from sleeping at once
        if not self._sleeping.locked():
            if tokens <= 0:
                await self._refresh()
            elif self._pending_requests:
                exception = (
                    RateLimited(self.reset_after)
                    if self._max_ratelimit_timeout
                    and self.reset_after > self._max_ratelimit_timeout
                    else None
                )
                self._wake(tokens, exception=exception)


# For some reason, the Discord voice websocket expects this header to be
# completely lowercase while aiohttp respects spec and does it as case-insensitive
aiohttp.hdrs.WEBSOCKET = "websocket"  # type: ignore
try:
    # Support brotli if installed
    aiohttp.client_reqrep.ClientRequest.DEFAULT_HEADERS[aiohttp.hdrs.ACCEPT_ENCODING] = _gen_accept_encoding_header()  # type: ignore
except Exception:
    # aiohttp does it for us on newer versions anyway
    pass


class _FakeResponse:
    def __init__(self, reason: str, status: int) -> None:
        self.reason = reason
        self.status = status


class HTTPClient:
    """Represents an HTTP client sending HTTP requests to the Discord API."""

    def __init__(
        self,
        connector: Optional[aiohttp.BaseConnector] = None,
        *,
        proxy: Optional[str] = None,
        proxy_auth: Optional[aiohttp.BasicAuth] = None,
        unsync_clock: bool = True,
        http_trace: Optional[aiohttp.TraceConfig] = None,
        captcha: Optional[Callable[[CaptchaRequired], Coroutine[Any, Any, str]]] = None,
        max_ratelimit_timeout: Optional[float] = None,
        locale: Callable[[], str] = lambda: "en-US",
    ) -> None:
        self.connector: aiohttp.BaseConnector = connector or MISSING
        self.__session: aiohttp.ClientSession = MISSING
        # Route key -> Bucket hash
        self._bucket_hashes: Dict[str, str] = {}
        # Bucket Hash + Major Parameters -> Rate limit
        # or
        # Route key + Major Parameters -> Rate limit
        # When the key is the latter, it is used for temporary
        # one shot requests that don't have a bucket hash
        # When this reaches 256 elements, it will try to evict based off of expiry
        self._buckets: Dict[str, Ratelimit] = {}
        self._global_over: asyncio.Event = MISSING
        self.token: Optional[str] = None
        self.ack_token: Optional[str] = None
        self.proxy: Optional[str] = proxy
        self.proxy_auth: Optional[aiohttp.BasicAuth] = proxy_auth
        self.http_trace: Optional[aiohttp.TraceConfig] = http_trace
        self.use_clock: bool = not unsync_clock
        self.captcha_handler: Optional[
            Callable[[CaptchaRequired], Coroutine[Any, Any, str]]
        ] = captcha
        self.max_ratelimit_timeout: Optional[float] = (
            max(30.0, max_ratelimit_timeout) if max_ratelimit_timeout else None
        )
        self.get_locale: Callable[[], str] = locale

        self.super_properties: Dict[str, Any] = {}
        self.encoded_super_properties: str = MISSING
        self._started: bool = False

    def __del__(self) -> None:
        session = self.__session
        if session:
            try:
                session.connector._close()  # type: ignore # Handled below
            except AttributeError:
                pass

    def clear(self) -> None:
        if self.__session and self.__session.closed:
            self.__session = MISSING

    async def startup(self) -> None:
        if self._started:
            return

        self._global_over = asyncio.Event()
        self._global_over.set()

        if self.connector is MISSING or self.connector.closed:
            self.connector = aiohttp.TCPConnector(limit=0)
        self.__session = session = await _gen_session(
            aiohttp.ClientSession(
                connector=self.connector,
                trace_configs=None if self.http_trace is None else [self.http_trace],
            )
        )
        self.super_properties, self.encoded_super_properties = sp, _ = (
            await utils._get_info(session)
        )
        _log.info(
            "Found user agent %s, build number %s.",
            sp.get("browser_user_agent"),
            sp.get("client_build_number"),
        )

        self._started = True

    async def ws_connect(
        self, url: str, *, compress: int = 0
    ) -> aiohttp.ClientWebSocketResponse:
        kwargs: Dict[str, Any] = {
            "proxy_auth": self.proxy_auth,
            "proxy": self.proxy,
            "max_msg_size": 0,
            "timeout": 30.0,
            "autoclose": False,
            "headers": {
                "Accept-Language": "en-US",
                "Cache-Control": "no-cache",
                "Connection": "Upgrade",
                "Origin": "https://discord.com",
                "Pragma": "no-cache",
                "Sec-WebSocket-Extensions": (
                    "permessage-deflate; client_max_window_bits"
                ),
                "User-Agent": self.user_agent,
            },
            "compress": compress,
        }

        return await self.__session.ws_connect(url, **kwargs)

    @property
    def browser_version(self) -> str:
        return self.super_properties["browser_version"]

    @property
    def user_agent(self) -> str:
        return self.super_properties["browser_user_agent"]

    def _try_clear_expired_ratelimits(self) -> None:
        if len(self._buckets) < 256:
            return

        keys = [key for key, bucket in self._buckets.items() if bucket.is_inactive()]
        for key in keys:
            del self._buckets[key]

    def get_ratelimit(self, key: str) -> Ratelimit:
        try:
            value = self._buckets[key]
        except KeyError:
            self._buckets[key] = value = Ratelimit(self.max_ratelimit_timeout)
            self._try_clear_expired_ratelimits()
        return value

    async def request(
        self,
        route: Route,
        *,
        files: Optional[Sequence[File]] = None,
        form: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Any:
        method = route.method
        url = route.url
        captcha_handler = self.captcha_handler
        route_key = route.key

        if not self._started:
            await self.startup()

        bucket_hash = None
        try:
            bucket_hash = self._bucket_hashes[route_key]
        except KeyError:
            key = f"{route_key}:{route.major_parameters}"
        else:
            key = f"{bucket_hash}:{route.major_parameters}"

        ratelimit = self.get_ratelimit(key)

        # Header creation
        headers = {
            "Accept-Language": "en-US",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Origin": "https://discord.com",
            "Pragma": "no-cache",
            "Referer": "https://discord.com/channels/@me",
            "Sec-CH-UA": (
                '"Google Chrome";v="{0}", "Chromium";v="{0}", ";Not-A.Brand";v="24"'
                .format(self.browser_version.split(".")[0])
            ),
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": self.user_agent,
            "X-Discord-Locale": self.get_locale(),
            "X-Debug-Options": "bugReporterEnabled",
            "X-Super-Properties": self.encoded_super_properties,
        }

        # This header isn't really necessary
        # Timezones are annoying, so if it errors, we don't care
        try:
            from tzlocal import get_localzone_name

            timezone = get_localzone_name()
        except Exception:
            pass
        else:
            if timezone:
                headers["X-Discord-Timezone"] = timezone

        if self.token is not None and kwargs.get("auth", True):
            headers["Authorization"] = self.token

        reason = kwargs.pop("reason", None)
        if reason:
            headers["X-Audit-Log-Reason"] = _uriquote(reason)

        payload = kwargs.pop("json", None)
        if payload is not None:
            headers["Content-Type"] = "application/json"
            kwargs["data"] = utils._to_json(payload)

        if kwargs.pop("super_properties_to_track", False):
            headers["X-Track"] = headers.pop("X-Super-Properties")

        kwargs["headers"] = headers

        # Proxy support
        if self.proxy is not None:
            kwargs["proxy"] = self.proxy
        if self.proxy_auth is not None:
            kwargs["proxy_auth"] = self.proxy_auth

        if not self._global_over.is_set():
            await self._global_over.wait()

        response: Optional[aiohttp.ClientResponse] = None
        data: Optional[Union[Dict[str, Any], str]] = None
        failed = 0  # Number of 500'd requests
        async with ratelimit:
            for tries in range(5):
                if files:
                    for f in files:
                        f.reset(seek=tries)

                if form:
                    # With quote_fields=True '[' and ']' in file field names are escaped, which Discord does not support
                    form_data = aiohttp.FormData(quote_fields=False)
                    for params in form:
                        form_data.add_field(**params)
                    kwargs["data"] = form_data

                if failed:
                    headers["X-Failed-Requests"] = str(failed)

                try:
                    async with self.__session.request(
                        method, url, **kwargs
                    ) as response:
                        _log.debug(
                            "%s %s with %s has returned %s.",
                            method,
                            url,
                            kwargs.get("data"),
                            response.status,
                        )
                        data = await json_or_text(response)

                        # Update and use rate limit information if the bucket header is present
                        discord_hash = response.headers.get("X-Ratelimit-Bucket")
                        # I am unsure if X-Ratelimit-Bucket is always available
                        # However, X-Ratelimit-Remaining has been a consistent cornerstone that worked
                        has_ratelimit_headers = (
                            "X-Ratelimit-Remaining" in response.headers
                        )
                        if discord_hash is not None:
                            # If the hash Discord has provided is somehow different from our current hash something changed
                            if bucket_hash != discord_hash:
                                if bucket_hash is not None:
                                    # If the previous hash was an actual Discord hash then this means the
                                    # hash has changed sporadically.
                                    # This can be due to two reasons
                                    # 1. It's a sub-ratelimit which is hard to handle
                                    # 2. The rate limit information genuinely changed
                                    # There is no good way to discern these, Discord doesn't provide a way to do so.
                                    # At best, there will be some form of logging to help catch it.
                                    # Alternating sub-ratelimits means that the requests oscillate between
                                    # different underlying rate limits -- this can lead to unexpected 429s
                                    # It is unavoidable.
                                    fmt = "A route (%s) has changed hashes: %s -> %s."
                                    _log.debug(
                                        fmt, route_key, bucket_hash, discord_hash
                                    )

                                    self._bucket_hashes[route_key] = discord_hash
                                    recalculated_key = (
                                        discord_hash + route.major_parameters
                                    )
                                    self._buckets[recalculated_key] = ratelimit
                                    self._buckets.pop(key, None)
                                elif route_key not in self._bucket_hashes:
                                    fmt = (
                                        "%s has found its initial rate limit bucket"
                                        " hash (%s)."
                                    )
                                    _log.debug(fmt, route_key, discord_hash)
                                    self._bucket_hashes[route_key] = discord_hash
                                    self._buckets[
                                        discord_hash + route.major_parameters
                                    ] = ratelimit

                        if has_ratelimit_headers:
                            if response.status != 429:
                                ratelimit.update(response, use_clock=self.use_clock)
                                if ratelimit.remaining == 0:
                                    _log.debug(
                                        "A rate limit bucket (%s) has been"
                                        " exhausted. Pre-emptively rate limiting...",
                                        discord_hash or route_key,
                                    )

                        # 202s must be retried
                        if (
                            response.status == 202
                            and isinstance(data, dict)
                            and data["code"] == 110000
                        ):
                            # We update the `attempts` query parameter
                            params = kwargs.get("params")
                            if not params:
                                kwargs["params"] = {"attempts": 1}
                            else:
                                params["attempts"] = (params.get("attempts") or 0) + 1

                            # Sometimes retry_after is 0, but that's undesirable
                            retry_after: float = data["retry_after"] or 5
                            _log.debug(
                                "%s %s received a 202. Retrying in %s seconds...",
                                method,
                                url,
                                retry_after,
                            )
                            await asyncio.sleep(retry_after)
                            continue

                        # Request was successful so just return the text/json
                        if 300 > response.status >= 200:
                            _log.debug("%s %s has received %s.", method, url, data)
                            return data

                        # Rate limited
                        if response.status == 429:
                            if not response.headers.get("Via") or isinstance(data, str):
                                # Banned by Cloudflare more than likely.
                                raise HTTPException(response, data)

                            if ratelimit.remaining > 0:
                                # According to night
                                # https://github.com/discord/discord-api-docs/issues/2190#issuecomment-816363129
                                # Remaining > 0 and 429 means that a sub ratelimit was hit.
                                # It is unclear what should happen in these cases other than just using the retry_after
                                # value in the body.
                                _log.debug(
                                    "%s %s received a 429 despite having %s"
                                    " remaining requests. This is a sub-ratelimit.",
                                    method,
                                    url,
                                    ratelimit.remaining,
                                )

                            retry_after: float = data["retry_after"]
                            if (
                                self.max_ratelimit_timeout
                                and retry_after > self.max_ratelimit_timeout
                            ):
                                _log.warning(
                                    "We are being rate limited. %s %s responded"
                                    " with 429. Timeout of %.2f was too long,"
                                    " erroring instead.",
                                    method,
                                    url,
                                    retry_after,
                                )
                                raise RateLimited(retry_after)

                            fmt = (
                                "We are being rate limited. %s %s responded with 429."
                                " Retrying in %.2f seconds."
                            )
                            _log.warning(fmt, method, url, retry_after)

                            _log.debug(
                                "Rate limit is being handled by bucket hash %s with"
                                " %r major parameters.",
                                bucket_hash,
                                route.major_parameters,
                            )

                            # Check if it's a global rate limit
                            is_global = data.get("global", False)
                            if is_global:
                                _log.warning(
                                    "Global rate limit has been hit. Retrying in"
                                    " %.2f seconds.",
                                    retry_after,
                                )
                                self._global_over.clear()

                            await asyncio.sleep(retry_after)
                            _log.debug("Done sleeping for the rate limit. Retrying...")

                            # Release the global lock now that the rate limit passed
                            if is_global:
                                self._global_over.set()
                                _log.debug("Global rate limit is now over.")

                            continue

                        # Unconditional retry
                        if response.status in {500, 502, 504, 507, 522, 523, 524}:
                            failed += 1
                            await asyncio.sleep(1 + tries * 2)
                            continue

                        # Usual error cases
                        if response.status == 403:
                            raise Forbidden(response, data)
                        elif response.status == 404:
                            raise NotFound(response, data)
                        elif response.status >= 500:
                            raise DiscordServerError(response, data)
                        else:
                            if isinstance(data, dict) and "captcha_key" in data:
                                raise CaptchaRequired(response, data)  # type: ignore
                            raise HTTPException(response, data)

                # This is handling exceptions from the request
                except OSError as e:
                    # Connection reset by peer
                    if tries < 4 and e.errno in (54, 10054):
                        failed += 1
                        await asyncio.sleep(1 + tries * 2)
                        continue
                    raise

                # Captcha handling
                except CaptchaRequired as e:
                    # The way captcha handling works is completely transparent
                    # The user is expected to provide a handler that will be called to return a solution
                    # Then, we just insert the solution + rqtoken (if applicable) into the headers and retry the request
                    if captcha_handler is None or tries == 4:
                        raise
                    else:
                        headers["X-Captcha-Key"] = await captcha_handler(e)
                        if e.rqtoken:
                            headers["X-Captcha-Rqtoken"] = e.rqtoken

            if response is not None:
                # We've run out of retries, raise
                if response.status >= 500:
                    raise DiscordServerError(response, data)

                raise HTTPException(response, data)

            raise RuntimeError("Unreachable code in HTTP handling")

    async def get_from_cdn(self, url: str) -> bytes:
        async with self.__session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()
            elif resp.status == 404:
                raise NotFound(resp, "asset not found")
            elif resp.status == 403:
                raise Forbidden(resp, "cannot retrieve asset")
            else:
                raise HTTPException(resp, "failed to get asset")

        raise RuntimeError("Unreachable code in HTTP handling")

    async def upload_to_cloud(
        self, url: str, file: Union[File, str], hash: Optional[str] = None
    ) -> Any:
        response: Optional[aiohttp.ClientResponse] = None
        data: Optional[Union[Dict[str, Any], str]] = None

        # aiohttp helpfully sets the content type for us,
        # but Google explodes if we do that; therefore, empty string
        headers = {"Content-Type": ""}
        if hash:
            headers["Content-MD5"] = hash

        for tries in range(5):
            if isinstance(file, File):
                file.reset(seek=tries)

            try:
                async with self.__session.put(
                    url, data=getattr(file, "fp", file), headers=headers
                ) as response:
                    _log.debug(
                        "PUT %s with %s has returned %s.", url, file, response.status
                    )
                    data = await json_or_text(response)

                    # Request was successful so just return the text/json
                    if 300 > response.status >= 200:
                        _log.debug("PUT %s has received %s.", url, data)
                        return data

                    # Unconditional retry
                    if response.status in {500, 502, 504}:
                        await asyncio.sleep(1 + tries * 2)
                        continue

                    # Usual error cases
                    if response.status == 403:
                        raise Forbidden(response, data)
                    elif response.status == 404:
                        raise NotFound(response, data)
                    elif response.status >= 500:
                        raise DiscordServerError(response, data)
                    else:
                        raise HTTPException(response, data)
            except OSError as e:
                # Connection reset by peer
                if tries < 4 and e.errno in (54, 10054):
                    await asyncio.sleep(1 + tries * 2)
                    continue
                raise

        if response is not None:
            # We've run out of retries, raise
            if response.status >= 500:
                raise DiscordServerError(response, data)

            raise HTTPException(response, data)

    async def get_preferred_voice_regions(self) -> List[dict]:
        async with self.__session.get("https://latency.discord.media/rtc") as resp:
            if resp.status == 200:
                return await resp.json()
            elif resp.status == 404:
                raise NotFound(resp, "rtc regions not found")
            elif resp.status == 403:
                raise Forbidden(resp, "cannot retrieve rtc regions")
            else:
                raise HTTPException(resp, "failed to get rtc regions")

    # State management

    async def close(self) -> None:
        if self.__session:
            await self.__session.close()

    # Login management

    def _token(self, token: str) -> None:
        self.token = token
        self.ack_token = None

    async def static_login(self, token: str) -> user.User:
        old_token, self.token = self.token, token

        try:
            data = await self.get_me()
        except HTTPException as exc:
            self.token = old_token
            if exc.status == 401:
                raise LoginFailure("Improper token has been passed") from exc
            raise

        return data

    # Self user

    def get_me(self, with_analytics_token: bool = True) -> Response[user.User]:
        params = {"with_analytics_token": str(with_analytics_token).lower()}
        return self.request(Route("GET", "/users/@me"), params=params)

    # PM functionality

    def start_private_message(self, user_id: Snowflake) -> Response[channel.DMChannel]:
        payload = {
            "recipients": [user_id],
        }
        return self.request(Route("POST", "/users/@me/channels"), json=payload)

    # Message management

    async def ack_message(
        self,
        channel_id: Snowflake,
        message_id: Snowflake,
        *,
        manual: bool = False,
        mention_count: Optional[int] = None,
        flags: Optional[int] = None,
        last_viewed: Optional[int] = None,
    ) -> None:
        payload = {}
        if manual:
            payload["manual"] = True
        else:
            payload["token"] = self.ack_token
        if mention_count is not None:
            payload["mention_count"] = mention_count
        if flags is not None:
            payload["flags"] = flags
        if last_viewed is not None:
            payload["last_viewed"] = last_viewed

        data: read_state.AcknowledgementToken = await self.request(
            Route(
                "POST",
                "/channels/{channel_id}/messages/{message_id}/ack",
                channel_id=channel_id,
                message_id=message_id,
            ),
            json=payload,
        )
        self.ack_token = data.get("token") if data else None

    def ack_guild(self, guild_id: Snowflake) -> Response[None]:
        return self.request(Route("POST", "/guilds/{guild_id}/ack", guild_id=guild_id))

    def delete_read_state(self, channel_id: Snowflake, type: int) -> Response[None]:
        payload = {
            "version": 2,
            "read_state_type": type,
        }  # Read state protocol version 2
        return self.request(
            Route(
                "DELETE", "/channels/{channel_id}/messages/ack", channel_id=channel_id
            ),
            json=payload,
        )

    async def get_message(
        self, channel_id: Snowflake, message_id: Snowflake
    ) -> message.Message:
        data = await self.logs_from(channel_id, 1, around=message_id)
        if not data or int(data[0]["id"]) != message_id:
            raise NotFound(_FakeResponse("Not Found", 404), {"code": 10008, "message": "Unknown Message"})  # type: ignore # Faked response

        return data[0]

    def get_channel(self, channel_id: Snowflake) -> Response[channel.Channel]:
        return self.request(
            Route("GET", "/channels/{channel_id}", channel_id=channel_id)
        )

    def logs_from(
        self,
        channel_id: Snowflake,
        limit: int,
        before: Optional[Snowflake] = None,
        after: Optional[Snowflake] = None,
        around: Optional[Snowflake] = None,
    ) -> Response[List[message.Message]]:
        params: Dict[str, Any] = {
            "limit": limit,
        }
        if before is not None:
            params["before"] = before
        if after is not None:
            params["after"] = after
        if around is not None:
            params["around"] = around

        return self.request(
            Route("GET", "/channels/{channel_id}/messages", channel_id=channel_id),
            params=params,
        )

    def publish_message(
        self, channel_id: Snowflake, message_id: Snowflake
    ) -> Response[message.Message]:
        return self.request(
            Route(
                "POST",
                "/channels/{channel_id}/messages/{message_id}/crosspost",
                channel_id=channel_id,
                message_id=message_id,
            )
        )

    # Member management

    def get_guild_applications(
        self,
        guild_id: Snowflake,
        *,
        type: Optional[int] = None,
        include_team: bool = False,
        channel_id: Optional[Snowflake] = None,
    ) -> Response[List[application.PartialApplication]]:
        params = {}
        if type is not None:
            params["type"] = type
        if include_team:
            params["include_team"] = "true"
        if channel_id is not None:
            params["channel_id"] = channel_id

        return self.request(
            Route("GET", "/guilds/{guild_id}/applications", guild_id=guild_id),
            params=params,
        )

    # OAuth2

    def get_oauth2_tokens(self) -> Response[List[oauth2.OAuth2Token]]:
        return self.request(Route("GET", "/oauth2/tokens"))

    def revoke_oauth2_token(self, token_id: Snowflake) -> Response[None]:
        return self.request(
            Route("DELETE", "/oauth2/tokens/{token_id}", token_id=token_id)
        )

    def get_guild_webhook_channels(
        self, guild_id: Snowflake
    ) -> Response[List[oauth2.WebhookChannel]]:
        params = {"guild_id": guild_id}
        return self.request(
            Route("GET", "/oauth2/authorize/webhook-channels"), params=params
        )

    def get_oauth2_authorization(
        self,
        application_id: Snowflake,
        scopes: List[str],
        response_type: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
        code_challenge: Optional[str] = None,
        state: Optional[str] = None,
    ) -> Response[oauth2.OAuth2Authorization]:
        params = {"client_id": application_id, "scope": " ".join(scopes)}
        if response_type:
            params["response_type"] = response_type
        if redirect_uri:
            params["redirect_uri"] = redirect_uri
        if code_challenge_method:
            params["code_challenge_method"] = code_challenge_method
        if code_challenge:
            params["code_challenge"] = code_challenge
        if state:
            params["state"] = state

        return self.request(Route("GET", "/oauth2/authorize"), params=params)

    def authorize_oauth2(
        self,
        application_id: Snowflake,
        scopes: List[str],
        response_type: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
        code_challenge: Optional[str] = None,
        state: Optional[str] = None,
        guild_id: Optional[Snowflake] = None,
        webhook_channel_id: Optional[Snowflake] = None,
        permissions: Optional[Snowflake] = None,
    ) -> Response[oauth2.OAuth2Location]:
        params = {"client_id": application_id, "scope": " ".join(scopes)}
        payload: Dict[str, Any] = {"authorize": True}
        if response_type:
            params["response_type"] = response_type
        if redirect_uri:
            params["redirect_uri"] = redirect_uri
        if code_challenge_method:
            params["code_challenge_method"] = code_challenge_method
        if code_challenge:
            params["code_challenge"] = code_challenge
        if state:
            params["state"] = state
        if guild_id:
            payload["guild_id"] = str(guild_id)
            payload["permissions"] = "0"
        if webhook_channel_id:
            payload["webhook_channel_id"] = str(webhook_channel_id)
        if permissions:
            payload["permissions"] = str(permissions)

        return self.request(
            Route("POST", "/oauth2/authorize"), params=params, json=payload
        )

    # Misc

    async def get_gateway(self, *, encoding: str = "json", zlib: bool = True) -> str:
        try:
            data = await self.request(Route("GET", "/gateway"))
        except HTTPException as exc:
            raise GatewayNotFound() from exc
        if zlib:
            value = "{0}?encoding={1}&v={2}&compress=zlib-stream"
        else:
            value = "{0}?encoding={1}&v={2}"
        return value.format(data["url"], encoding, INTERNAL_API_VERSION)

    def get_user(self, user_id: Snowflake) -> Response[user.APIUser]:
        return self.request(Route("GET", "/users/{user_id}", user_id=user_id))

    def get_proto_settings(self, type: int) -> Response[user.ProtoSettings]:
        return self.request(Route("GET", "/users/@me/settings-proto/{type}", type=type))

    def edit_proto_settings(
        self, type: int, settings: str, required_data_version: Optional[int] = None
    ) -> Response[user.ProtoSettings]:
        payload: Dict[str, Snowflake] = {"settings": settings}
        if required_data_version is not None:
            # The required data version of the proto is set to the last known version when an offline edit is made
            # so the PATCH doesn't overwrite newer edits made on a different client
            payload["required_data_version"] = required_data_version

        return self.request(
            Route("PATCH", "/users/@me/settings-proto/{type}", type=type), json=payload
        )

    def get_settings(self):
        return self.request(Route("GET", "/users/@me/settings"))

    def edit_settings(self, **payload):
        return self.request(Route("PATCH", "/users/@me/settings"), json=payload)

    def get_application_commands(
        self, app_id: Snowflake
    ) -> Response[List[command.ApplicationCommand]]:
        return self.request(
            Route(
                "GET", "/applications/{application_id}/commands", application_id=app_id
            )
        )

    def search_application_commands(
        self,
        channel_id: Snowflake,
        type: int,
        *,
        limit: Optional[int] = None,
        query: Optional[str] = None,
        cursor: Optional[str] = None,
        command_ids: Optional[List[Snowflake]] = None,
        application_id: Optional[Snowflake] = None,
        include_applications: Optional[bool] = None,
    ) -> Response[command.ApplicationCommandSearch]:
        params: Dict[str, Any] = {
            "type": type,
        }
        if include_applications is not None:
            params["include_applications"] = str(include_applications).lower()
        if limit is not None:
            params["limit"] = limit
        if query:
            params["query"] = query
        if cursor:
            params["cursor"] = cursor
        if command_ids:
            params["command_ids"] = ",".join(map(str, command_ids))
        if application_id:
            params["application_id"] = application_id

        return self.request(
            Route(
                "GET",
                "/channels/{channel_id}/application-commands/search",
                channel_id=channel_id,
            ),
            params=params,
        )

    def interact(
        self,
        type: InteractionType,
        data: interactions.InteractionData,
        channel: MessageableChannel,
        message: Optional[Message] = None,
        *,
        nonce: Optional[str] = MISSING,
        application_id: Snowflake = MISSING,
        files: Optional[List[_FileBase]] = None,
    ) -> Response[None]:
        state = getattr(message, "_state", channel._state)
        payload = {
            "application_id": str(
                (message.application_id) if message else application_id
            ),
            "channel_id": str(channel.id),
            "data": data,
            "nonce": nonce if nonce is not MISSING else utils._generate_nonce(),
            "session_id": state.session_id or utils._generate_session_id(),
            "type": type.value,
        }
        if message is not None:
            payload["message_flags"] = message.flags.value
            payload["message_id"] = str(message.id)
            if message.guild:
                payload["guild_id"] = str(message.guild.id)
        else:
            guild = getattr(channel, "guild", None)
            if guild is not None:
                payload["guild_id"] = str(guild.id)

        form = []
        to_upload = [file for file in files if isinstance(file, File)] if files else []
        if files is not None:
            form.append({"name": "payload_json", "value": utils._to_json(payload)})

            # Legacy uploading
            for index, file in enumerate(to_upload or []):
                form.append(
                    {
                        "name": f"files[{index}]",
                        "value": file.fp,
                        "filename": file.filename,
                        "content_type": "application/octet-stream",
                    }
                )
            payload = None

        return self.request(
            Route("POST", "/interactions"), json=payload, form=form, files=to_upload
        )
