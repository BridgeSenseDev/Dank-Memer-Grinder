package discord

import (
	"context"
	"errors"
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
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
	GatewayParams     string

	heartbeatInterval time.Duration
	reconnectAttempts int
}

func CreateGateway(ctx context.Context, selfbot *Selfbot, config *types.Config) *Gateway {
	mu.Lock()
	if len(headers) == 0 {
		headers.Set("Host", "gateway.discord.gg")
		headers.Set("User-Agent", config.UserAgent)
	}
	mu.Unlock()
	return &Gateway{CloseChan: make(chan struct{}), Selfbot: selfbot, GatewayURL: "wss://gateway.discord.gg", Config: config, ClientBuildNumber: clientBuildNumber, Ctx: ctx, GatewayParams: "/?encoding=json&v=" + config.ApiVersion, reconnectAttempts: 0}
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
	conn, resp, err := websocket.DefaultDialer.Dial(gateway.GatewayURL+gateway.GatewayParams, headers)

	if err != nil {
		return err
	}

	if resp.StatusCode == 404 {
		return fmt.Errorf("gateway not found")
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

	gateway.Log("INF", "Connected to gateway")

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
	payload, err := json.Marshal(types.IdentifyPayload{
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
		err := gateway.reset()
		if err != nil {
			return err
		}
	} else if event.Op != types.OpcodeDispatch {
		return fmt.Errorf("unexpected opcode, expected %d, got %d", types.OpcodeDispatch, event.Op)
	}

	var ready types.ReadyEvent

	if err = json.Unmarshal(msg, &ready); err != nil {
		return err
	}

	gateway.Selfbot.User = ready.D.User
	gateway.SessionID = ready.D.SessionID
	gateway.GatewayURL = ready.D.ResumeGatewayURL + gateway.GatewayParams
	gateway.reconnectAttempts = 0

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
			gateway.Log("ERR", fmt.Sprintf("Resetting discord gateway: %s", closeError.Error()))
			err := gateway.reset()
			if err != nil {
				gateway.Log("ERR", fmt.Sprintf("Error resetting discord gateway: %s", err.Error()))
			}
			return err
		default:
			closeEvent, ok := types.CloseEventCodes[closeError.Code]

			if ok && closeEvent.Reconnect {
				gateway.Log("ERR", "Attempting a reconnect")
				err := gateway.reconnect()
				if err != nil {
					gateway.Log("ERR", fmt.Sprintf("Failed to reconnect to gateway: %s", err.Error()))
				}
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
		if errors.As(err, &closeError) {
			switch closeError.Code {
			case websocket.CloseNormalClosure, websocket.CloseGoingAway, websocket.CloseNoStatusReceived: // Websocket closed without any close code.
				gateway.Log("ERR", fmt.Sprintf("Resetting discord gateway: %s", closeError.Error()))
				err := gateway.reset()
				if err != nil {
					gateway.Log("ERR", fmt.Sprintf("Error resetting discord gateway: %s", err.Error()))
				}

				return nil, err
			default:
				if closeEvent, ok := types.CloseEventCodes[closeError.Code]; ok {
					if closeEvent.Reconnect { // If the session is re-connectable.
						gateway.Log("ERR", "Attempting a reconnect")
						err := gateway.reconnect()
						if err != nil {
							gateway.Log("ERR", fmt.Sprintf("Failed to reconnect to gateway: %s", err.Error()))
						}
					} else {
						err := gateway.Close()
						if err != nil {
							return nil, err
						}

						return nil, fmt.Errorf("gateway closed with code %d: %s - %s", closeEvent.Code, closeEvent.Description, closeEvent.Explanation)
					}
				} else {
					err := gateway.Close()
					if err != nil {
						return nil, err
					}

					return nil, err
				}
			}
		} else {
			// Handle the case where err is not a *websocket.CloseError
			return nil, err
		}
	}

	return msg, nil
}

func (gateway *Gateway) reset() error {
	err := gateway.Close()
	if err != nil {
		gateway.Log("ERR", fmt.Sprintf("Failed to close gateway: %s", err.Error()))
	}
	gateway.LastSeq = 0
	gateway.SessionID = ""
	gateway.GatewayURL = "wss://gateway.discord.gg"

	return gateway.Connect()
}

func (gateway *Gateway) reconnect() error {
	conn, resp, err := websocket.DefaultDialer.Dial(gateway.GatewayURL, headers)

	if err != nil {
		return err
	}

	if resp.StatusCode == 404 {
		return fmt.Errorf("gateway not found")
	}

	gateway.Closed = false
	gateway.Connection = conn

	payload, err := json.Marshal(types.ResumePayload{
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

	if err = gateway.hello(); err != nil {
		return err
	}

	return nil
}

func (gateway *Gateway) callHandlers(msg []byte, event types.DefaultEvent) error {
	switch event.Op {
	case types.OpcodeDispatch:

		switch event.T {
		case types.EventNameResumed:
			gateway.reconnectAttempts = 0
			gateway.Log("INF", "Successfully resumed discord gateway")
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
		err := gateway.sendHeartbeat()
		if err != nil {
			return err
		}
	case types.OpcodeHeartbeatACK:

	case types.OpcodeReconnect:
		err := gateway.reconnect()
		if err != nil {
			return err
		}

		for _, handler := range gateway.Handlers.OnReconnect {
			handler()
		}
	case types.OpcodeInvalidSession:
		err := gateway.reset()
		if err != nil {
			return err
		}

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
				if !gateway.Closed {
					delay := utils.ExponentialBackoff(gateway.reconnectAttempts)
					gateway.reconnectAttempts++
					gateway.Log("ERR", fmt.Sprintf("Attempting a reconnect in %ds: %s", delay/time.Second, err.Error()))
					time.Sleep(delay)

					err := gateway.reconnect()

					if err != nil {
						gateway.Log("ERR", fmt.Sprintf("Failed to reconnect to gateway: %s", err.Error()))
					} else {
						gateway.Log("INF", "Sent resume request to gateway")
					}
					continue
				}
			}

			var event types.DefaultEvent

			if err = json.Unmarshal(msg, &event); err != nil {
				if !gateway.Closed {
					delay := utils.ExponentialBackoff(gateway.reconnectAttempts)
					gateway.reconnectAttempts++
					gateway.Log("ERR", fmt.Sprintf("Attempting a reconnect in %ds: %s", delay/time.Second, err.Error()))
					time.Sleep(delay)

					err := gateway.reconnect()

					if err != nil {
						gateway.Log("ERR", fmt.Sprintf("Failed to reconnect to gateway: %s", err.Error()))
					} else {
						gateway.Log("INF", "Sent resume request to gateway")
					}
					continue
				}
			}

			if event.S != 0 { // Some payloads, for example the heartbeat ack, don't contribute to the sequence ID.
				gateway.LastSeq = event.S
			}

			if err = gateway.callHandlers(msg, event); err != nil {
				gateway.Log("ERR", fmt.Sprintf("Discord gateway: Error calling handlers: %v", err.Error()))
				continue
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
	err = gateway.Connection.Close()
	if err != nil {
		return err
	}
	gateway.Connection = nil

	return nil
}
