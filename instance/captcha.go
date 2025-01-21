package instance

import (
	"fmt"
	"strings"
	"time"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
)

type ApiResponse struct {
	Success bool   `json:"success"`
	Message string `json:"message"`
}

func (in *Instance) Captcha(message gateway.EventMessage) bool {
	embed := message.Embeds[0]
	if !strings.Contains(embed.Description, "captcha") || len(message.Components) == 0 {
		if embed.Description == "You have passed the captcha! You can now run commands." {
			utils.Log(utils.Important, utils.Info, in.SafeGetUsername(), "Successfully solved captcha")
		}
		return false
	}

	utils.Log(utils.Important, utils.Info, in.SafeGetUsername(), "Captcha Detected")
	in.PauseCommands(true)

	if in.Cfg.ApiKey == "" {
		utils.Log(utils.Important, utils.Error, in.SafeGetUsername(), "API key missing, not automatically solving captcha")
		return true
	}

	captchaID, err := in.startCaptchaSolve()
	if err != nil {
		utils.Log(utils.Important, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Captcha solver initiation failed: %s", err))
		return true
	}

	return in.waitForCaptchaSolution(captchaID)
}

func (in *Instance) startCaptchaSolve() (string, error) {
	code, err := in.Client.GetAuthorizationCode()

	headers := map[string]string{
		"api-key":    in.Cfg.ApiKey,
		"code":       code,
		"discord-id": in.User.ID,
	}

	resp, err := utils.MakeAPIRequest("https://api.dankmemer.tools/captcha/v2/new", headers)
	if err != nil {
		return "", err
	}

	if !resp.Success {
		return "", fmt.Errorf("captcha solver failed: %s", resp.Message)
	}

	return resp.Message, nil
}

func (in *Instance) waitForCaptchaSolution(captchaID string) bool {
	headers := map[string]string{
		"api-key":    in.Cfg.ApiKey,
		"captcha-id": captchaID,
	}

	for {
		resp, err := utils.MakeAPIRequest("https://api.dankmemer.tools/captcha/v2/status", headers)
		if err != nil {
			utils.Log(utils.Important, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Captcha update request failed: %s", err))
			return true
		}

		switch resp.Message {
		case "An internal error occurred":
			utils.Log(utils.Important, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Captcha solver failed: %s", resp.Message))
			return true
		case "Successfully solved captcha":
			utils.Log(utils.Important, utils.Info, in.SafeGetUsername(), "Successfully solved captcha")
			return true
		case "Solving in progress":
			utils.Sleep(time.Minute)
		default:
			utils.Log(utils.Important, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Unknown captcha solver status: %s", resp.Message))
			return true
		}
	}
}
