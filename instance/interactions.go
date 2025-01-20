package instance

import (
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"math/rand"
	"time"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
)

func (in *Instance) SendCommand(name string, options map[string]string, delay bool) error {
	if delay {
		minDelay := in.Cfg.Cooldowns.CommandInterval.MinDelay
		maxDelay := in.Cfg.Cooldowns.CommandInterval.MaxDelay
		<-utils.Sleep(time.Duration(rand.Intn(maxDelay-minDelay)+minDelay) * time.Millisecond)
	}

	return in.Client.SendCommand(name, options)
}

func (in *Instance) SendSubCommand(name string, subCommandName string, options map[string]string, delay bool) error {
	if delay {
		minDelay := in.Cfg.Cooldowns.CommandInterval.MinDelay
		maxDelay := in.Cfg.Cooldowns.CommandInterval.MaxDelay
		<-utils.Sleep(time.Duration(rand.Intn(maxDelay-minDelay)+minDelay) * time.Millisecond)
	}

	return in.Client.SendSubCommand(name, subCommandName, options)
}

func (in *Instance) ClickButton(message gateway.EventMessage, row int, column int) error {
	minDelay := in.Cfg.Cooldowns.ButtonClickDelay.MinDelay
	maxDelay := in.Cfg.Cooldowns.ButtonClickDelay.MaxDelay
	<-utils.Sleep(time.Duration(rand.Intn(maxDelay-minDelay)+minDelay) * time.Millisecond)

	err := in.Client.ClickButton(message, row, column)
	if err != nil {
		for attempt := 0; attempt < 5; attempt++ {
			backoff := time.Duration(1<<attempt) * time.Second
			utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Attempt %d to click button, waiting %v", attempt+1, backoff))
			time.Sleep(backoff)
			err = in.Client.ClickButton(message, row, column)
			if err == nil {
				return nil
			}
		}
		return err
	} else {
		return nil
	}
}

func (in *Instance) ClickDmButton(message gateway.EventMessage, row int, column int) error {
	minDelay := in.Cfg.Cooldowns.ButtonClickDelay.MinDelay
	maxDelay := in.Cfg.Cooldowns.ButtonClickDelay.MaxDelay
	<-utils.Sleep(time.Duration(rand.Intn(maxDelay-minDelay)+minDelay) * time.Millisecond)
	return in.Client.ClickDmButton(message, row, column)
}

func (in *Instance) ChooseSelectMenu(message gateway.EventMessage, row int, column int, values []string) error {
	minDelay := in.Cfg.Cooldowns.ButtonClickDelay.MinDelay
	maxDelay := in.Cfg.Cooldowns.ButtonClickDelay.MaxDelay
	<-utils.Sleep(time.Duration(rand.Intn(maxDelay-minDelay)+minDelay) * time.Millisecond)
	return in.Client.ChooseSelectMenu(message, row, column, values)
}

func (in *Instance) SubmitModal(modal gateway.EventModalCreate) error {
	minDelay := in.Cfg.Cooldowns.ButtonClickDelay.MinDelay
	maxDelay := in.Cfg.Cooldowns.ButtonClickDelay.MaxDelay
	<-utils.Sleep(time.Duration(rand.Intn(maxDelay-minDelay)+minDelay) * time.Millisecond)
	return in.Client.SubmitModal(modal)
}
