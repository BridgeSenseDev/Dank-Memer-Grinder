package instance

import (
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
)

func (in *Instance) ScratchMessageCreate(message gateway.EventMessage) {
	embed := message.Embeds[0]
	if !strings.Contains(embed.Description, "You can scratch") {
		return
	}

	if message.Flags != 64 {
		in.PauseCommands(false)
		utils.Log(utils.Others, utils.Info, in.SafeGetUsername(), "Solving scratch command")

		err := in.ClickButton(message, utils.Rng.Intn(4), utils.Rng.Intn(2))
		if err != nil {
			utils.Log(utils.Others, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click scratch answer button: %s", err.Error()))
		}
	} else {
		if strings.Contains(embed.Description, "You can scratch only once") {
			re := regexp.MustCompile(`Try <t:(\d+):R>`)
			matches := re.FindStringSubmatch(message.Embeds[0].Description)

			if len(matches) > 1 {
				timestamp, err := strconv.ParseInt(matches[1], 10, 64)
				if err != nil {
					return
				}
				in.LastRan["Scratch"] = time.Unix(timestamp+int64(time.Minute.Seconds()), 0)

				utils.Log(utils.Others, utils.Info, in.SafeGetUsername(), fmt.Sprintf("Time until next scratch: %.2f minutes", time.Until(in.LastRan["Scratch"]).Minutes()))
			}
		} else if strings.Contains(embed.Description, "vote") {
			utils.Log(utils.Others, utils.Error, in.SafeGetUsername(), "Account hasn't voted in past 12 hours")
		}
	}
}

func (in *Instance) ScratchMessageUpdate(message gateway.EventMessage) {
	re := regexp.MustCompile(`You can scratch \*\*(\d+)\*\* more field`)
	matches := re.FindStringSubmatch(message.Embeds[0].Description)

	if len(matches) > 1 {
		attemptsLeft, err := strconv.Atoi(matches[1])
		if err != nil {
			return
		}

		if attemptsLeft == 0 {
			err = in.ClickButton(message, 4, 3)
			if err != nil {
				utils.Log(utils.Others, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click end scratch button: %s", err.Error()))
			}

			utils.Log(utils.Others, utils.Info, in.SafeGetUsername(), "Solved scratch command")
			in.UnpauseCommands()

			re = regexp.MustCompile(`Next Scratch-Off available <t:(\d+):R>`)
			matches = re.FindStringSubmatch(message.Embeds[0].Description)

			if len(matches) > 1 {
				actionsRow, ok := message.Components[4].(*types.ActionsRow)
				if ok && len(actionsRow.Components) == 4 {
					timestamp, err := strconv.ParseInt(matches[1], 10, 64)
					if err != nil {
						return
					}
					in.LastRan["Scratch"] = time.Unix(timestamp+int64(time.Minute.Seconds()), 0)

					utils.Log(utils.Others, utils.Info, in.SafeGetUsername(), fmt.Sprintf("Time until next scratch: %.2f minutes", time.Until(in.LastRan["Scratch"]).Minutes()))
				}
			}
		} else {
			for {
				x := utils.Rng.Intn(2)
				y := utils.Rng.Intn(4)

				actionRow := message.Components[y].(*types.ActionsRow)
				button := actionRow.Components[x].(*types.Button)
				if !button.Disabled {
					err = in.ClickButton(message, y, x)
					if err != nil {
						utils.Log(utils.Others, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click scratch button: %s", err.Error()))
					} else {
						break
					}
				}
			}
		}
	}
}
