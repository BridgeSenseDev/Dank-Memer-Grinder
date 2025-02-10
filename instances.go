package main

import (
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
	"sync"
	"time"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/config"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/instance"
)

func (d *DmgService) StartInstance(account config.AccountsConfig, readyState string, breakUpdateTime time.Time) {
	d.wg.Add(1)
	go func() {
		defer d.wg.Done()
		client := discord.NewClient(d.ctx, account.Token)

		var readyOnce sync.Once
		err := client.AddHandler(gateway.EventTypeReady, func(e gateway.EventReady) {
			readyOnce.Do(func() {
				client.ChannelID = account.ChannelID
				guildID, err := client.GetGuildID(account.ChannelID)
				if err != nil {
					utils.Log(utils.Discord, utils.Error, client.SafeGetUsername(), fmt.Sprintf("Failed to fetch GuildID from channelID %v: %s", account.ChannelID, err.Error()))
					in := instance.NewInstance(nil, nil, "", *d.cfg, account, "invalidChannelID", time.Now(), d.ctx)
					d.UpdateInstance(in)
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

				in := instance.NewInstance(client.Gateway.User(), client, client.GuildID, *d.cfg, account, readyState, breakUpdateTime, d.ctx)

				d.UpdateInstance(in)

				d.UpdateDiscordStatus(d.cfg.DiscordStatus)

				err = in.Start()
				if err != nil {
					return
				}
				utils.Log(utils.Important, utils.Info, in.SafeGetUsername(), fmt.Sprintf("Logged in as %s", e.User.Username))
			})
		})
		if err != nil {
			utils.Log(utils.Important, utils.Info, client.SafeGetUsername(), fmt.Sprintf("Failed to add ready handler: %s", err.Error()))
			return
		}

		err = client.Connect()

		if err != nil {
			utils.Log(utils.Important, utils.Error, "", fmt.Sprintf("Failed to connect: %v", err.Error()))
			in := instance.NewInstance(nil, nil, "", *d.cfg, account, "invalidToken", time.Now(), d.ctx)
			d.UpdateInstance(in)
		}

		statusChan := client.Gateway.StatusUpdates()

		for {
			select {
			case status := <-statusChan:
				switch status {
				case gateway.StatusInvalidToken:
					in := instance.NewInstance(nil, nil, "", *d.cfg, account, "invalidToken", time.Now(), d.ctx)
					d.UpdateInstance(in)
					break
				default:
				}
			case <-d.ctx.Done():
				client.Close()
				return
			}
		}
	}()
}

func (d *DmgService) RemoveInstance(token string, restarting bool) {
	in := d.instances[d.GetIndex(token)]

	if restarting {
		in.State = "restarting"
		utils.EmitEventIfNotCLI("instanceUpdate", in.GetView())
	}

	in.Stop()

	if !restarting {
		d.instances = append(
			d.instances[:d.GetIndex(token)],
			d.instances[d.GetIndex(token)+1:]...,
		)
	}
}

func (d *DmgService) RestartInstance(token string) *instance.View {
	d.RemoveInstance(token, true)
	in := d.instances[d.GetIndex(token)]

	d.StartInstance(in.AccountCfg, "ready", time.Now())

	return in.GetView()
}

func (d *DmgService) processAccounts(accounts []config.AccountsConfig, action func(config.AccountsConfig, bool)) {
	for index, account := range accounts {
		action(account, index == 0)
	}
}

func (d *DmgService) StartInstances() {
	d.instances = make([]*instance.Instance, 0)

	accounts := make([]config.AccountsConfig, len(d.cfg.Accounts))
	copy(accounts, d.cfg.Accounts)

	utils.Rng.Shuffle(len(accounts), func(i, j int) {
		accounts[i], accounts[j] = accounts[j], accounts[i]
	})

	d.processAccounts(accounts, func(account config.AccountsConfig, firstAccount bool) {
		if firstAccount {
			in := instance.NewInstance(nil, nil, "", *d.cfg, account, "starting", time.Now(), d.ctx)
			d.UpdateInstance(in)
			d.StartInstance(account, "ready", time.Now())
			return
		}

		waitTime := utils.RandMinutes(d.cfg.Cooldowns.StartDelay.MinMinutes, d.cfg.Cooldowns.StartDelay.MaxMinutes)

		in := instance.NewInstance(nil, nil, "", *d.cfg, account, "waitingUnready", time.Now().Add(waitTime), d.ctx)
		d.UpdateInstance(in)
		d.StartInstance(account, "waitingReady", time.Now().Add(waitTime))

		<-utils.Sleep(5 * time.Second)
	})
}

func (d *DmgService) RestartInstances() {
	accounts := make([]config.AccountsConfig, len(d.cfg.Accounts))
	copy(accounts, d.cfg.Accounts)

	utils.Rng.Shuffle(len(accounts), func(i, j int) {
		accounts[i], accounts[j] = accounts[j], accounts[i]
	})

	d.processAccounts(accounts, func(account config.AccountsConfig, firstAccount bool) {
		d.RemoveInstance(account.Token, true)
	})

	d.StartInstances()
}

func (d *DmgService) GetIndex(token string) int {
	for i, in := range d.instances {
		if in.AccountCfg.Token == token {
			return i
		}
	}
	return -1
}

func (d *DmgService) UpdateInstance(ins *instance.Instance) {
	utils.EmitEventIfNotCLI("instanceUpdate", ins.GetView())

	for i, in := range d.instances {
		if in.AccountCfg.Token == ins.AccountCfg.Token {
			d.instances[i] = ins
			return
		}
	}

	d.instances = append(d.instances, ins)
}
