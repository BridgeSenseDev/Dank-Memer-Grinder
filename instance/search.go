package instance

import (
	"fmt"
	"strings"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
)

func (in *Instance) Search(message *types.MessageEventData) {
	buttons := message.Components[0].(*types.ActionsRow).Components

	buttonPriority := make(map[int]int)

	for i, button := range buttons {
		label := strings.ToLower(button.(*types.Button).Label)

		if utils.Contains(in.Cfg.Commands.Search.Priority, label) {
			buttonPriority[i] = 2
		} else if utils.Contains(in.Cfg.Commands.Search.SecondPriority, label) {
			buttonPriority[i] = 1
		} else if utils.Contains(in.Cfg.Commands.Search.Avoid, label) {
			buttonPriority[i] = -1
		} else {
			buttonPriority[i] = 0
		}
	}

	maxPriority := utils.GetMaxPriority(buttonPriority)

	err := in.Client.ClickButton(message.MessageData, 0, maxPriority)
	if err != nil {
		in.Log("discord", "ERR", fmt.Sprintf("Failed to click search button: %s", err.Error()))
	}
}
