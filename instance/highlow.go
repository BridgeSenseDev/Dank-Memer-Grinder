package instance

import (
	"fmt"
	"regexp"
	"strconv"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
)

func (in *Instance) HighLow(message *types.MessageEventData) {
	embed := message.Embeds[0]

	matches := regexp.MustCompile(`\*\*(.*?)\*\*`).FindStringSubmatch(embed.Description)
	if len(matches) < 2 {
		return
	}

	numStr := matches[1]
	num, _ := strconv.Atoi(numStr)

	if num >= 50 {
		err := in.Client.ClickButton(message.MessageData, 0, 0)
		if err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to click highlow button: %s", err.Error()))
		}
	} else {
		err := in.Client.ClickButton(message.MessageData, 0, 2)
		if err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to click highlow button: %s", err.Error()))
		}
	}
}
