package gateway

import (
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/goccy/go-json"
	"io"
)

type EventData interface {
	MessageData
	eventData()
}

// EventUnknown is an event that is not known
type EventUnknown json.RawMessage

func (e EventUnknown) MarshalJSON() ([]byte, error) {
	return json.RawMessage(e).MarshalJSON()
}

func (e *EventUnknown) UnmarshalJSON(data []byte) error {
	return (*json.RawMessage)(e).UnmarshalJSON(data)
}

func (EventUnknown) messageData() {}
func (EventUnknown) eventData()   {}

// EventReady is the event sent by discord when you successfully Identify
type EventReady struct {
	types.ReadyEventData
}

func (EventReady) messageData() {}
func (EventReady) eventData()   {}

type EventMessage struct {
	types.MessageData
}

func (EventMessage) messageData() {}
func (EventMessage) eventData()   {}

type EventModalCreate struct {
	types.ModalData
}

func (EventModalCreate) messageData() {}
func (EventModalCreate) eventData()   {}

type EventRaw struct {
	EventType EventType
	Payload   io.Reader
}

func (EventRaw) messageData() {}
func (EventRaw) eventData()   {}
