package instance

import (
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
)

func (in *Instance) SendChatMessage(content string, delay bool) error {
	if !in.Cfg.State || !in.AccountCfg.State {
		return nil
	}

	if delay {
		<-utils.Sleep(utils.RandSeconds(in.Cfg.Cooldowns.CommandInterval.MinSeconds, in.Cfg.Cooldowns.CommandInterval.MaxSeconds))
	}

	return in.Client.SendChatMessage(content)
}

func (in *Instance) SendCommand(name string, options map[string]string, delay bool) error {
	if !in.Cfg.State || !in.AccountCfg.State {
		return nil
	}

	if delay {
		<-utils.Sleep(utils.RandSeconds(in.Cfg.Cooldowns.CommandInterval.MinSeconds, in.Cfg.Cooldowns.CommandInterval.MaxSeconds))
	}

	return in.Client.SendCommand(name, options)
}

func (in *Instance) SendSubCommand(name string, subCommandName string, options map[string]string, delay bool) error {
	if !in.Cfg.State || !in.AccountCfg.State {
		return nil
	}

	if delay {
		<-utils.Sleep(utils.RandSeconds(in.Cfg.Cooldowns.CommandInterval.MinSeconds, in.Cfg.Cooldowns.CommandInterval.MaxSeconds))
	}

	return in.Client.SendSubCommand(name, subCommandName, options)
}

func (in *Instance) ClickButton(message gateway.EventMessage, row int, column int) error {
	if !in.Cfg.State || !in.AccountCfg.State {
		return nil
	}

	<-utils.Sleep(utils.RandSeconds(in.Cfg.Cooldowns.ButtonClickDelay.MinSeconds, in.Cfg.Cooldowns.ButtonClickDelay.MaxSeconds))

	err := in.Client.ClickButton(message, row, column)
	if err != nil {
		return err
	} else {
		return nil
	}
}

func (in *Instance) ClickDmButton(message gateway.EventMessage, row int, column int) error {
	if !in.Cfg.State || !in.AccountCfg.State {
		return nil
	}

	<-utils.Sleep(utils.RandSeconds(in.Cfg.Cooldowns.ButtonClickDelay.MinSeconds, in.Cfg.Cooldowns.ButtonClickDelay.MaxSeconds))
	return in.Client.ClickDmButton(message, row, column)
}

func (in *Instance) ChooseSelectMenu(message gateway.EventMessage, row int, column int, values []string) error {
	if !in.Cfg.State || !in.AccountCfg.State {
		return nil
	}

	<-utils.Sleep(utils.RandSeconds(in.Cfg.Cooldowns.ButtonClickDelay.MinSeconds, in.Cfg.Cooldowns.ButtonClickDelay.MaxSeconds))
	return in.Client.ChooseSelectMenu(message, row, column, values)
}

func (in *Instance) SubmitModal(modal gateway.EventModalCreate) error {
	if !in.Cfg.State || !in.AccountCfg.State {
		return nil
	}

	<-utils.Sleep(utils.RandSeconds(in.Cfg.Cooldowns.ButtonClickDelay.MinSeconds, in.Cfg.Cooldowns.ButtonClickDelay.MaxSeconds))
	return in.Client.SubmitModal(modal)
}
