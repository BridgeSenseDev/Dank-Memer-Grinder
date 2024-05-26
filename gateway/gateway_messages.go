package gateway

import (
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"

	"github.com/goccy/go-json"
)

// Message raw Message type
type Message struct {
	Op   Opcode          `json:"op"`
	S    int             `json:"s,omitempty"`
	T    EventType       `json:"t,omitempty"`
	D    MessageData     `json:"d,omitempty"`
	RawD json.RawMessage `json:"-"`
}

func (e *Message) UnmarshalJSON(data []byte) error {
	var v struct {
		Op Opcode          `json:"op"`
		S  int             `json:"s,omitempty"`
		T  EventType       `json:"t,omitempty"`
		D  json.RawMessage `json:"d,omitempty"`
	}
	if err := json.Unmarshal(data, &v); err != nil {
		return err
	}

	var (
		messageData MessageData
		err         error
	)

	switch v.Op {
	case OpcodeDispatch:
		messageData, err = UnmarshalEventData(v.D, v.T)

	case OpcodeHeartbeat:
		var d MessageDataHeartbeat
		err = json.Unmarshal(v.D, &d)
		messageData = d

	case OpcodeIdentify:
		var d MessageDataIdentify
		err = json.Unmarshal(v.D, &d)
		messageData = d

	case OpcodePresenceUpdate:
		var d MessageDataPresenceUpdate
		err = json.Unmarshal(v.D, &d)
		messageData = d

	case OpcodeResume:
		var d MessageDataResume
		err = json.Unmarshal(v.D, &d)
		messageData = d

	case OpcodeReconnect:

	case OpcodeInvalidSession:
		var d MessageDataInvalidSession
		err = json.Unmarshal(v.D, &d)
		messageData = d

	case OpcodeHello:
		var d MessageDataHello
		err = json.Unmarshal(v.D, &d)
		messageData = d

	case OpcodeHeartbeatACK:

	default:
		var d MessageDataUnknown
		err = json.Unmarshal(v.D, &d)
		messageData = d
	}
	if err != nil {
		return fmt.Errorf("failed to unmarshal message data: %s: %w", string(data), err)
	}
	e.Op = v.Op
	e.S = v.S
	e.T = v.T
	e.D = messageData
	e.RawD = v.D
	return nil
}

type MessageData interface {
	messageData()
}

func UnmarshalEventData(data []byte, eventType EventType) (EventData, error) {
	var (
		eventData EventData
		err       error
	)
	switch eventType {
	case EventTypeReady:
		var d EventReady
		err = json.Unmarshal(data, &d)
		eventData = d

	case EventTypeResumed:
		// no data

	case EventTypeMessageCreate:
		var d EventMessage
		err = json.Unmarshal(data, &d)
		eventData = d

	case EventTypeMessageUpdate:
		var d EventMessage
		err = json.Unmarshal(data, &d)
		eventData = d

	case EventTypeModalCreate:
		var d EventModalCreate
		err = json.Unmarshal(data, &d)
		eventData = d

	default:
		var d EventUnknown
		err = json.Unmarshal(data, &d)
		eventData = d
	}

	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal event data: %s: %w", string(data), err)
	}

	return eventData, nil
}

type MessageDataUnknown json.RawMessage

func (MessageDataUnknown) messageData() {}

// MessageDataHeartbeat is used to ensure the websocket connection remains open, and disconnect if not.
type MessageDataHeartbeat int

func (MessageDataHeartbeat) messageData() {}

// MessageDataIdentify is the data used in IdentifyCommandData
type MessageDataIdentify struct {
	Capabilities int64                         `json:"capabilities"`
	Token        string                        `json:"token"`
	Properties   IdentifyCommandDataProperties `json:"properties"`
	ClientState  ClientState                   `json:"client_state"`
	Compress     bool                          `json:"compress,omitempty"`
	Presence     *MessageDataPresenceUpdate    `json:"presence,omitempty"`
}

func (MessageDataIdentify) messageData() {}

type ClientState struct {
	GuildVersions struct{} `json:"guild_versions"`
}

// IdentifyCommandDataProperties is used for specifying to discord which library and OS the bot is using, is
// automatically handled by the library and should rarely be used.
type IdentifyCommandDataProperties struct {
	Browser           string `json:"browser"`
	BrowserUserAgent  string `json:"browser_user_agent"`
	BrowserVersion    string `json:"browser_version"`
	ClientBuildNumber string `json:"client_build_number"`
	DesignID          int    `json:"design_id"`
	OS                string `json:"os"`
	OSVersion         string `json:"os_version"`
	ReleaseChannel    string `json:"release_channel"`
	Device            string `json:"device"`
	SystemLocale      string `json:"system_locale"`
}

// MessageDataPresenceUpdate is used for updating Client's presence
type MessageDataPresenceUpdate struct {
	Since      *int64                   `json:"since"`
	Activities []map[string]interface{} `json:"activities"`
	Status     types.OnlineStatus       `json:"status"`
	AFK        bool                     `json:"afk"`
}

func (MessageDataPresenceUpdate) messageData() {}

// MessageDataResume is used to resume a connection to discord in the case that you are disconnected. Is automatically
// handled by the library and should rarely be used.
type MessageDataResume struct {
	Token     string `json:"token"`
	SessionID string `json:"session_id"`
	Seq       int    `json:"seq"`
}

func (MessageDataResume) messageData() {}

type MessageDataInvalidSession bool

func (MessageDataInvalidSession) messageData() {}

type MessageDataHello struct {
	HeartbeatInterval int `json:"heartbeat_interval"`
}

func (MessageDataHello) messageData() {}
