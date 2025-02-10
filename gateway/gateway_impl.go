package gateway

import (
	"compress/zlib"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
	"io"
	"net"
	"strconv"
	"sync"
	"syscall"
	"time"

	"github.com/fasthttp/websocket"
)

var _ Gateway = (*gatewayImpl)(nil)

// New creates a new Gateway instance with the provided token.
func New(ctx context.Context, token string, eventHandlerFunc EventHandlerFunc) Gateway {
	config := DefaultConfig()

	g := &gatewayImpl{
		config:           *config,
		eventHandlerFunc: eventHandlerFunc,
		token:            token,
		statusChan:       make(chan Status, 1),
		ctx:              ctx,
	}

	g.statusChan <- StatusUnconnected

	return g
}

type gatewayImpl struct {
	ReadyUser        *types.User
	config           Config
	eventHandlerFunc EventHandlerFunc
	token            string

	conn            *websocket.Conn
	connMu          sync.Mutex
	heartbeatCancel context.CancelFunc
	statusChan      chan Status
	ctx             context.Context

	heartbeatInterval     time.Duration
	lastHeartbeatSent     time.Time
	lastHeartbeatReceived time.Time
}

func (g *gatewayImpl) SessionID() *string {
	g.connMu.Lock()
	defer g.connMu.Unlock()
	return g.config.SessionID
}

func (g *gatewayImpl) User() *types.User {
	return g.ReadyUser
}

func (g *gatewayImpl) UserAgent() string {
	return g.config.UserAgent
}

func (g *gatewayImpl) LastSequenceReceived() *int {
	return g.config.LastSequenceReceived
}

func (g *gatewayImpl) Open(ctx context.Context) error {
	return g.reconnectTry(ctx, 0)
}

func (g *gatewayImpl) open(ctx context.Context) error {
	g.connMu.Lock()
	defer g.connMu.Unlock()
	if g.conn != nil {
		return types.ErrGatewayAlreadyConnected
	}

	wsURL := g.config.URL
	if g.config.ResumeURL != nil && g.config.EnableResumeURL {
		wsURL = *g.config.ResumeURL
	}
	gatewayURL := fmt.Sprintf("%s?v=%d&encoding=json", wsURL, Version)
	g.lastHeartbeatSent = time.Now().UTC()
	conn, rs, err := g.config.Dialer.DialContext(ctx, gatewayURL, nil)
	if err != nil {
		body := ""
		if rs != nil && rs.Body != nil {
			defer func() {
				_ = rs.Body.Close()
			}()
			rawBody, bErr := io.ReadAll(rs.Body)
			if bErr != nil {
				utils.Log(utils.Discord, utils.Error, g.SafeGetUsername(), fmt.Sprintf("Error while reading response body: %s", err.Error()))
			}
			body = string(rawBody)
		}

		utils.Log(utils.Discord, utils.Error, g.SafeGetUsername(), fmt.Sprintf("Error connecting to the gateway: %s | url=%s | body=%s", err.Error(), gatewayURL, body))
		return err
	}

	g.conn = conn

	// reset rate limiter when connecting
	g.config.RateLimiter.Reset()

	go g.listen(conn)

	return nil
}

func (g *gatewayImpl) Close(ctx context.Context) {
	g.CloseWithCode(ctx, websocket.CloseNormalClosure, "Shutting down")
}

func (g *gatewayImpl) CloseWithCode(ctx context.Context, code int, message string) {
	if g.heartbeatCancel != nil {
		g.heartbeatCancel()
	}

	g.connMu.Lock()
	defer g.connMu.Unlock()
	if g.conn != nil {
		g.config.RateLimiter.Close(ctx)
		utils.Log(utils.Discord, utils.Info, g.SafeGetUsername(), fmt.Sprintf("Closing gateway connection code=%d | message=%s", code, message))
		if err := g.conn.WriteMessage(websocket.CloseMessage, websocket.FormatCloseMessage(code, message)); err != nil && !errors.Is(err, websocket.ErrCloseSent) {
			utils.Log(utils.Discord, utils.Error, g.SafeGetUsername(), fmt.Sprintf("Error writing close code: %s", err.Error()))
		}
		_ = g.conn.Close()
		g.conn = nil

		// clear resume data as we closed gracefully
		if code == websocket.CloseNormalClosure || code == websocket.CloseGoingAway {
			g.config.SessionID = nil
			g.config.ResumeURL = nil
			g.config.LastSequenceReceived = nil
		}
	}
}

func (g *gatewayImpl) StatusUpdates() <-chan Status {
	return g.statusChan
}

func (g *gatewayImpl) Send(ctx context.Context, op Opcode, d MessageData) error {
	data, err := json.Marshal(Message{
		Op: op,
		D:  d,
	})
	if err != nil {
		return err
	}
	return g.send(ctx, websocket.TextMessage, data)
}

func (g *gatewayImpl) send(ctx context.Context, messageType int, data []byte) error {
	g.connMu.Lock()
	defer g.connMu.Unlock()
	if g.conn == nil {
		return types.ErrGatewayNotConnected
	}

	if err := g.config.RateLimiter.Wait(ctx); err != nil {
		return err
	}

	defer g.config.RateLimiter.Unlock()
	return g.conn.WriteMessage(messageType, data)
}

func (g *gatewayImpl) Latency() time.Duration {
	return g.lastHeartbeatReceived.Sub(g.lastHeartbeatSent)
}

func (g *gatewayImpl) Presence() *MessageDataPresenceUpdate {
	return g.config.Presence
}

func (g *gatewayImpl) reconnectTry(ctx context.Context, try int) error {
	delay := time.Duration(try) * 2 * time.Second
	if delay > 30*time.Second {
		delay = 30 * time.Second
	}

	timer := time.NewTimer(delay)
	defer timer.Stop()
	select {
	case <-ctx.Done():
		timer.Stop()
		return ctx.Err()
	case <-timer.C:
	}

	if err := g.open(ctx); err != nil {
		if errors.Is(err, types.ErrGatewayAlreadyConnected) {
			return err
		}
		utils.Log(utils.Discord, utils.Error, g.SafeGetUsername(), fmt.Sprintf("Failed to reconnect gateway: %s", err.Error()))
		g.statusChan <- StatusDisconnected
		return g.reconnectTry(ctx, try+1)
	}
	return nil
}

func (g *gatewayImpl) reconnect() {
	err := g.reconnectTry(context.Background(), 0)
	if err != nil {
		utils.Log(utils.Discord, utils.Error, g.SafeGetUsername(), fmt.Sprintf("Failed to reopen gateway: %s", err.Error()))
	}
}

func (g *gatewayImpl) heartbeat() {
	ctx, cancel := context.WithCancel(context.Background())
	g.heartbeatCancel = cancel

	heartbeatTicker := time.NewTicker(g.heartbeatInterval)
	defer heartbeatTicker.Stop()

	for {
		select {
		case <-ctx.Done():
			return

		case <-heartbeatTicker.C:
			g.sendHeartbeat()
		}
	}
}

func (g *gatewayImpl) sendHeartbeat() {
	ctx, cancel := context.WithTimeout(context.Background(), g.heartbeatInterval)
	defer cancel()
	if err := g.Send(ctx, OpcodeHeartbeat, MessageDataHeartbeat(*g.config.LastSequenceReceived)); err != nil {
		if errors.Is(err, types.ErrGatewayNotConnected) || errors.Is(err, syscall.EPIPE) {
			return
		}
		utils.Log(utils.Discord, utils.Error, g.SafeGetUsername(), fmt.Sprintf("Failed to send heartbeat: %s", err.Error()))
		closeCtx, closeCancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer closeCancel()
		g.CloseWithCode(closeCtx, websocket.CloseServiceRestart, "heartbeat timeout")
		go g.reconnect()
		return
	}
	g.lastHeartbeatSent = time.Now().UTC()
}

func (g *gatewayImpl) identify() {
	g.statusChan <- StatusIdentifying

	identify := MessageDataIdentify{
		Capabilities: 30717,
		Token:        g.token,
		Properties: IdentifyCommandDataProperties{
			Browser:           "Chrome",
			BrowserUserAgent:  g.config.UserAgent,
			BrowserVersion:    "125.0.0.0",
			ClientBuildNumber: g.mustGetLatestBuild(),
			DesignID:          0,
			Device:            "",
			OS:                "Windows",
			OSVersion:         "10",
			ReleaseChannel:    "stable",
			SystemLocale:      g.mustGetLocale(),
		},
		ClientState: ClientState{
			GuildVersions: struct{}{},
		},
		Compress: g.config.Compress,
		Presence: g.config.Presence,
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := g.Send(ctx, OpcodeIdentify, identify); err != nil {
		utils.Log(utils.Discord, utils.Error, g.SafeGetUsername(), fmt.Sprintf("Error sending Identify command: %s", err.Error()))
	}
	g.statusChan <- StatusWaitingForReady
}

func (g *gatewayImpl) resume() {
	g.statusChan <- StatusResuming
	resume := MessageDataResume{
		Token:     g.token,
		SessionID: *g.config.SessionID,
		Seq:       *g.config.LastSequenceReceived,
	}
	utils.Log(utils.Discord, utils.Info, g.SafeGetUsername(), "Sending resume command")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := g.Send(ctx, OpcodeResume, resume); err != nil {
		utils.Log(utils.Discord, utils.Error, g.SafeGetUsername(), fmt.Sprintf("Error sending resume command: %s", err.Error()))
	}
}

func (g *gatewayImpl) listen(conn *websocket.Conn) {
	g.statusChan <- StatusWaitingForHello

loop:
	for {
		mt, r, err := conn.NextReader()
		if err != nil {
			g.connMu.Lock()
			sameConnection := g.conn == conn
			g.connMu.Unlock()

			// if sameConnection is false, it means the connection has been closed by the user, and we can just exit
			if !sameConnection {
				return
			}

			reconnect := true
			var closeError *websocket.CloseError
			if errors.As(err, &closeError) {
				closeCode := CloseEventCodeByCode(closeError.Code)
				reconnect = closeCode.Reconnect

				if closeCode == CloseEventCodeInvalidSeq {
					g.config.LastSequenceReceived = nil
					g.config.SessionID = nil
					g.config.ResumeURL = nil
				}

				utils.Log(utils.Discord, utils.Error, g.SafeGetUsername(), "gateway close reconnect="+strconv.FormatBool(reconnect)+
					" | code="+strconv.Itoa(closeError.Code)+
					" | error="+closeError.Text)

				if closeError.Code == 4004 {
					g.statusChan <- StatusInvalidToken
				}
			} else if errors.Is(err, net.ErrClosed) {
				// we closed the connection ourselves. Don't try to reconnect here
				reconnect = false
			} else {
				utils.Log(utils.Discord, utils.Error, g.SafeGetUsername(), fmt.Sprintf("Failed to read next message from gateway: %s", err.Error()))
			}

			// make sure the connection is properly closed
			ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
			g.CloseWithCode(ctx, websocket.CloseServiceRestart, "reconnecting")
			cancel()
			if g.config.AutoReconnect && reconnect {
				go g.reconnect()
			}

			break loop
		}

		message, err := g.parseMessage(mt, r)
		if err != nil {
			utils.Log(utils.Discord, utils.Error, g.SafeGetUsername(), fmt.Sprintf("Error while parsing gateway message: %s", err.Error()))
			continue
		}

		switch message.Op {
		case OpcodeHello:
			g.heartbeatInterval = time.Duration(message.D.(MessageDataHello).HeartbeatInterval) * time.Millisecond
			g.lastHeartbeatReceived = time.Now().UTC()
			go g.heartbeat()

			if g.config.LastSequenceReceived == nil || g.config.SessionID == nil {
				g.identify()
			} else {
				g.resume()
			}

		case OpcodeDispatch:
			// set last sequence received
			g.config.LastSequenceReceived = &message.S

			eventData, ok := message.D.(EventData)
			if !ok && message.D != nil {
				utils.Log(utils.Discord, utils.Error, g.SafeGetUsername(), fmt.Sprintf("Invalid message data received: %T", message.D))
				continue
			}

			// get session id here
			if readyEvent, ok := eventData.(EventReady); ok {
				g.config.SessionID = &readyEvent.SessionID
				g.config.ResumeURL = &readyEvent.ResumeGatewayURL
				g.ReadyUser = &readyEvent.User
				g.statusChan <- StatusReady
			}

			if _, ok := eventData.(EventUnknown); ok {
				continue
			}

			// push message to the command manager
			g.eventHandlerFunc(message.T, eventData)

		case OpcodeHeartbeat:
			g.sendHeartbeat()

		case OpcodeReconnect:
			ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
			g.CloseWithCode(ctx, websocket.CloseServiceRestart, "received reconnect")
			cancel()
			go g.reconnect()
			break loop

		case OpcodeInvalidSession:
			canResume := message.D.(MessageDataInvalidSession)

			code := websocket.CloseNormalClosure
			if canResume {
				code = websocket.CloseServiceRestart
			} else {
				// clear resume info
				g.config.SessionID = nil
				g.config.LastSequenceReceived = nil
				g.config.ResumeURL = nil
			}

			ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
			g.CloseWithCode(ctx, code, "invalid session")
			cancel()
			go g.reconnect()
			break loop

		case OpcodeHeartbeatACK:
			g.lastHeartbeatReceived = time.Now().UTC()

		default:
			utils.Log(utils.Discord, utils.Error, g.SafeGetUsername(), fmt.Sprintf("Unknown opcode received: %v", int(message.Op)))
		}
	}
}

func (g *gatewayImpl) parseMessage(mt int, r io.Reader) (Message, error) {
	if mt == websocket.BinaryMessage {
		reader, err := zlib.NewReader(r)
		if err != nil {
			return Message{}, fmt.Errorf("failed to decompress zlib: %w", err)
		}
		defer reader.Close()
		r = reader
	}

	var message Message
	return message, json.NewDecoder(r).Decode(&message)
}

func (g *gatewayImpl) SafeGetUsername() string {
	if g.User() != nil {
		return g.User().Username
	} else {
		return utils.GetAccountNumber(g.token)
	}
}
