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
	"github.com/wailsapp/wails/v2/pkg/runtime"
)

type App struct {
	ctx       context.Context
	cfg       *config.Config
	wg        *sync.WaitGroup
	instances []*instance.Instance
	wsMutex   sync.Mutex
}

func NewApp() *App {
	return &App{
		wg:      &sync.WaitGroup{},
		wsMutex: sync.Mutex{},
	}
}

func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
	log.Logger = log.Output(zerolog.ConsoleWriter{Out: os.Stderr})

	// Load configuration
	configFile := "./config.json"
	cfg, err := config.ReadConfig(configFile)
	if err != nil {
		runtime.MessageDialog(a.ctx, runtime.MessageDialogOptions{
			Type:    runtime.ErrorDialog,
			Title:   "A fatal error occurred!",
			Message: fmt.Sprintf("Failed to read config file: %s", err.Error()),
		})
		panic(fmt.Sprintf("Failed to read config file: %s", err.Error()))
	}

	a.cfg = &cfg
}

func (a *App) domReady(ctx context.Context) {
	if a.cfg != nil {
		a.StartInstances()
	}
}

func (a *App) beforeClose(ctx context.Context) (prevent bool) {
	return false
}

func (a *App) shutdown(ctx context.Context) {
}

func (a *App) GetConfig() *config.Config {
	return a.cfg
}

func (a *App) UpdateConfig(newCfg *config.Config) error {

	a.cfg = newCfg

	configJSON, err := json.MarshalIndent(newCfg, "", "  ")
	if err != nil {
		return err
	}

	err = os.WriteFile("./config.json", configJSON, 0644)
	if err != nil {
		return err
	}

	for _, i := range a.instances {
		i.UpdateConfig(*newCfg)
	}

	return nil
}

func (a *App) UpdateInstanceToken(oldToken string, newToken string) {
	for _, in := range a.instances {
		if in.AccountCfg.Token == oldToken {
			in.AccountCfg.Token = newToken
			break
		}
	}
}

func (a *App) UpdateDiscordStatus(status types.OnlineStatus) {
	a.wsMutex.Lock()
	defer a.wsMutex.Unlock()

	for _, in := range a.instances {
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
