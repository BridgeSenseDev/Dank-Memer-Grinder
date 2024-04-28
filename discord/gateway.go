package discord

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"sync"
	"time"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/fasthttp/websocket"
	"github.com/goccy/go-json"
	"github.com/rs/zerolog/log"
	"github.com/wailsapp/wails/v2/pkg/runtime"
)

var (
	headers = make(http.Header)
	mu      sync.Mutex
)

type Gateway struct {
	CloseChan         chan struct{}
	Closed            bool
	Config            *types.Config
	Connection        *websocket.Conn
	GatewayURL        string
	Handlers          Handlers
	LastSeq           int
	Selfbot           *Selfbot
	SessionID         string
	ClientBuildNumber string
	Ctx               context.Context

	heartbeatInterval time.Duration
}

func CreateGateway(ctx context.Context, selfbot *Selfbot, config *types.Config) *Gateway {
	mu.Lock()
	if len(headers) == 0 {
		headers.Set("Host", "gateway.discord.gg")
		headers.Set("User-Agent", config.UserAgent)
	}
	mu.Unlock()
	return &Gateway{CloseChan: make(chan struct{}), Selfbot: selfbot, GatewayURL: "wss://gateway.discord.gg/?encoding=json&v=" + config.ApiVersion, Config: config, ClientBuildNumber: clientBuildNumber, Ctx: ctx}
}

func (gateway *Gateway) Log(logType LogType, msg string) {
	runtime.EventsEmit(gateway.Ctx, "logDiscord", logType, gateway.Selfbot.User.Username, msg)
	switch logType {
	case Info:
		log.Info().Msg(fmt.Sprintf("%s %s", gateway.Selfbot.User.Username, msg))
	case Error:
		log.Error().Msg(fmt.Sprintf("%s %s", gateway.Selfbot.User.Username, msg))
	}
}

func (gateway *Gateway) Connect() error {
	conn, resp, err := websocket.DefaultDialer.Dial(gateway.GatewayURL, headers)

	if resp.StatusCode == 404 {
		return fmt.Errorf("gateway not found")
	} else if err != nil {
		return err
	}

	gateway.Closed = false
	gateway.Connection = conn

	if err = gateway.hello(); err != nil {
		return err
	}

	if err = gateway.identify(); err != nil {
		return err
	}

	if err = gateway.ready(); err != nil {
		return err
	}

	gateway.startHandler()
	return nil
}

func (gateway *Gateway) hello() error {
	msg, err := gateway.readMessage()

	if err != nil {
		return err
	}

	var resp types.HelloEvent

	if err = json.Unmarshal(msg, &resp); err != nil {
		return err
	}

	if resp.Op != types.OpcodeHello {
		return fmt.Errorf("unexpected opcode, expected %d, got %d", types.OpcodeHello, resp.Op)
	}

	gateway.heartbeatInterval = time.Duration(resp.D.HeartbeatInterval)
	go gateway.heartbeatSender()

	return nil
}

func (gateway *Gateway) identify() error {
	var err error
	var payload []byte

	if gateway.canReconnect() {
		payload, err = json.Marshal(types.ResumePayload{
			Op: types.OpcodeResume,
			D: types.ResumePayloadData{
				Token:     gateway.Selfbot.Token,
				SessionID: gateway.SessionID,
				Seq:       gateway.LastSeq,
			},
		})

		if err != nil {
			return err
		}

		err = gateway.sendMessage(payload)

		if err != nil {
			return err
		}

		payload := map[string]interface{}{
			"op": 3,
			"d": map[string]interface{}{
				"since":      0,
				"activities": []map[string]interface{}{},
				"status":     gateway.Config.Presence,
				"afk":        false,
			},
		}

		payloadJSON, err := json.Marshal(payload)
		if err != nil {
			return err
		}

		err = gateway.sendMessage(payloadJSON)
		if err != nil {
			gateway.Log("ERR", fmt.Sprintf("Error setting Discord status: %s", err.Error()))
		}
	} else {
		payload, err = json.Marshal(types.IdentifyPayload{
			Op: types.OpcodeIdentify,
			D: types.IdentifyPayloadData{
				Token:        gateway.Selfbot.Token,
				Capabilities: gateway.Config.Capabilities,
				Properties: types.SuperProperties{
					OS:                     gateway.Config.Os,
					Browser:                gateway.Config.Browser,
					Device:                 gateway.Config.Device,
					SystemLocale:           clientLocale,
					BrowserUserAgent:       gateway.Config.UserAgent,
					BrowserVersion:         gateway.Config.BrowserVersion,
					OSVersion:              gateway.Config.OsVersion,
					Referrer:               "",
					ReferringDomain:        "",
					ReferrerCurrent:        "",
					ReferringDomainCurrent: "",
					ReleaseChannel:         "stable",
					ClientBuildNumber:      clientBuildNumber,
					ClientEventSource:      nil,
				},
				Compress: false,
				ClientState: types.ClientState{
					GuildVersions:            types.GuildVersions{},
					HighestLastMessageID:     "0",
					ReadStateVersion:         0,
					UserGuildSettingsVersion: -1,
					UserSettingsVersion:      -1,
					PrivateChannelsVersion:   "0",
					APICodeVersion:           0,
				},
			},
		})

		if err != nil {
			return err
		}

		err = gateway.sendMessage(payload)
	}

	if err != nil {
		return err
	}

	return nil
}

func (gateway *Gateway) ready() error {
	msg, err := gateway.readMessage()

	if err != nil {
		return err
	}

	var event types.DefaultEvent
	err = json.Unmarshal(msg, &event)

	if err != nil {
		return err
	}

	if event.Op == types.OpcodeInvalidSession {
		<-gateway.CloseChan
		return gateway.reconnect()
	} else if event.Op != types.OpcodeDispatch {
		return fmt.Errorf("unexpected opcode, expected %d, got %d", types.OpcodeDispatch, event.Op)
	}

	var ready types.ReadyEvent

	if err = json.Unmarshal(msg, &ready); err != nil {
		return err
	}

	gateway.Selfbot.User = ready.D.User
	gateway.SessionID = ready.D.SessionID
	gateway.GatewayURL = ready.D.ResumeGatewayURL

	for _, handler := range gateway.Handlers.OnReady {
		handler(&ready.D)
	}

	return nil
}

func (gateway *Gateway) canReconnect() bool {
	return gateway.SessionID != "" && gateway.LastSeq != 0 && gateway.GatewayURL != ""
}

func (gateway *Gateway) heartbeatSender() {
	ticker := time.NewTicker(gateway.heartbeatInterval * time.Millisecond) // Every heartbeat interval (sent in milliseconds).
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C: // On ticker tick.
			if err := gateway.sendHeartbeat(); err != nil {
				return
			}
		case <-gateway.CloseChan: // If a close is signalled.
			return
		default:
			time.Sleep(25 * time.Millisecond) // Wait to prevent CPU overload.
		}
	}
}

func (gateway *Gateway) sendHeartbeat() error {
	payload, err := json.Marshal(types.DefaultEvent{
		Op: types.OpcodeHeartbeat,
		D:  4,
	})

	if err != nil {
		return err
	}

	return gateway.sendMessage(payload)

}
func (gateway *Gateway) sendMessage(payload []byte) error {
	err := gateway.Connection.WriteMessage(websocket.TextMessage, payload)

	if err != nil {
		var closeError *websocket.CloseError

		switch err := err.(type) {
		case *websocket.CloseError:
			closeError = err
		default:
			return err // assume close
		}

		switch closeError.Code {
		case websocket.CloseNormalClosure, websocket.CloseGoingAway, websocket.CloseNoStatusReceived:
			go gateway.reset()
			return err
		default:
			closeEvent, ok := types.CloseEventCodes[closeError.Code]

			if ok && closeEvent.Reconnect {
				go gateway.reconnect()
			}

			return fmt.Errorf("gateway closed with code %d: %s - %s", closeEvent.Code, closeEvent.Description, closeEvent.Explanation)
		}
	}
	return nil
}

func (gateway *Gateway) readMessage() ([]byte, error) {
	if gateway.Closed {
		return nil, errors.New("gateway connection is closed")
	}

	_, msg, err := gateway.Connection.ReadMessage()

	if err != nil {
		var closeError *websocket.CloseError

		switch err := err.(type) {
		case *websocket.CloseError:
			closeError = err
		default:
			return nil, err // assume close
		}

		switch closeError.Code {
		case websocket.CloseNormalClosure, websocket.CloseGoingAway, websocket.CloseNoStatusReceived: // Websocket closed without any close code.
			go gateway.reset()

			return nil, err
		default:
			if closeEvent, ok := types.CloseEventCodes[closeError.Code]; ok {
				if closeEvent.Reconnect { // If the session is re-connectable.
					go gateway.reconnect()
				} else {
					gateway.Close()

					return nil, fmt.Errorf("gateway closed with code %d: %s - %s", closeEvent.Code, closeEvent.Description, closeEvent.Explanation)
				}
			} else {
				gateway.Close()

				return nil, err
			}
		}
	}

	return msg, nil
}

func (gateway *Gateway) reset() error {
	gateway.LastSeq = 0
	gateway.SessionID = ""

	return gateway.reconnect()
}

func (gateway *Gateway) reconnect() error {
	return gateway.Connect()
}

func (gateway *Gateway) callHandlers(msg []byte, event types.DefaultEvent) error {
	switch event.Op {
	case types.OpcodeDispatch:

		switch event.T {
		case types.EventNameMessageCreate:
			var data types.MessageEvent
			err := json.Unmarshal(msg, &data)
			if err != nil {
				return err
			}
			for _, handler := range gateway.Handlers.OnMessageCreate {
				handler(&data.D)
			}
		case types.EventNameMessageUpdate:
			var data types.MessageEvent
			err := json.Unmarshal(msg, &data)
			if err != nil {
				return err
			}
			for _, handler := range gateway.Handlers.OnMessageUpdate {
				handler(&data.D)
			}
		case types.EventNameInteractionModalCreate:
			var modalData types.ModalEvent
			err := json.Unmarshal(msg, &modalData)
			if err != nil {
				return err
			}
			for _, handler := range gateway.Handlers.OnModalCreate {
				handler(&modalData.D)
			}
		}
	case types.OpcodeHeartbeat:
		gateway.sendHeartbeat()
	case types.OpcodeHeartbeatACK:

	case types.OpcodeReconnect:
		gateway.reconnect()

		for _, handler := range gateway.Handlers.OnReconnect {
			handler()
		}
	case types.OpcodeInvalidSession:
		gateway.reconnect()

		for _, handler := range gateway.Handlers.OnInvalidated {
			handler()
		}
	}

	return nil
}

func (gateway *Gateway) startHandler() {
	for {
		select {
		case <-gateway.CloseChan:
			return
		default:
			msg, err := gateway.readMessage()

			if err != nil {
				gateway.Log("ERR", fmt.Sprintf("Discord gateway: Error reading message: %v", err.Error()))

				if !gateway.Closed {
					gateway.Log("ERR", "Reconnecting to discord gateway")
					go gateway.reconnect()
				}
			}

			var event types.DefaultEvent

			if err = json.Unmarshal(msg, &event); err != nil {
				gateway.Log("ERR", fmt.Sprintf("Discord gateway: Error unmarshalling message: %v", err.Error()))
				continue
			}

			if err = gateway.callHandlers(msg, event); err != nil {
				gateway.Log("ERR", fmt.Sprintf("Discord gateway: Error calling handlers: %v", err.Error()))
				continue
			}

			if event.S == 0 { // Some payloads, for example the heartbeat ack, don't contribute to the sequence ID.
				gateway.LastSeq = event.S
			}
		}
	}
}

func (gateway *Gateway) Close() error {
	if gateway.Closed || gateway.Connection == nil {
		return errors.New("gateway connection is already closed")
	}

	gateway.Closed = true

	err := gateway.Connection.WriteControl(websocket.CloseMessage, websocket.FormatCloseMessage(websocket.CloseGoingAway, "going away"), time.Now().Add(time.Second*10))

	if err != nil {
		return err
	}

	gateway.CloseChan <- struct{}{}
	gateway.Connection.Close()
	gateway.Connection = nil

	return nil
}
