package instance

import (
	"fmt"
	"strings"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/wailsapp/wails/v2/pkg/runtime"
)

func (in *Instance) Others(message *types.MessageEventData) {
	if message.Embeds[0].Title == "You have an unread alert!" && in.Cfg.ReadAlerts {
		err := in.SendCommand("alert", nil)

		if err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to send /alert command: %s", err.Error()))
		}
	}

	if strings.Contains(strings.ToLower(message.Embeds[0].Title), "maintenance") {
		in.Log("important", "INF", "Global toggle has been switched due to a Dank Memer maintenance. Check if the update is safe before continuing to grind")
		in.Cfg.State = false
		in.UpdateConfig(in.Cfg)
		runtime.EventsEmit(in.Ctx, "configUpdate", in.Cfg)
	}
	if strings.Contains(strings.ToLower(message.Embeds[0].Title), "calm down!") {
		in.Log("important", "INF", "Grinding has been paused as discord channel ratelimit has been reached. Please come back later to continue.")
		in.Cfg.State = false
		in.UpdateConfig(in.Cfg)
		runtime.EventsEmit(in.Ctx, "configUpdate", in.Cfg)
	}
}
