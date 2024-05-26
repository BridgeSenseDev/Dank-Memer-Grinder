package instance

import (
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"regexp"
	"strconv"
)

func (in *Instance) HighLow(message gateway.EventMessage) {
	embed := message.Embeds[0]

	matches := regexp.MustCompile(`\*\*(.*?)\*\*`).FindStringSubmatch(embed.Description)
	if len(matches) < 2 {
		return
	}

	numStr := matches[1]
	num, _ := strconv.Atoi(numStr)

	if num >= 50 {
		err := in.ClickButton(message, 0, 0)
		if err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to click highlow button: %s", err.Error()))
		}
	} else {
		err := in.ClickButton(message, 0, 2)
		if err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to click highlow button: %s", err.Error()))
		}
	}
}
