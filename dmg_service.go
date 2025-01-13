package main

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"os"
	"sync"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/config"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/instance"
	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
)

type DmgService struct {
	ctx       context.Context
	cfg       *config.Config
	wg        *sync.WaitGroup
	instances []*instance.Instance
	wsMutex   sync.Mutex
}

func (d *DmgService) startup() {
	log.Logger = log.Output(zerolog.ConsoleWriter{Out: os.Stderr})

	// Load configuration
	configFile := "./config.json"
	cfg, err := config.ReadConfig(configFile)
	if err != nil {
		//runtime.MessageDialog(d.ctx, runtime.MessageDialogOptions{
		//	Type:    runtime.ErrorDialog,
		//	Title:   "A fatal error occurred!",
		//	Message: fmt.Sprintf("Failed to read config file: %s", err.Error()),
		//})
		panic(fmt.Sprintf("Failed to read config file: %s", err.Error()))
	}

	d.ctx = context.Background()
	d.cfg = &cfg
	d.StartInstances()
}

func (d *DmgService) GetConfig() *config.Config {
	return d.cfg
}

func (d *DmgService) UpdateConfig(newCfg *config.Config) error {

	d.cfg = newCfg

	configJSON, err := json.MarshalIndent(newCfg, "", "  ")
	if err != nil {
		return err
	}

	err = os.WriteFile("./config.json", configJSON, 0644)
	if err != nil {
		return err
	}

	for _, i := range d.instances {
		i.UpdateConfig(*newCfg)
	}

	return nil
}

func (d *DmgService) UpdateInstanceToken(oldToken string, newToken string) {
	for _, in := range d.instances {
		if in.AccountCfg.Token == oldToken {
			in.AccountCfg.Token = newToken
			break
		}
	}
}

func (d *DmgService) UpdateDiscordStatus(status types.OnlineStatus) {
	d.wsMutex.Lock()
	defer d.wsMutex.Unlock()

	for _, in := range d.instances {
		if in == nil || in.User == nil || in.User.Status == status {
			continue
		}

		d := gateway.MessageDataPresenceUpdate{
			Since:      new(int64),
			Activities: []map[string]interface{}{},
			Status:     status,
			AFK:        false,
		}

		err := in.Client.SendMessage(3, d)
		if err != nil {
			log.Error().Msgf("Error setting Discord status: %s", err)
		}

		in.User.Status = status
	}
}
