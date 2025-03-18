package main

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/wailsapp/wails/v3/pkg/application"
	"io"
	"os"
	"sync"
	"time"

	"dario.cat/mergo"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/config"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/instance"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
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
		utils.Log(utils.Important, utils.Info, "",
			fmt.Sprintf("Failed to find config file, downloading example config. Error: %s", err.Error()))
		utils.Log(utils.Important, utils.Info, "",
			"Welcome to DMG! If this is your first time running DMG, start by [adding your accounts](https://docs.dankmemer.tools/configuration/entering-token-and-channel-id).")

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
	d.CheckForUpdates()
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

		presenceUpdate := gateway.MessageDataPresenceUpdate{
			Since:      new(int64),
			Activities: []map[string]interface{}{},
			Status:     status,
			AFK:        false,
		}

		err := in.Client.SendMessage(3, presenceUpdate)
		if err != nil {
			utils.Log(utils.Others, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Error setting Discord status: %s", err))
		}

		in.User.Status = status
	}
}

func (d *DmgService) CheckForUpdates() bool {
	currentVersion := "v2.0.0-alpha14"
	newVersion, changes := utils.CheckForUpdates(currentVersion)

	if newVersion != "" && newVersion != currentVersion {
		application.Get().CurrentWindow().SetURL("/#/update")
		time.Sleep(500 * time.Millisecond)
		utils.EmitEventIfNotCLI("updateChanges", currentVersion, newVersion, changes)
		return true
	}

	return false
}

func (d *DmgService) Update() {
	if application.Get().Environment().Debug {
		utils.EmitEventIfNotCLI("updateFailed", "Debug environment detected. Update using git instead.")
		return
	}

	err := utils.DownloadUpdate()
	if err != nil {
		utils.Log(utils.Important, utils.Error, "", fmt.Sprintf("Failed to download update: %s", err.Error()))
		utils.EmitEventIfNotCLI("updateFailed", err.Error())
		return
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
