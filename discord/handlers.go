package discord

import (
	"errors"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"sync"
)

type Handlers struct {
	OnReady         []func(data gateway.EventReady)
	OnMessageCreate []func(data gateway.EventMessage)
	OnMessageUpdate []func(data gateway.EventMessage)
	OnModalCreate   []func(data gateway.EventModalCreate)
	mutex           sync.Mutex
}

func (handlers *Handlers) Add(event gateway.EventType, function any) error {
	handlers.mutex.Lock()
	defer handlers.mutex.Unlock()

	failed := false
	switch event {
	case gateway.EventTypeReady:
		if function, ok := function.(func(data gateway.EventReady)); ok {
			handlers.OnReady = append(handlers.OnReady, function)
		} else {
			failed = true
		}
	case gateway.EventTypeMessageCreate:
		if function, ok := function.(func(data gateway.EventMessage)); ok {
			handlers.OnMessageCreate = append(handlers.OnMessageCreate, function)
		} else {
			failed = true
		}
	case gateway.EventTypeMessageUpdate:
		if function, ok := function.(func(data gateway.EventMessage)); ok {
			handlers.OnMessageUpdate = append(handlers.OnMessageUpdate, function)
		} else {
			failed = true
		}
	case gateway.EventTypeModalCreate:
		if function, ok := function.(func(data gateway.EventModalCreate)); ok {
			handlers.OnModalCreate = append(handlers.OnModalCreate, function)
		} else {
			failed = true
		}
	default:
		return errors.New("failed to match event to gateway event")
	}

	if failed {
		return errors.New("function signature was not correct for the specified event")
	}

	return nil
}
