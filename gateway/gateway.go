package gateway

import (
	"context"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"time"
)

// Version defines which discord API version should be used to connect to discord.
const Version = 9

// Status is the state that the client is currently in.
type Status int

// IsConnected returns whether the Gateway is connected.
func (s Status) IsConnected() bool {
	switch s {
	case StatusWaitingForHello, StatusIdentifying, StatusWaitingForReady, StatusReady:
		return true
	default:
		return false
	}
}

// Indicates how far along the client is too connecting.
const (
	// StatusUnconnected is the initial state when a new Gateway is created.
	StatusUnconnected Status = iota

	// StatusConnecting is the state when the client is connecting to the Discord gateway.
	StatusConnecting

	// StatusWaitingForHello is the state when the Gateway is waiting for the first OpcodeHello packet.
	StatusWaitingForHello

	// StatusIdentifying is the state when the Gateway received its first OpcodeHello packet and now sends a OpcodeIdentify packet.
	StatusIdentifying

	// StatusResuming is the state when the Gateway received its first OpcodeHello packet and now sends a OpcodeResume packet.
	StatusResuming

	// StatusWaitingForReady is the state when the Gateway received sent a OpcodeIdentify or OpcodeResume packet and now waits for a OpcodeDispatch with EventTypeReady packet.
	StatusWaitingForReady

	// StatusReady is the state when the Gateway received a OpcodeDispatch with EventTypeReady packet.
	StatusReady

	// StatusDisconnected is the state when the Gateway is disconnected.
	// Either due to an error or because the Gateway was closed gracefully.
	StatusDisconnected

	// StatusInvalidToken is the state when the Gateway is disconnected due to an invalid token.
	StatusInvalidToken
)

type (
	// CreateFunc is a type that is used to create a new Gateway(s).
	CreateFunc func(token string) Gateway
)

type (
	// EventHandlerFunc is a function that is called when an event is received.
	EventHandlerFunc func(gatewayEventType EventType, event EventData)
)

// Gateway is what is used to connect to discord.
type Gateway interface {
	// SessionID returns the session ID that is used by this Gateway.
	// This may be nil if the Gateway was never connected to Discord, was gracefully closed with websocket.CloseNormalClosure or websocket.CloseGoingAway.
	SessionID() *string

	User() *types.User

	UserAgent() string

	// LastSequenceReceived returns the last sequence number that was received by the Gateway.
	// This may be nil if the Gateway was never connected to Discord, was gracefully closed with websocket.CloseNormalClosure or websocket.CloseGoingAway.
	LastSequenceReceived() *int

	// Open connects this Gateway to the Discord API.
	Open(ctx context.Context) error

	// Close gracefully closes the Gateway with the websocket.CloseNormalClosure code.
	// If the context is done, the Gateway connection will be killed.
	Close(ctx context.Context)

	// CloseWithCode closes the Gateway with the given code & message.
	// If the context is done, the Gateway connection will be killed.
	CloseWithCode(ctx context.Context, code int, message string)

	// Send sends a message to the Discord gateway with the opCode and data.
	// If context is deadline exceeds, the message sending will be aborted.
	Send(ctx context.Context, op Opcode, data MessageData) error

	// Latency returns the latency of the Gateway.
	// This is calculated by the time it takes to send a heartbeat and receive a heartbeat ack by discord.
	Latency() time.Duration

	// Presence returns the current presence of the Gateway.
	Presence() *MessageDataPresenceUpdate

	// StatusUpdates returns a channel that will be updated with the status of the gateway.
	StatusUpdates() <-chan Status

	// SafeGetUsername returns the username of the gateway if it is not nil, otherwise it returns the token
	SafeGetUsername() string
}
