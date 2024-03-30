package instance

import (
	"fmt"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
)

func (in *Instance) ScratchMessageCreate(message *types.MessageEventData) {
	in.PauseCommands(false)
	in.Log("others", "INF", "Solving scratch command")

	coordinates := make([][2]int, 0, 15)
	for x := 0; x < 3; x++ {
		for y := 0; y < 5; y++ {
			coordinates = append(coordinates, [2]int{x, y})
		}
	}
	utils.Rng.Shuffle(len(coordinates), func(i, j int) { coordinates[i], coordinates[j] = coordinates[j], coordinates[i] })

	for i := 0; i < 4; i++ {
		x, y := coordinates[len(coordinates)-1][0], coordinates[len(coordinates)-1][1]
		coordinates = coordinates[:len(coordinates)-1]
		err := in.Client.ClickButton(message.MessageData, y, x)
		if err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to click scratch answer button: %s", err.Error()))
		}
	}
}

func (in *Instance) ScratchMessageUpdate(message *types.MessageEventData) {
	actionsRow, ok := message.Components[4].(*types.ActionsRow)
	if ok && len(actionsRow.Components) == 4 {
		if !actionsRow.Components[3].(*types.Button).Disabled {
			err := in.Client.ClickButton(message.MessageData, 4, 3)
			if err != nil {
				in.Log("discord", "ERR", fmt.Sprintf("Failed to click close scratch menu button: %s", err.Error()))
			} else {
				in.Log("others", "INF", "Solved scratch command")
			}
			in.UnpauseCommands()
		}
	}
}
