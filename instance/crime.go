package instance

import (
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"strings"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
)

func (in *Instance) Crime(message gateway.EventMessage) {
	buttons := message.Components[0].(*types.ActionsRow).Components

	buttonPriority := make(map[int]int)

	for i, button := range buttons {
		label := strings.ToLower(button.(*types.Button).Label)

		if utils.Contains(in.Cfg.Commands.Crime.Priority, label) {
			buttonPriority[i] = 2
		} else if utils.Contains(in.Cfg.Commands.Crime.SecondPriority, label) {
			buttonPriority[i] = 1
		} else if utils.Contains(in.Cfg.Commands.Crime.Avoid, label) {
			buttonPriority[i] = -1
		} else {
			buttonPriority[i] = 0
		}
	}

	maxPriority := utils.GetMaxPriority(buttonPriority)

	err := in.ClickButton(message, 0, maxPriority)
	if err != nil {
		in.Log("discord", "ERR", fmt.Sprintf("Failed to click crime button: %s", err.Error()))
	}
}
