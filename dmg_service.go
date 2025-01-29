package main

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"github.com/valyala/fasthttp"
	"os"
	"sync"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/config"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/instance"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
)

type DmgService struct {
	ctx       context.Context
	cfg       *config.Config
	wg        *sync.WaitGroup
	instances []*instance.Instance
	wsMutex   sync.Mutex
}

func (d *DmgService) startup() {
	// Load configuration
	cfg, err := utils.ReadConfig()

	if err != nil {
		utils.Log(utils.Important, utils.Error, "", fmt.Sprintf("Failed to read config file, downloading example config: %s", err.Error()))

		client := &fasthttp.Client{}

		req := fasthttp.AcquireRequest()
		defer fasthttp.ReleaseRequest(req)

		req.SetRequestURI("https://raw.githubusercontent.com/BridgeSenseDev/Dank-Memer-Grinder/refs/heads/main/config.example.json")
		resp := fasthttp.AcquireResponse()
		defer fasthttp.ReleaseResponse(resp)

		err = client.Do(req, resp)
		if err != nil {
			utils.ShowErrorDialog("A fatal error occurred!", fmt.Sprintf("Failed to download config file: %s", err.Error()))
		}

		if resp.StatusCode() != fasthttp.StatusOK {
			utils.ShowErrorDialog("A fatal error occurred!", fmt.Sprintf("Failed to download config file: %d", resp.StatusCode()))
		}

		file, err2 := os.Create(utils.GetConfigPath())
		if err2 != nil {
			utils.ShowErrorDialog("A fatal error occurred!", fmt.Sprintf("Failed to write config.json: %s", err2.Error()))
		}
		defer func(file *os.File) {
			err = file.Close()
			if err != nil {
				utils.ShowErrorDialog("A fatal error occurred!", fmt.Sprintf("Failed to close config.json: %s", err2.Error()))
			}
		}(file)

		_, err2 = file.Write(resp.Body())
		if err2 != nil {
			utils.ShowErrorDialog("A fatal error occurred!", fmt.Sprintf("Error saving file: %s", err2.Error()))
		}

		cfg, err = utils.ReadConfig()
		if err != nil {
			utils.ShowErrorDialog("A fatal error occurred!", fmt.Sprintf("Failed to read config.json: %s", err.Error()))
		}
	}

	if err = cfg.Validate(); err != nil {
		utils.ShowErrorDialog("A fatal error occurred!", fmt.Sprintf("Invalid config.json: %s", err.Error()))
	}

	utils.EmitEventIfNotCLI("configUpdate", cfg)
	d.ctx = context.Background()
	d.cfg = &cfg
	d.StartInstances()
}

func (d *DmgService) GetConfig() *config.Config {
	return d.cfg
}

func (d *DmgService) UpdateConfig(newCfg *config.Config) error {
	if err := newCfg.Validate(); err != nil {
		return err
	}

	d.cfg = newCfg

	configJSON, err := json.MarshalIndent(newCfg, "", "  ")
	if err != nil {
		return err
	}

	err = os.WriteFile(utils.GetConfigPath(), configJSON, 0644)
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
			utils.Log(utils.Others, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Error setting Discord status: %s", err))
		}

		in.User.Status = status
	}
}
