package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"sync"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/config"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/instance"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
	"github.com/imdario/mergo"
	"github.com/valyala/fasthttp"
)

type DmgService struct {
	ctx       context.Context
	cfg       *config.Config
	wg        *sync.WaitGroup
	instances []*instance.Instance
	wsMutex   sync.Mutex
}

func (d *DmgService) startup() {
	userCfg, err := utils.ReadConfig()
	if err != nil {
		utils.Log(utils.Important, utils.Error, "",
			fmt.Sprintf("Failed to read config file, downloading example config: %s", err.Error()))

		defaultCfg, dlErr := downloadDefaultConfig()
		if dlErr != nil {
			utils.ShowErrorDialog("A fatal error occurred!",
				fmt.Sprintf("Failed to download default config file: %s", dlErr.Error()))
		}

		if writeErr := writeConfigToDisk(defaultCfg); writeErr != nil {
			utils.ShowErrorDialog("A fatal error occurred!",
				fmt.Sprintf("Failed to write config.json: %s", writeErr.Error()))
		}
		userCfg = defaultCfg
	} else {
		defaultCfg, dlErr := downloadDefaultConfig()
		if dlErr != nil {
			utils.Log(utils.Important, utils.Error, "",
				fmt.Sprintf("Failed to download default config file for merging: %s", dlErr.Error()))
		} else {
			if mergeErr := mergo.Merge(&userCfg, defaultCfg); mergeErr != nil {
				utils.Log(utils.Important, utils.Error, "",
					fmt.Sprintf("Failed to merge config: %s", mergeErr.Error()))
			}
		}
	}

	if err = userCfg.Validate(); err != nil {
		utils.ShowErrorDialog("A fatal error occurred!",
			fmt.Sprintf("Invalid config.json: %s", err.Error()))
	}

	utils.EmitEventIfNotCLI("configUpdate", userCfg)
	d.ctx = context.Background()
	d.cfg = &userCfg
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

func downloadDefaultConfig() (config.Config, error) {
	var defCfg config.Config

	client := &fasthttp.Client{}

	req := fasthttp.AcquireRequest()
	defer fasthttp.ReleaseRequest(req)

	req.SetRequestURI("https://raw.githubusercontent.com/BridgeSenseDev/Dank-Memer-Grinder/refs/heads/main/config.example.json")
	resp := fasthttp.AcquireResponse()
	defer fasthttp.ReleaseResponse(resp)

	if err := client.Do(req, resp); err != nil {
		return defCfg, err
	}

	if resp.StatusCode() != fasthttp.StatusOK {
		return defCfg, fmt.Errorf("failed to download default config: %d", resp.StatusCode())
	}

	body := resp.Body()
	if err := json.Unmarshal(body, &defCfg); err != nil {
		return defCfg, err
	}

	return defCfg, nil
}

func writeConfigToDisk(cfg config.Config) error {
	file, err := os.Create(utils.GetConfigPath())
	if err != nil {
		return err
	}
	defer func() {
		errClose := file.Close()
		if errClose != nil {
			utils.Log(utils.Important, utils.Error, "",
				fmt.Sprintf("Failed to close config.json: %s", errClose.Error()))
		}
	}()

	configJSON, err := json.MarshalIndent(cfg, "", "  ")
	if err != nil {
		return err
	}

	_, err = io.WriteString(file, string(configJSON))
	return err
}
