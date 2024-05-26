package gateway

// EventType wraps all EventType types
type EventType string

// Constants for the gateway events
const (
	EventTypeReady         EventType = "READY"
	EventTypeResumed       EventType = "RESUMED"
	EventTypeMessageCreate EventType = "MESSAGE_CREATE"
	EventTypeMessageUpdate EventType = "MESSAGE_UPDATE"
	EventTypeModalCreate   EventType = "INTERACTION_MODAL_CREATE"
)
