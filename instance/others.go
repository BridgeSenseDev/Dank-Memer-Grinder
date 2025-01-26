package instance

import (
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
	"strings"
)

func (in *Instance) Others(message gateway.EventMessage) {
	if message.Embeds[0].Title == "You have an unread alert!" && in.Cfg.ReadAlerts {
		err := in.SendCommand("alert", nil, true)

		if err != nil {
			utils.Log(utils.Others, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to send /alert command: %s", err.Error()))
		}
	}

	if strings.Contains(strings.ToLower(message.Embeds[0].Title), "maintenance") {
		utils.Log(utils.Important, utils.Info, in.SafeGetUsername(), "Global toggle has been switched due to a Dank Memer maintenance. Check if the update is safe before continuing to grind")
		in.Cfg.State = false
		in.UpdateConfig(in.Cfg)
		utils.EmitEventIfNotCLI("configUpdate", in.Cfg)
	}
}
