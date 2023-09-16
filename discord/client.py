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
import logging
from typing import (
    Any,
    Awaitable,
    Callable,
    Collection,
    Coroutine,
    Dict,
    Generator,
    List,
    Optional,
    Sequence,
    TYPE_CHECKING,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import aiohttp

from . import utils
from .backoff import ExponentialBackoff
from .channel import (
    PartialMessageable,
    _channel_factory,
)
from .enums import (
    ActivityType,
    ChannelType,
    Status,
)
from .errors import *
from .gateway import *
from .gateway import ConnectionClosed
from .guild import UserGuild
from .http import HTTPClient
from .oauth2 import OAuth2Authorization, OAuth2Token
from .settings import UserSettings
from .state import ConnectionState
from .user import User, ClientUser
from .utils import MISSING

if TYPE_CHECKING:
    from typing_extensions import Self
    from types import TracebackType
    from .guild import GuildChannel
    from .abc import Snowflake
    from .channel import DMChannel
    from .message import Message
    from .read_state import ReadState
    from .guild import Guild

    PrivateChannel = Union[DMChannel]

# fmt: off
__all__ = (
    'Client',
)
# fmt: on

Coro = TypeVar("Coro", bound=Callable[..., Coroutine[Any, Any, Any]])

_log = logging.getLogger(__name__)


class _LoopSentinel:
    __slots__ = ()

    def __getattr__(self, attr: str) -> None:
        msg = (
            "loop attribute cannot be accessed in non-async contexts. Consider using"
            " either an asynchronous main function and passing it to asyncio.run or"
            " using asynchronous initialisation hooks such as Client.setup_hook"
        )
        raise AttributeError(msg)


_loop: Any = _LoopSentinel()


class Client:
    r"""Represents a client connection that connects to Discord.
    This class is used to interact with the Discord WebSocket and API.

    .. container:: operations

        .. describe:: async with x

            Asynchronously initialises the client and automatically cleans up.

            .. versionadded:: 2.0

    A number of options can be passed to the :class:`Client`.

    Parameters
    -----------
    max_messages: Optional[:class:`int`]
        The maximum number of messages to store in the internal message cache.
        This defaults to ``1000``. Passing in ``None`` disables the message cache.

        .. versionchanged:: 1.3
            Allow disabling the message cache and change the default size to ``1000``.
    proxy: Optional[:class:`str`]
        Proxy URL.
    proxy_auth: Optional[:class:`aiohttp.BasicAuth`]
        An object that represents proxy HTTP Basic Authorization.
    member_cache_flags: :class:`MemberCacheFlags`
        Allows for finer control over how the library caches members.
        If not given, defaults to cache as much as possible.

        .. versionadded:: 1.5
    chunk_guilds_at_startup: :class:`bool`
        Indicates if :func:`.on_ready` should be delayed to chunk all guilds
        at start-up if necessary. This operation is incredibly slow for large
        amounts of guilds. The default is ``True``.

        .. versionadded:: 1.5
    request_guilds: :class:`bool`
        Whether to request guilds at startup. Defaults to True.

        .. versionadded:: 2.0
    status: Optional[:class:`.Status`]
        A status to start your presence with upon logging on to Discord.
    activity: Optional[:class:`.BaseActivity`]
        An activity to start your presence with upon logging on to Discord.
    allowed_mentions: Optional[:class:`AllowedMentions`]
        Control how the client handles mentions by default on every message sent.

        .. versionadded:: 1.4
    heartbeat_timeout: :class:`float`
        The maximum numbers of seconds before timing out and restarting the
        WebSocket in the case of not receiving a HEARTBEAT_ACK. Useful if
        processing the initial packets take too long to the point of disconnecting
        you. The default timeout is 60 seconds.
    assume_unsync_clock: :class:`bool`
        Whether to assume the system clock is unsynced. This applies to the ratelimit handling
        code. If this is set to ``True``, the default, then the library uses the time to reset
        a rate limit bucket given by Discord. If this is ``False`` then your system clock is
        used to calculate how long to sleep for. If this is set to ``False`` it is recommended to
        sync your system clock to Google's NTP server.

        .. versionadded:: 1.3
    enable_debug_events: :class:`bool`
        Whether to enable events that are useful only for debugging gateway related information.

        Right now this involves :func:`on_socket_raw_receive` and :func:`on_socket_raw_send`. If
        this is ``False`` then those events will not be dispatched (due to performance considerations).
        To enable these events, this must be set to ``True``. Defaults to ``False``.

        .. versionadded:: 2.0
    sync_presence: :class:`bool`
        Whether to keep presences up-to-date across clients.
        The default behavior is ``True`` (what the client does).

        .. versionadded:: 2.0
    http_trace: :class:`aiohttp.TraceConfig`
        The trace configuration to use for tracking HTTP requests the library does using ``aiohttp``.
        This allows you to check requests the library is using. For more information, check the
        `aiohttp documentation <https://docs.aiohttp.org/en/stable/client_advanced.html#client-tracing>`_.

        .. versionadded:: 2.0
    captcha_handler: Optional[Callable[[:class:`.CaptchaRequired`, :class:`.Client`], Awaitable[:class:`str`]]
        A function that solves captcha challenges.

        .. versionadded:: 2.0

        .. versionchanged:: 2.1

            Now accepts a coroutine instead of a ``CaptchaHandler``.
    max_ratelimit_timeout: Optional[:class:`float`]
        The maximum number of seconds to wait when a non-global rate limit is encountered.
        If a request requires sleeping for more than the seconds passed in, then
        :exc:`~discord.RateLimited` will be raised. By default, there is no timeout limit.
        In order to prevent misuse and unnecessary bans, the minimum value this can be
        set to is ``30.0`` seconds.

        .. versionadded:: 2.0

    Attributes
    -----------
    ws
        The websocket gateway the client is currently connected to. Could be ``None``.
    """

    def __init__(self, **options: Any) -> None:
        self.loop: asyncio.AbstractEventLoop = _loop
        # self.ws is set in the connect method
        self.ws: DiscordWebSocket = None  # type: ignore
        self._listeners: Dict[str, List[Tuple[asyncio.Future, Callable[..., bool]]]] = (
            {}
        )

        proxy: Optional[str] = options.pop("proxy", None)
        proxy_auth: Optional[aiohttp.BasicAuth] = options.pop("proxy_auth", None)
        unsync_clock: bool = options.pop("assume_unsync_clock", True)
        http_trace: Optional[aiohttp.TraceConfig] = options.pop("http_trace", None)
        max_ratelimit_timeout: Optional[float] = options.pop(
            "max_ratelimit_timeout", None
        )
        self.captcha_handler: Optional[
            Callable[[CaptchaRequired, Client], Awaitable[str]]
        ] = options.pop("captcha_handler", None)
        self.http: HTTPClient = HTTPClient(
            proxy=proxy,
            proxy_auth=proxy_auth,
            unsync_clock=unsync_clock,
            http_trace=http_trace,
            captcha=self.handle_captcha,
            max_ratelimit_timeout=max_ratelimit_timeout,
            locale=lambda: self._connection.locale,
        )

        self._handlers: Dict[str, Callable[..., None]] = {
            "ready": self._handle_ready,
            "connect": self._handle_connect,
        }

        self._hooks: Dict[str, Callable[..., Coroutine[Any, Any, Any]]] = {
            "before_identify": self._call_before_identify_hook,
        }

        self._enable_debug_events: bool = options.pop("enable_debug_events", False)
        self._sync_presences: bool = options.pop("sync_presence", True)
        self._connection: ConnectionState = self._get_state(**options)
        self._closed: bool = False
        self._ready: asyncio.Event = MISSING

    async def __aenter__(self) -> Self:
        await self._async_setup_hook()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if not self.is_closed():
            await self.close()

    # Internals

    def _get_state(self, **options: Any) -> ConnectionState:
        return ConnectionState(
            dispatch=self.dispatch,
            handlers=self._handlers,
            hooks=self._hooks,
            http=self.http,
            loop=self.loop,
            client=self,
            **options,
        )

    def _handle_ready(self) -> None:
        self._ready.set()

    def _handle_connect(self) -> None:
        activities = None
        status = self.initial_status
        if status or activities:
            if status is None:
                state = self._connection
                status = getattr(state.settings, "status", None) or Status.unknown
            self.loop.create_task(
                self.change_presence(activities=activities, status=status)
            )

    @property
    def latency(self) -> float:
        """:class:`float`: Measures latency between a HEARTBEAT and a HEARTBEAT_ACK in seconds.

        This could be referred to as the Discord WebSocket protocol latency.
        """
        ws = self.ws
        return float("nan") if not ws else ws.latency

    def is_ws_ratelimited(self) -> bool:
        """:class:`bool`: Whether the websocket is currently rate limited.

        This can be useful to know when deciding whether you should query members
        using HTTP or via the gateway.

        .. versionadded:: 1.6
        """
        if self.ws:
            return self.ws.is_ratelimited()
        return False

    @property
    def user(self) -> Optional[ClientUser]:
        """Optional[:class:`.ClientUser`]: Represents the connected client. ``None`` if not logged in."""
        return self._connection.user

    @property
    def guilds(self) -> Sequence[Guild]:
        """Sequence[:class:`.Guild`]: The guilds that the connected client is a member of."""
        return self._connection.guilds

    @property
    def cached_messages(self) -> Sequence[Message]:
        """Sequence[:class:`.Message`]: Read-only list of messages the connected client has cached.

        .. versionadded:: 1.1
        """
        return utils.SequenceProxy(self._connection._messages or [])

    @property
    def private_channels(self) -> Sequence[PrivateChannel]:
        """Sequence[:class:`.abc.PrivateChannel`]: The private channels that the connected client is participating on."""
        return self._connection.private_channels

    @property
    def settings(self) -> Optional[UserSettings]:
        """Optional[:class:`.UserSettings`]: Returns the user's settings.

        .. versionadded:: 2.0
        """
        return self._connection.settings

    @property
    def read_states(self) -> List[ReadState]:
        """List[:class:`.ReadState`]: The read states that the connected client has.

        .. versionadded:: 2.1
        """
        return [
            read_state
            for group in self._connection._read_states.values()
            for read_state in group.values()
        ]

    @property
    def disclose(self) -> Sequence[str]:
        """Sequence[:class:`str`]: Upcoming changes to the user's account.

        .. versionadded:: 2.1
        """
        return utils.SequenceProxy(self._connection.disclose)

    def is_ready(self) -> bool:
        """:class:`bool`: Specifies if the client's internal cache is ready for use."""
        return self._ready is not MISSING and self._ready.is_set()

    async def _run_event(
        self,
        coro: Callable[..., Coroutine[Any, Any, Any]],
        event_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        try:
            await coro(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception:
            try:
                await self.on_error(event_name, *args, **kwargs)
            except asyncio.CancelledError:
                pass

    def _schedule_event(
        self,
        coro: Callable[..., Coroutine[Any, Any, Any]],
        event_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> asyncio.Task:
        wrapped = self._run_event(coro, event_name, *args, **kwargs)
        # Schedules the task
        return self.loop.create_task(wrapped, name=f"discord.py: {event_name}")

    def dispatch(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        _log.debug("Dispatching event %s.", event)
        method = "on_" + event

        listeners = self._listeners.get(event)
        if listeners:
            removed = []
            for i, (future, condition) in enumerate(listeners):
                if future.cancelled():
                    removed.append(i)
                    continue

                try:
                    result = condition(*args)
                except Exception as exc:
                    future.set_exception(exc)
                    removed.append(i)
                else:
                    if result:
                        if len(args) == 0:
                            future.set_result(None)
                        elif len(args) == 1:
                            future.set_result(args[0])
                        else:
                            future.set_result(args)
                        removed.append(i)

            if len(removed) == len(listeners):
                self._listeners.pop(event)
            else:
                for idx in reversed(removed):
                    del listeners[idx]

        try:
            coro = getattr(self, method)
        except AttributeError:
            pass
        else:
            self._schedule_event(coro, method, *args, **kwargs)

    async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:
        """|coro|

        The default error handler provided by the client.

        By default this logs to the library logger however it could be
        overridden to have a different implementation.
        Check :func:`~discord.on_error` for more details.

        .. versionchanged:: 2.0

            ``event_method`` parameter is now positional-only
            and instead of writing to ``sys.stderr`` it logs instead.
        """
        _log.exception("Ignoring exception in %s", event_method)

    # Hooks

    async def _call_before_identify_hook(self, *, initial: bool = False) -> None:
        # This hook is an internal hook that actually calls the public one
        # It allows the library to have its own hook without stepping on the
        # toes of those who need to override their own hook
        await self.before_identify_hook(initial=initial)

    async def before_identify_hook(self, *, initial: bool = False) -> None:
        """|coro|

        A hook that is called before IDENTIFYing a session. This is useful
        if you wish to have more control over the synchronization of multiple
        IDENTIFYing clients.

        The default implementation does nothing.

        .. versionadded:: 1.4

        Parameters
        ------------
        initial: :class:`bool`
            Whether this IDENTIFY is the first initial IDENTIFY.
        """
        pass

    async def handle_captcha(self, exception: CaptchaRequired, /) -> str:
        """|coro|

        Handles a CAPTCHA challenge and returns a solution.

        The default implementation tries to use the CAPTCHA handler
        passed in the constructor.

        .. versionadded:: 2.1

        Parameters
        ------------
        exception: :class:`.CaptchaRequired`
            The exception that was raised.

        Raises
        --------
        CaptchaRequired
            The CAPTCHA challenge could not be solved.

        Returns
        --------
        :class:`str`
            The solution to the CAPTCHA challenge.
        """
        handler = self.captcha_handler
        if handler is None:
            raise exception
        return await handler(exception, self)

    async def _async_setup_hook(self) -> None:
        # Called whenever the client needs to initialise asyncio objects with a running loop
        loop = asyncio.get_running_loop()
        self.loop = loop
        self._connection.loop = loop
        await self._connection.async_setup()

        self._ready = asyncio.Event()

    async def setup_hook(self) -> None:
        """|coro|

        A coroutine to be called to setup the client, by default this is blank.

        To perform asynchronous setup after the user is logged in but before
        it has connected to the Websocket, overwrite this coroutine.

        This is only called once, in :meth:`login`, and will be called before
        any events are dispatched, making it a better solution than doing such
        setup in the :func:`~discord.on_ready` event.

        .. warning::

            Since this is called *before* the websocket connection is made therefore
            anything that waits for the websocket will deadlock, this includes things
            like :meth:`wait_for` and :meth:`wait_until_ready`.

        .. versionadded:: 2.0
        """
        pass

    # Login state management

    async def login(self, token: str) -> None:
        """|coro|

        Logs in the client with the specified credentials and
        calls the :meth:`setup_hook`.

        .. warning::

            Logging on with a user token is unfortunately against the Discord
            `Terms of Service <https://support.discord.com/hc/en-us/articles/115002192352>`_
            and doing so might potentially get your account banned.
            Use this at your own risk.

        Parameters
        -----------
        token: :class:`str`
            The authentication token.

        Raises
        ------
        LoginFailure
            The wrong credentials are passed.
        HTTPException
            An unknown HTTP related error occurred,
            usually when it isn't 200 or the known incorrect credentials
            passing status code.
        """

        _log.info("Logging in using static token.")

        if self.loop is _loop:
            await self._async_setup_hook()

        if not isinstance(token, str):
            raise TypeError(
                f"expected token to be a str, received {token.__class__!r} instead"
            )

        state = self._connection
        data = await state.http.static_login(token.strip())
        state.analytics_token = data.get("analytics_token", "")
        state.user = ClientUser(state=state, data=data)
        await self.setup_hook()

    async def connect(self, *, reconnect: bool = True) -> None:
        """|coro|

        Creates a websocket connection and lets the websocket listen
        to messages from Discord. This is a loop that runs the entire
        event system and miscellaneous aspects of the library. Control
        is not resumed until the WebSocket connection is terminated.

        Parameters
        -----------
        reconnect: :class:`bool`
            If we should attempt reconnecting, either due to internet
            failure or a specific failure on Discord's part. Certain
            disconnects that lead to bad state will not be handled
            (such as bad tokens).

        Raises
        -------
        GatewayNotFound
            If the gateway to connect to Discord is not found. Usually if this
            is thrown then there is a Discord API outage.
        ConnectionClosed
            The websocket connection has been terminated.
        """

        backoff = ExponentialBackoff()
        ws_params: Dict[str, Any] = {
            "initial": True,
        }
        while not self.is_closed():
            try:
                coro = DiscordWebSocket.from_client(self, **ws_params)
                self.ws = await asyncio.wait_for(coro, timeout=60.0)
                ws_params["initial"] = False
                while True:
                    await self.ws.poll_event()
            except ReconnectWebSocket as e:
                _log.debug("Got a request to %s the websocket.", e.op)
                self.dispatch("disconnect")
                ws_params.update(
                    sequence=self.ws.sequence,
                    resume=e.resume,
                    session=self.ws.session_id,
                )
                if e.resume:
                    ws_params["gateway"] = self.ws.gateway
                continue
            except (
                OSError,
                HTTPException,
                GatewayNotFound,
                ConnectionClosed,
                aiohttp.ClientError,
                asyncio.TimeoutError,
            ) as exc:
                self.dispatch("disconnect")
                if not reconnect:
                    await self.close()
                    if isinstance(exc, ConnectionClosed) and exc.code == 1000:
                        # Clean close, don't re-raise this
                        return
                    raise

                if self.is_closed():
                    return

                # If we get connection reset by peer then try to RESUME
                if isinstance(exc, OSError) and exc.errno in (54, 10054):
                    ws_params.update(
                        sequence=self.ws.sequence,
                        gateway=self.ws.gateway,
                        initial=False,
                        resume=True,
                        session=self.ws.session_id,
                    )
                    continue

                # We should only get this when an unhandled close code happens,
                # such as a clean disconnect (1000) or a bad state (bad token, etc)
                # Sometimes, Discord sends us 1000 for unknown reasons so we should
                # reconnect regardless and rely on is_closed instead
                if isinstance(exc, ConnectionClosed):
                    if exc.code != 1000:
                        await self.close()
                        raise

                retry = backoff.delay()
                _log.exception("Attempting a reconnect in %.2fs", retry)
                await asyncio.sleep(retry)
                # Always try to RESUME the connection
                # If the connection is not RESUME-able then the gateway will invalidate the session
                # This is apparently what the official Discord client does
                ws_params.update(
                    sequence=self.ws.sequence,
                    gateway=self.ws.gateway,
                    resume=True,
                    session=self.ws.session_id,
                )

    async def close(self) -> None:
        """|coro|

        Closes the connection to Discord.
        """
        if self._closed:
            return

        self._closed = True

        if self.ws is not None and self.ws.open:
            await self.ws.close(code=1000)

        await self.http.close()

        if self._ready is not MISSING:
            self._ready.clear()

        self.loop = MISSING

    def clear(self) -> None:
        """Clears the internal state of the bot.

        After this, the client can be considered "re-opened", i.e. :meth:`is_closed`
        and :meth:`is_ready` both return ``False`` along with the bot's internal
        cache cleared.
        """
        self._closed = False
        self._ready.clear()
        self._connection.clear()
        self.http.clear()

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        """|coro|

        A shorthand coroutine for :meth:`login` + :meth:`connect`.

        Parameters
        -----------
        token: :class:`str`
            The authentication token.
        reconnect: :class:`bool`
            If we should attempt reconnecting, either due to internet
            failure or a specific failure on Discord's part. Certain
            disconnects that lead to bad state will not be handled (such as bad tokens).

        Raises
        -------
        TypeError
            An unexpected keyword argument was received.
        """
        await self.login(token)
        await self.connect(reconnect=reconnect)

    def run(
        self,
        token: str,
        *,
        reconnect: bool = True,
        log_handler: Optional[logging.Handler] = MISSING,
        log_formatter: logging.Formatter = MISSING,
        log_level: int = MISSING,
        root_logger: bool = False,
    ) -> None:
        """A blocking call that abstracts away the event loop
        initialisation from you.

        If you want more control over the event loop then this
        function should not be used. Use :meth:`start` coroutine
        or :meth:`connect` + :meth:`login`.

        This function also sets up the logging library to make it easier
        for beginners to know what is going on with the library. For more
        advanced users, this can be disabled by passing ``None`` to
        the ``log_handler`` parameter.

        .. warning::

            This function must be the last function to call due to the fact that it
            is blocking. That means that registration of events or anything being
            called after this function call will not execute until it returns.

        Parameters
        -----------
        token: :class:`str`
            The authentication token.
        reconnect: :class:`bool`
            If we should attempt reconnecting, either due to internet
            failure or a specific failure on Discord's part. Certain
            disconnects that lead to bad state will not be handled (such as bad tokens).
        log_handler: Optional[:class:`logging.Handler`]
            The log handler to use for the library's logger. If this is ``None``
            then the library will not set up anything logging related. Logging
            will still work if ``None`` is passed, though it is your responsibility
            to set it up.

            The default log handler if not provided is :class:`logging.StreamHandler`.

            .. versionadded:: 2.0
        log_formatter: :class:`logging.Formatter`
            The formatter to use with the given log handler. If not provided then it
            defaults to a colour based logging formatter (if available).

            .. versionadded:: 2.0
        log_level: :class:`int`
            The default log level for the library's logger. This is only applied if the
            ``log_handler`` parameter is not ``None``. Defaults to ``logging.INFO``.

            .. versionadded:: 2.0
        root_logger: :class:`bool`
            Whether to set up the root logger rather than the library logger.
            By default, only the library logger (``'discord'``) is set up. If this
            is set to ``True`` then the root logger is set up as well.

            Defaults to ``False``.

            .. versionadded:: 2.0
        """

        async def runner():
            async with self:
                await self.start(token, reconnect=reconnect)

        if log_handler is not None:
            utils.setup_logging(
                handler=log_handler,
                formatter=log_formatter,
                level=log_level,
                root=root_logger,
            )

        try:
            asyncio.run(runner())
        except KeyboardInterrupt:
            # Nothing to do here
            # `asyncio.run` handles the loop cleanup
            # and `self.start` closes all sockets and the HTTPClient instance
            return

    # Properties

    def is_closed(self) -> bool:
        """:class:`bool`: Indicates if the websocket connection is closed."""
        return self._closed

    @property
    def initial_status(self) -> Optional[Status]:
        """Optional[:class:`.Status`]: The status set upon logging in.

        .. versionadded:: 2.0
        """
        if self._connection._status in {state.value for state in Status}:
            return Status(self._connection._status)

    @initial_status.setter
    def initial_status(self, value: Status):
        if value is Status.offline:
            self._connection._status = "invisible"
        elif isinstance(value, Status):
            self._connection._status = str(value)
        else:
            raise TypeError("status must derive from Status")

    @property
    def status(self) -> Status:
        """:class:`.Status`: The user's overall status.

        .. versionadded:: 2.0
        """
        status = getattr(self._connection.all_session, "status", None)
        if status is None and not self.is_closed():
            status = getattr(self._connection.settings, "status", status)
        return status or Status.offline

    @property
    def raw_status(self) -> str:
        """:class:`str`: The user's overall status as a string value.

        .. versionadded:: 2.0
        """
        return str(self.status)

    @property
    def client_status(self) -> Status:
        """:class:`.Status`: The library's status.

        .. versionadded:: 2.0
        """
        status = getattr(self._connection.current_session, "status", None)
        if status is None and not self.is_closed():
            status = getattr(self._connection.settings, "status", status)
        return status or Status.offline

    @property
    def allowed_mentions(self) -> Optional[AllowedMentions]:
        """Optional[:class:`~discord.AllowedMentions`]: The allowed mention configuration.

        .. versionadded:: 1.4
        """
        return self._connection.allowed_mentions

    @allowed_mentions.setter
    def allowed_mentions(self, value: Optional[AllowedMentions]) -> None:
        if value is None or isinstance(value, AllowedMentions):
            self._connection.allowed_mentions = value
        else:
            raise TypeError(
                f"allowed_mentions must be AllowedMentions not {value.__class__!r}"
            )

    # Helpers/Getters

    @property
    def users(self) -> List[User]:
        """List[:class:`~discord.User`]: Returns a list of all the users the current user can see."""
        return list(self._connection._users.values())

    def get_channel(self, id: int, /) -> Optional[Union[GuildChannel, PrivateChannel]]:
        """Returns a channel or thread with the given ID.

        .. versionchanged:: 2.0

            ``id`` parameter is now positional-only.

        Parameters
        -----------
        id: :class:`int`
            The ID to search for.

        Returns
        --------
        Optional[Union[:class:`.abc.GuildChannel`, :class:`.Thread`, :class:`.abc.PrivateChannel`]]
            The returned channel or ``None`` if not found.
        """
        return self._connection.get_channel(id)  # type: ignore # The cache contains all channel types

    def get_partial_messageable(
        self,
        id: int,
        *,
        guild_id: Optional[int] = None,
        type: Optional[ChannelType] = None,
    ) -> PartialMessageable:
        """Returns a partial messageable with the given channel ID.

        This is useful if you have a channel_id but don't want to do an API call
        to send messages to it.

        .. versionadded:: 2.0

        Parameters
        -----------
        id: :class:`int`
            The channel ID to create a partial messageable for.
        guild_id: Optional[:class:`int`]
            The optional guild ID to create a partial messageable for.

            This is not required to actually send messages, but it does allow the
            :meth:`~discord.PartialMessageable.jump_url` and
            :attr:`~discord.PartialMessageable.guild` properties to function properly.
        type: Optional[:class:`.ChannelType`]
            The underlying channel type for the partial messageable.

        Returns
        --------
        :class:`.PartialMessageable`
            The partial messageable
        """
        return PartialMessageable(
            state=self._connection, id=id, guild_id=guild_id, type=type
        )

    def get_guild(self, id: int, /) -> Optional[Guild]:
        """Returns a guild with the given ID.

        .. versionchanged:: 2.0

            ``id`` parameter is now positional-only.

        Parameters
        -----------
        id: :class:`int`
            The ID to search for.

        Returns
        --------
        Optional[:class:`.Guild`]
            The guild or ``None`` if not found.
        """
        return self._connection._get_guild(id)

    def get_user(self, id: int, /) -> Optional[User]:
        """Returns a user with the given ID.

        .. versionchanged:: 2.0

            ``id`` parameter is now positional-only.

        Parameters
        -----------
        id: :class:`int`
            The ID to search for.

        Returns
        --------
        Optional[:class:`~discord.User`]
            The user or ``None`` if not found.
        """
        return self._connection.get_user(id)

    def get_all_channels(self) -> Generator[GuildChannel, None, None]:
        """A generator that retrieves every :class:`.abc.GuildChannel` the client can 'access'.

        This is equivalent to: ::

            for guild in client.guilds:
                for channel in guild.channels:
                    yield channel

        .. note::

            Just because you receive a :class:`.abc.GuildChannel` does not mean that
            you can communicate in said channel. :meth:`.abc.GuildChannel.permissions_for` should
            be used for that.

        Yields
        ------
        :class:`.abc.GuildChannel`
            A channel the client can 'access'.
        """

        for guild in self.guilds:
            yield from guild.channels

    # Listeners/Waiters

    async def wait_until_ready(self) -> None:
        """|coro|

        Waits until the client's internal cache is all ready.

        .. warning::

            Calling this inside :meth:`setup_hook` can lead to a deadlock.
        """
        if self._ready is not MISSING:
            await self._ready.wait()
        else:
            raise RuntimeError(
                "Client has not been properly initialised. Please use the login method"
                " or asynchronous context manager before calling this method"
            )

    def wait_for(
        self,
        event: str,
        /,
        *,
        check: Optional[Callable[..., bool]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """|coro|

        Waits for a WebSocket event to be dispatched.

        This could be used to wait for a user to reply to a message,
        or to react to a message, or to edit a message in a self-contained
        way.

        The ``timeout`` parameter is passed onto :func:`asyncio.wait_for`. By default,
        it does not timeout. Note that this does propagate the
        :exc:`asyncio.TimeoutError` for you in case of timeout and is provided for
        ease of use.

        In case the event returns multiple arguments, a :class:`tuple` containing those
        arguments is returned instead. Please check the
        :ref:`documentation <discord-api-events>` for a list of events and their
        parameters.

        This function returns the **first event that meets the requirements**.

        Examples
        ---------

        Waiting for a user reply: ::

            @client.event
            async def on_message(message):
                if message.content.startswith('$greet'):
                    channel = message.channel
                    await channel.send('Say hello!')

                    def check(m):
                        return m.content == 'hello' and m.channel == channel

                    msg = await client.wait_for('message', check=check)
                    await channel.send(f'Hello {msg.author}!')

        Waiting for a thumbs up reaction from the message author: ::

            @client.event
            async def on_message(message):
                if message.content.startswith('$thumb'):
                    channel = message.channel
                    await channel.send('Send me that \N{THUMBS UP SIGN} reaction, mate')

                    def check(reaction, user):
                        return user == message.author and str(reaction.emoji) == '\N{THUMBS UP SIGN}'

                    try:
                        reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
                    except asyncio.TimeoutError:
                        await channel.send('\N{THUMBS DOWN SIGN}')
                    else:
                        await channel.send('\N{THUMBS UP SIGN}')

        .. versionchanged:: 2.0

            ``event`` parameter is now positional-only.


        Parameters
        ------------
        event: :class:`str`
            The event name, similar to the :ref:`event reference <discord-api-events>`,
            but without the ``on_`` prefix, to wait for.
        check: Optional[Callable[..., :class:`bool`]]
            A predicate to check what to wait for. The arguments must meet the
            parameters of the event being waited for.
        timeout: Optional[:class:`float`]
            The number of seconds to wait before timing out and raising
            :exc:`asyncio.TimeoutError`.

        Raises
        -------
        asyncio.TimeoutError
            If a timeout is provided and it was reached.

        Returns
        --------
        Any
            Returns no arguments, a single argument, or a :class:`tuple` of multiple
            arguments that mirrors the parameters passed in the
            :ref:`event reference <discord-api-events>`.
        """

        future = self.loop.create_future()
        if check is None:

            def _check(*args):
                return True

            check = _check

        ev = event.lower()
        try:
            listeners = self._listeners[ev]
        except KeyError:
            listeners = []
            self._listeners[ev] = listeners

        listeners.append((future, check))
        return asyncio.wait_for(future, timeout)

    # Event registration

    def event(self, coro: Coro, /) -> Coro:
        """A decorator that registers an event to listen to.

        You can find more info about the events on the :ref:`documentation below <discord-api-events>`.

        The events must be a :ref:`coroutine <coroutine>`, if not, :exc:`TypeError` is raised.

        Example
        ---------

        .. code-block:: python3

            @client.event
            async def on_ready():
                print('Ready!')

        .. versionchanged:: 2.0

            ``coro`` parameter is now positional-only.

        Raises
        --------
        TypeError
            The coroutine passed is not actually a coroutine.
        """

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("event registered must be a coroutine function")

        setattr(self, coro.__name__, coro)
        _log.debug("%s has successfully been registered as an event", coro.__name__)
        return coro

    async def change_presence(
        self,
        *,
        status: Optional[Status] = None,
        afk: bool = False,
        edit_settings: bool = True,
    ) -> None:
        """|coro|

        Changes the client's presence.

        .. versionchanged:: 2.0
            Edits are no longer in place.
            Added option to update settings.

        .. versionchanged:: 2.0
            This function will now raise :exc:`TypeError` instead of
            ``InvalidArgument``.

        Example
        ---------

        .. code-block:: python3

            game = discord.Game("with the API")
            await client.change_presence(status=discord.Status.idle, activity=game)

        Parameters
        ----------
        activity: Optional[:class:`.BaseActivity`]
            The activity being done. ``None`` if no activity is done.
        activities: Optional[List[:class:`.BaseActivity`]]
            A list of the activities being done. ``None`` if no activities
            are done. Cannot be sent with ``activity``.
        status: Optional[:class:`.Status`]
            Indicates what status to change to. If ``None``, then
            :attr:`.Status.online` is used.
        afk: :class:`bool`
            Indicates if you are going AFK. This allows the Discord
            client to know how to handle push notifications better
            for you in case you are actually idle and not lying.
        edit_settings: :class:`bool`
            Whether to update the settings with the new status and/or
            custom activity. This will broadcast the change and cause
            all connected (official) clients to change presence as well.
            Required for setting/editing ``expires_at`` for custom activities.
            It's not recommended to change this, as setting it to ``False`` causes undefined behavior.

        Raises
        ------
        TypeError
            The ``activity`` parameter is not the proper type.
            Both ``activity`` and ``activities`` were passed.
        """
        activities = []

        if status is None:
            status = Status.online
        elif status is Status.offline:
            status = Status.invisible
        await self.ws.change_presence(status=status, activities=activities, afk=afk)

        if edit_settings:
            custom_activity = None

            for activity in activities:
                if getattr(activity, "type", None) is ActivityType.custom:
                    custom_activity = activity

            payload: Dict[str, Any] = {}
            if status != getattr(self.settings, "status", None):
                payload["status"] = status
            if custom_activity != getattr(self.settings, "custom_activity", None):
                payload["custom_activity"] = custom_activity
            if payload and self.settings:
                await self.settings.edit(**payload)

    # Guild stuff

    async def fetch_guilds(self, *, with_counts: bool = True) -> List[UserGuild]:
        """|coro|

        Retrieves all your guilds.

        .. note::

            This method is an API call. For general usage, consider :attr:`guilds` instead.

        .. versionchanged:: 2.0

            This method now returns a list of :class:`.UserGuild` instead of :class:`.Guild`.

        Parameters
        -----------
        with_counts: :class:`bool`
            Whether to fill :attr:`.Guild.approximate_member_count` and :attr:`.Guild.approximate_presence_count`.

        Raises
        ------
        HTTPException
            Getting the guilds failed.

        Returns
        --------
        List[:class:`.UserGuild`]
            A list of all your guilds.
        """
        state = self._connection
        guilds = await state.http.get_guilds(with_counts)
        return [UserGuild(data=data, state=state) for data in guilds]

    async def fetch_guild(self, guild_id: int, /, *, with_counts: bool = True) -> Guild:
        """|coro|

        Retrieves a :class:`.Guild` from an ID.

        .. note::

            Using this, you will **not** receive :attr:`.Guild.channels` and :attr:`.Guild.members`.

        .. note::

            This method is an API call. For general usage, consider :meth:`get_guild` instead.

        .. versionchanged:: 2.0

            ``guild_id`` parameter is now positional-only.

        Parameters
        -----------
        guild_id: :class:`int`
            The guild's ID to fetch from.
        with_counts: :class:`bool`
            Whether to include count information in the guild. This fills in
            :attr:`.Guild.approximate_member_count` and :attr:`.Guild.approximate_presence_count`.

            .. versionadded:: 2.0

        Raises
        ------
        Forbidden
            You do not have access to the guild.
        HTTPException
            Getting the guild failed.

        Returns
        --------
        :class:`.Guild`
            The guild from the ID.
        """
        state = self._connection
        data = await state.http.get_guild(guild_id, with_counts)
        guild = state.create_guild(data)
        guild._cs_joined = True
        return guild

    async def fetch_guild_preview(self, guild_id: int, /) -> Guild:
        """|coro|

        Retrieves a public :class:`.Guild` preview from an ID.

        .. versionadded:: 2.0

        Raises
        ------
        NotFound
            Guild with given ID does not exist/is not public.
        HTTPException
            Retrieving the guild failed.

        Returns
        --------
        :class:`.Guild`
            The guild from the ID.
        """
        state = self._connection
        data = await state.http.get_guild_preview(guild_id)
        return state.create_guild(data)

    # Miscellaneous stuff

    async def fetch_user(self, user_id: int, /) -> User:
        """|coro|

        Retrieves a :class:`discord.User` based on their ID.
        You do not have to share any guilds with the user to get
        this information, however many operations do require that you do.

        .. note::

            This method is an API call. If you have member cache enabled, consider :meth:`get_user` instead.

        .. warning::

            This API route is not well-used by the Discord client and may increase your chances at getting detected.
            Consider :meth:`fetch_user_profile` if you share a guild/relationship with the user.

        .. versionchanged:: 2.0

            ``user_id`` parameter is now positional-only.

        Parameters
        -----------
        user_id: :class:`int`
            The user's ID to fetch from.

        Raises
        -------
        NotFound
            A user with this ID does not exist.
        HTTPException
            Fetching the user failed.

        Returns
        --------
        :class:`discord.User`
            The user you requested.
        """
        data = await self.http.get_user(user_id)
        return User(state=self._connection, data=data)

    async def fetch_channel(
        self, channel_id: int, /
    ) -> Union[GuildChannel, PrivateChannel]:
        """|coro|

        Retrieves a :class:`.abc.GuildChannel`, :class:`.abc.PrivateChannel`, or :class:`.Thread` with the specified ID.

        .. note::

            This method is an API call. For general usage, consider :meth:`get_channel` instead.

        .. versionadded:: 1.2

        .. versionchanged:: 2.0

            ``channel_id`` parameter is now positional-only.

        Raises
        -------
        InvalidData
            An unknown channel type was received from Discord.
        HTTPException
            Retrieving the channel failed.
        NotFound
            Invalid Channel ID.
        Forbidden
            You do not have permission to fetch this channel.

        Returns
        --------
        Union[:class:`.abc.GuildChannel`, :class:`.abc.PrivateChannel`]
            The channel from the ID.
        """
        data = await self.http.get_channel(channel_id)

        factory, ch_type = _channel_factory(data["type"])
        if factory is None:
            raise InvalidData(
                "Unknown channel type {type} for channel ID {id}.".format_map(data)
            )

        if str(ch_type) in ChannelType.private:
            # The factory will be a DMChannel here
            return factory(me=self.user, data=data, state=self._connection)
        # The factory can't be a DMChannel here
        guild_id = int(data["guild_id"])  # type: ignore
        guild = self._connection._get_or_create_unavailable_guild(guild_id)
        # the factory should be a GuildChannel or Thread
        return factory(guild=guild, state=self._connection, data=data)

    async def create_dm(self, user: Snowflake, /) -> DMChannel:
        """|coro|

        Creates a :class:`.DMChannel` with this user.

        This should be rarely called, as this is done transparently for most
        people.

        .. versionadded:: 2.0

        Parameters
        -----------
        user: :class:`~discord.abc.Snowflake`
            The user to create a DM with.

        Returns
        -------
        :class:`.DMChannel`
            The channel that was created.
        """
        state = self._connection
        found = state._get_private_channel_by_user(user.id)
        if found:
            return found

        data = await state.http.start_private_message(user.id)
        return state.add_dm_channel(data)

    async def authorizations(self) -> List[OAuth2Token]:
        """|coro|

        Retrieves the OAuth2 applications authorized on your account.

        .. versionadded:: 2.1

        Raises
        -------
        HTTPException
            Retrieving the authorized applications failed.

        Returns
        -------
        List[:class:`.OAuth2Token`]
            The OAuth2 applications authorized on your account.
        """
        state = self._connection
        data = await state.http.get_oauth2_tokens()
        return [OAuth2Token(state=state, data=d) for d in data]

    async def fetch_authorization(
        self,
        application_id: int,
        /,
        *,
        scopes: Collection[str],
        response_type: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
        code_challenge: Optional[str] = None,
        state: Optional[str] = None,
    ) -> OAuth2Authorization:
        """|coro|

        Retrieves an OAuth2 authorization for the given application.
        This provides information about the application before you authorize it.

        .. versionadded:: 2.1

        Parameters
        -----------
        application_id: :class:`int`
            The ID of the application to fetch the authorization for.
        scopes: List[:class:`str`]
            The scopes to request for the authorization.
        response_type: Optional[:class:`str`]
            The response type that will be used for the authorization, if using the full OAuth2 flow.
        redirect_uri: Optional[:class:`str`]
            The redirect URI that will be used for the authorization, if using the full OAuth2 flow.
            If this isn't provided and ``response_type`` is provided, then the default redirect URI
            for the application will be provided in the returned authorization.
        code_challenge_method: Optional[:class:`str`]
            The code challenge method that will be used for the PKCE authorization, if using the full OAuth2 flow.
        code_challenge: Optional[:class:`str`]
            The code challenge that will be used for the PKCE authorization, if using the full OAuth2 flow.
        state: Optional[:class:`str`]
            The state that will be used for authorization security.

        Raises
        -------
        HTTPException
            Fetching the authorization failed.

        Returns
        -------
        :class:`.OAuth2Authorization`
            The authorization for the application.
        """
        _state = self._connection
        data = await _state.http.get_oauth2_authorization(
            application_id,
            list(scopes),
            response_type,
            redirect_uri,
            code_challenge_method,
            code_challenge,
            state,
        )
        return OAuth2Authorization(
            _state=_state,
            data=data,
            scopes=list(scopes),
            response_type=response_type,
            code_challenge_method=code_challenge_method,
            code_challenge=code_challenge,
            state=state,
        )

    async def create_authorization(
        self,
        application_id: int,
        /,
        *,
        scopes: Collection[str],
        response_type: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
        code_challenge: Optional[str] = None,
        state: Optional[str] = None,
        guild: Snowflake = MISSING,
        channel: Snowflake = MISSING,
    ) -> str:
        """|coro|

        Creates an OAuth2 authorization for the given application. It is recommended to instead first
        fetch the authorization information using :meth:`fetch_authorization` and then call :meth:`.OAuth2Authorization.authorize`.

        .. versionadded:: 2.1

        Parameters
        -----------
        application_id: :class:`int`
            The ID of the application to create the authorization for.
        scopes: List[:class:`str`]
            The scopes to request for the authorization.
        response_type: Optional[:class:`str`]
            The response type to use for the authorization, if using the full OAuth2 flow.
        redirect_uri: Optional[:class:`str`]
            The redirect URI to use for the authorization, if using the full OAuth2 flow.
            If this isn't provided and ``response_type`` is provided, then the default redirect URI
            for the application will be used.
        code_challenge_method: Optional[:class:`str`]
            The code challenge method to use for the PKCE authorization, if using the full OAuth2 flow.
        code_challenge: Optional[:class:`str`]
            The code challenge to use for the PKCE authorization, if using the full OAuth2 flow.
        state: Optional[:class:`str`]
            The state to use for authorization security.
        guild: :class:`.Guild`
            The guild to authorize for, if authorizing with the ``applications.commands`` or ``bot`` scopes.
        channel: Union[:class:`.TextChannel`, :class:`.VoiceChannel`, :class:`.StageChannel`]
            The channel to authorize for, if authorizing with the ``webhooks.incoming`` scope. See :meth:`.Guild.webhook_channels`.
        permissions: :class:`.Permissions`
            The permissions to grant, if authorizing with the ``bot`` scope.

        Raises
        -------
        HTTPException
            Creating the authorization failed.

        Returns
        -------
        :class:`str`
            The URL to redirect the user to for authorization.
        """
        _state = self._connection
        data = await _state.http.authorize_oauth2(
            application_id,
            list(scopes),
            response_type,
            redirect_uri,
            code_challenge_method,
            code_challenge,
            state,
            guild_id=guild.id if guild else None,
            webhook_channel_id=channel.id if channel else None,
            permissions=None,
        )
        return data["location"]
