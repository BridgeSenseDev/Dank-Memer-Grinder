package main

import (
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"sync"
	"time"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/config"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/instance"
	"github.com/rs/zerolog/log"
	"github.com/wailsapp/wails/v2/pkg/runtime"
)

type InstanceView struct {
	User       *types.User           `json:"user"`
	ChannelID  string                `json:"channelID"`
	GuildID    string                `json:"guildID"`
	Cfg        config.Config         `json:"config"`
	AccountCfg config.AccountsConfig `json:"accountCfg"`
	LastRan    map[string]time.Time  `json:"lastRan"`
	Pause      bool                  `json:"pause"`
	Error      string                `json:"error,omitempty"`
}

func (a *App) StartInstance(account config.AccountsConfig) {
	a.wg.Add(1)
	go func() {
		defer a.wg.Done()
		client := discord.NewClient(a.ctx, account.Token)

		var readyOnce sync.Once
		client.AddHandler(gateway.EventTypeReady, func(e gateway.EventReady) {
			readyOnce.Do(func() {
				client.ChannelID = account.ChannelID
				client.GuildID = client.GetGuildID(account.ChannelID)
				if client.GuildID == "" {
					log.Error().Msgf("Failed to fetch GuildID from channelID: %v", account.ChannelID)
					in := &instance.Instance{
						AccountCfg: account,
						Error:      "invalidChannelID",
					}
					a.instances = append(a.instances, in)
					runtime.EventsEmit(a.ctx, "instancesUpdate", a.GetInstances())
					return
				}

				commands, err := client.GetCommands(client.GuildID)
				if err != nil {
					client.Log("ERR", fmt.Sprintf("Failed to get commands: %s", err.Error()))
				}

				commandDataSlice := make([]discord.CommandData, 0, len(commands))
				for _, cmd := range commands {
					commandDataSlice = append(commandDataSlice, cmd)
				}

				client.CommandsData = &commandDataSlice

				in := &instance.Instance{
					User:       client.Gateway.User(),
					Client:     client,
					ChannelID:  account.ChannelID,
					GuildID:    client.GetGuildID(account.ChannelID),
					Cfg:        *a.cfg,
					AccountCfg: account,
					LastRan:    make(map[string]time.Time),
					Pause:      false,
					StopChan:   make(chan struct{}),
					Error:      "healthy",
					Ctx:        a.ctx,
				}

				a.instances = append(a.instances, in)
				runtime.EventsEmit(a.ctx, "instancesUpdate", a.GetInstances())

				a.UpdateDiscordStatus(a.cfg.DiscordStatus)

				err = in.Start()
				if err != nil {
					return
				}
				in.Log("important", "INF", fmt.Sprintf("Logged in as %s", e.User.Username))
			})
		})

		err := client.Connect()
		if err != nil {
			log.Error().Msgf("Failed to connect: %v", err.Error())
			in := &instance.Instance{
				AccountCfg: account,
				Error:      "invalidToken",
			}

			a.instances = append(a.instances, in)
			runtime.EventsEmit(a.ctx, "instancesUpdate", a.GetInstances())
		}
	}()
}

func (a *App) RemoveInstance(token string) {
	var wg sync.WaitGroup
	instancesToKeep := make([]*instance.Instance, 0, len(a.instances))

	for _, in := range a.instances {
		if in.AccountCfg.Token != token {
			instancesToKeep = append(instancesToKeep, in)
		} else if in.Error == "healthy" {
			wg.Add(1)
			go func(in *instance.Instance) {
				defer wg.Done()
				in.Stop()
			}(in)
		}
	}

	wg.Wait()
	a.instances = instancesToKeep
}

func (a *App) RestartInstance(token string) {
	a.RemoveInstance(token)

	var accountToRestart config.AccountsConfig
	for _, account := range a.cfg.Accounts {
		if account.Token == token {
			accountToRestart = account
			break
		}
	}

	if accountToRestart.Token != "" {
		a.StartInstance(accountToRestart)
	} else {
		log.Warn().Msgf("No account found with token %s", token)
	}
}

func (a *App) processAccounts(accounts []config.AccountsConfig, action func(config.AccountsConfig)) {
	for _, account := range accounts {
		action(account)
	}
}

func (a *App) StartInstances() {
	a.instances = make([]*instance.Instance, 0)
	a.processAccounts(a.cfg.Accounts, a.StartInstance)
}

func (a *App) RestartInstances() {
	a.processAccounts(a.cfg.Accounts, func(account config.AccountsConfig) {
		a.RemoveInstance(account.Token)
		a.StartInstance(account)
	})
}

func (a *App) GetInstances() []*InstanceView {
	if len(a.instances) == 0 {
		return []*InstanceView{}
	}

	for len(a.instances) != len(a.cfg.Accounts) {
		time.Sleep(100 * time.Millisecond)
	}

	var instanceViews []*InstanceView

	for _, i := range a.instances {
		instanceView := &InstanceView{
			User:       i.User,
			ChannelID:  i.ChannelID,
			GuildID:    i.GuildID,
			Cfg:        i.Cfg,
			AccountCfg: i.AccountCfg,
			LastRan:    i.LastRan,
			Pause:      i.Pause,
			Error:      i.Error,
		}
		instanceViews = append(instanceViews, instanceView)
	}

	return instanceViews
}
