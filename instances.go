package main

import (
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
	"sync"
	"time"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/config"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/instance"
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

func (d *DmgService) StartInstance(account config.AccountsConfig) {
	d.wg.Add(1)
	go func() {
		defer d.wg.Done()
		client := discord.NewClient(d.ctx, account.Token)

		var readyOnce sync.Once
		client.AddHandler(gateway.EventTypeReady, func(e gateway.EventReady) {
			readyOnce.Do(func() {
				client.ChannelID = account.ChannelID
				guildID, err := client.GetGuildID(account.ChannelID)
				if err != nil {
					utils.Log(utils.Discord, utils.Error, client.SafeGetUsername(), fmt.Sprintf("Failed to fetch GuildID from channelID %v: %s", account.ChannelID, err.Error()))
					in := &instance.Instance{
						AccountCfg: account,
						Error:      "invalidChannelID",
					}
					d.instances = append(d.instances, in)
					utils.EmitEventIfNotCLI("instancesUpdate", d.GetInstances())
					return
				}
				client.GuildID = guildID

				err = client.Gateway.Send(d.ctx, gateway.GUILD_SUBSCRIPTIONS_BULK, gateway.MessageDataGuildSubscriptionsBulk{
					Subscriptions: map[string]gateway.GuildSubscription{
						client.GuildID: {
							Typing:            true,
							Threads:           false,
							Activities:        false,
							Members:           []int64{},
							MemberUpdates:     false,
							Channels:          map[string][][2]int{},
							ThreadMemberLists: []int64{},
						},
					},
				})
				if err != nil {
					utils.Log(utils.Important, utils.Error, client.SafeGetUsername(), fmt.Sprintf("Failed to send guild subscriptions bulk: %s", err.Error()))
				}

				commands, err := client.GetCommands(client.GuildID)
				if err != nil {
					utils.Log(utils.Discord, utils.Error, client.SafeGetUsername(), fmt.Sprintf("Failed to get commands: %s", err.Error()))
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
					GuildID:    client.GuildID,
					Cfg:        *d.cfg,
					AccountCfg: account,
					LastRan:    make(map[string]time.Time),
					StopChan:   make(chan struct{}),
					Error:      "healthy",
					Ctx:        d.ctx,
				}

				d.instances = append(d.instances, in)
				utils.EmitEventIfNotCLI("instancesUpdate", d.GetInstances())

				d.UpdateDiscordStatus(d.cfg.DiscordStatus)

				err = in.Start()
				if err != nil {
					return
				}
				utils.Log(utils.Important, utils.Info, in.SafeGetUsername(), fmt.Sprintf("Logged in as %s", e.User.Username))
			})
		})

		err := client.Connect()

		if err != nil {
			utils.Log(utils.Important, utils.Error, "", fmt.Sprintf("Failed to connect: %v", err.Error()))
			in := &instance.Instance{
				AccountCfg: account,
				Error:      "invalidToken",
			}

			d.instances = append(d.instances, in)
			utils.EmitEventIfNotCLI("instancesUpdate", d.GetInstances())
		}

		statusChan := client.Gateway.StatusUpdates()

		for {
			select {
			case status := <-statusChan:
				switch status {
				case gateway.StatusInvalidToken:
					in := &instance.Instance{
						AccountCfg: account,
						Error:      "invalidToken",
					}

					d.instances = append(d.instances, in)
					utils.EmitEventIfNotCLI("instancesUpdate", d.GetInstances())
					break
				default:
				}
			case <-d.ctx.Done():
				client.Close()
				return
			}
		}
	}()

	time.Sleep(5 * time.Second)
}

func (d *DmgService) RemoveInstance(token string) {
	var wg sync.WaitGroup
	instancesToKeep := make([]*instance.Instance, 0, len(d.instances))

	for _, in := range d.instances {
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
	d.instances = instancesToKeep
	utils.EmitEventIfNotCLI("instancesUpdate", d.GetInstances())
}

func (d *DmgService) RestartInstance(token string) {
	d.RemoveInstance(token)

	var accountToRestart config.AccountsConfig
	for _, account := range d.cfg.Accounts {
		if account.Token == token {
			accountToRestart = account
			break
		}
	}

	if accountToRestart.Token != "" {
		d.StartInstance(accountToRestart)
	} else {
		utils.Log(utils.Important, utils.Error, "", fmt.Sprintf("No account found with token %s", token))
	}
}

func (d *DmgService) processAccounts(accounts []config.AccountsConfig, action func(config.AccountsConfig)) {
	for _, account := range accounts {
		action(account)
	}
}

func (d *DmgService) StartInstances() {
	d.instances = make([]*instance.Instance, 0)
	d.processAccounts(d.cfg.Accounts, d.StartInstance)
}

func (d *DmgService) RestartInstances() {
	d.processAccounts(d.cfg.Accounts, func(account config.AccountsConfig) {
		d.RemoveInstance(account.Token)
		d.StartInstance(account)
	})
}

func (d *DmgService) GetInstances() []*InstanceView {
	instanceViews := make([]*InstanceView, 0, len(d.instances))

	for _, i := range d.instances {
		instanceView := &InstanceView{
			User:       i.User,
			ChannelID:  i.ChannelID,
			GuildID:    i.GuildID,
			Cfg:        i.Cfg,
			AccountCfg: i.AccountCfg,
			LastRan:    i.LastRan,
			Error:      i.Error,
		}
		instanceViews = append(instanceViews, instanceView)
	}

	return instanceViews
}
