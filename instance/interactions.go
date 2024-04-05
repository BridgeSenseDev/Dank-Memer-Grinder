package instance

import (
	"math/rand"
	"time"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
)

func (in *Instance) SendCommand(name string, options map[string]string) error {
	minDelay := in.Cfg.Cooldowns.CommandInterval.MinDelay
	maxDelay := in.Cfg.Cooldowns.CommandInterval.MaxDelay
	<-utils.Sleep(time.Duration(rand.Intn(maxDelay-minDelay)+minDelay) * time.Millisecond)
	return in.Client.SendCommand(name, options)
}

func (in *Instance) SendSubCommand(name string, subCommandName string, options map[string]string) error {
	minDelay := in.Cfg.Cooldowns.CommandInterval.MinDelay
	maxDelay := in.Cfg.Cooldowns.CommandInterval.MaxDelay
	<-utils.Sleep(time.Duration(rand.Intn(maxDelay-minDelay)+minDelay) * time.Millisecond)
	return in.Client.SendSubCommand(name, subCommandName, options)
}

func (in *Instance) ClickButton(message types.MessageData, row int, column int) error {
	minDelay := in.Cfg.Cooldowns.ButtonClickDelay.MinDelay
	maxDelay := in.Cfg.Cooldowns.ButtonClickDelay.MaxDelay
	<-utils.Sleep(time.Duration(rand.Intn(maxDelay-minDelay)+minDelay) * time.Millisecond)
	return in.Client.ClickButton(message, row, column)
}

func (in *Instance) ChooseSelectMenu(message types.MessageData, row int, column int, values []string) error {
	minDelay := in.Cfg.Cooldowns.ButtonClickDelay.MinDelay
	maxDelay := in.Cfg.Cooldowns.ButtonClickDelay.MaxDelay
	<-utils.Sleep(time.Duration(rand.Intn(maxDelay-minDelay)+minDelay) * time.Millisecond)
	return in.Client.ChooseSelectMenu(message, row, column, values)
}

func (in *Instance) SubmitModal(modal types.ModalData) error {
	minDelay := in.Cfg.Cooldowns.ButtonClickDelay.MinDelay
	maxDelay := in.Cfg.Cooldowns.ButtonClickDelay.MaxDelay
	<-utils.Sleep(time.Duration(rand.Intn(maxDelay-minDelay)+minDelay) * time.Millisecond)
	return in.Client.SubmitModal(modal)
}
