package instance

import (
	"fmt"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
)

func (in *Instance) Others(message *types.MessageEventData) {
	if message.Embeds[0].Title == "You have an unread alert!" && in.Cfg.ReadAlerts {
		err := in.Client.SendCommand("alert", nil)

		if err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to send /alert command: %s", err.Error()))
		}
	}
}
