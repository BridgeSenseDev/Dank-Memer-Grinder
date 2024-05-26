package instance

import (
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"strings"
	"time"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
)

func (in *Instance) PostMemesMessageCreate(message gateway.EventMessage) {
	platformOptions := message.Components[0].(*types.ActionsRow).Components[0].(*types.SelectMenu).Options
	memeTypeOptions := message.Components[1].(*types.ActionsRow).Components[0].(*types.SelectMenu).Options
	configOptions := in.Cfg.Commands.PostMemes.Platform
	option := configOptions[utils.Rng.Intn(len(configOptions))]

	if !platformOptions[option].Default {
		err := in.ChooseSelectMenu(message, 0, 0, []string{platformOptions[option].Value})
		if err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to choose postmemes platform select menu: %s", err.Error()))
		}
	}

	defaultOptionFound := false
	for _, option := range memeTypeOptions {
		if option.Default {
			defaultOptionFound = true
			break
		}
	}

	if !defaultOptionFound {
		randomIndex := utils.Rng.Intn(len(memeTypeOptions))
		err := in.ChooseSelectMenu(message, 1, 0, []string{memeTypeOptions[randomIndex].Value})
		if err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to choose postmemes option select menu: %s", err.Error()))
		}
	}

	err := in.ClickButton(message, 2, 0)
	if err != nil {
		in.Log("discord", "ERR", fmt.Sprintf("Failed to click postmemes button: %s", err.Error()))
	}
}

func (in *Instance) PostMemesMessageUpdate(message gateway.EventMessage) {
	embed := message.Embeds[0]
	if strings.Contains(embed.Description, "cannot post another meme for another 3 minutes") {
		in.LastRan["PostMemes"] = in.LastRan["PostMemes"].Add(3 * time.Minute)
	}
}
