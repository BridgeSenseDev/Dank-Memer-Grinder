package instance

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
)

func (in *Instance) Adventure(message *types.MessageEventData) {
	embed := message.Embeds[0]
	adventureOption := in.Cfg.Commands.Adventure.AdventureOption

	if strings.Contains(embed.Description, "> You can start another adventure at <t:") {
		re := regexp.MustCompile(`<t:(\d+):`)
		matches := re.FindStringSubmatch(embed.Description)
		if len(matches) > 1 {
			timestamp, err := strconv.ParseInt(matches[1], 10, 64)
			if err != nil {
				return
			}
			cooldownTime := time.Unix(timestamp, 0)

			now := time.Now()
			timeLeft := cooldownTime.Sub(now).Seconds()

			in.LastRan["Adventure"] = time.Unix(now.Unix()+int64(timeLeft)+int64(time.Minute.Seconds()), 0)

			in.Log("others", "INF", fmt.Sprintf("Time until next adventure: %.2f seconds", timeLeft))
			return
		}
	}

	if embed.Author.Name == "Choose an Adventure" {
		adventureOptions := message.Components[0].(*types.ActionsRow).Components[0].(*types.SelectMenu).Options
		for _, option := range adventureOptions {
			if option.Value == string(adventureOption) {
				if !option.Default {
					err := in.Client.ChooseSelectMenu(message.MessageData, 0, 0, []string{string(adventureOption)})
					if err != nil {
						in.Log("discord", "ERR", fmt.Sprintf("Failed to choose adventure select menu: %s", err.Error()))
					}
					return
				} else {
					if !message.Components[1].(*types.ActionsRow).Components[0].(*types.Button).Disabled {
						err := in.Client.ClickButton(message.MessageData, 1, 0)
						if err != nil {
							in.Log("discord", "ERR", fmt.Sprintf("Failed to click start adventure button: %s", err.Error()))
						}

						return
					} else {
						in.Log("others", "ERR", fmt.Sprintf("Not enough tickets to start %s adventure", adventureOption))
						return
					}
				}
			}
		}
	} else if embed.Author.Name == "Adventure Summary" {
		in.Log("others", "INF", fmt.Sprintf("Completed %s adventure", adventureOption))
		in.UnpauseCommands()

		cooldownLabel := message.Components[0].(*types.ActionsRow).Components[0].(*types.Button).Label

		re := regexp.MustCompile(`(\d+) minutes`)
		matches := re.FindStringSubmatch(cooldownLabel)
		if len(matches) > 1 {
			cooldownMinutes, err := strconv.Atoi(matches[1])
			if err != nil {
				return
			}

			in.LastRan["Adventure"] = time.Unix(time.Now().Unix()+int64(cooldownMinutes*60)+int64(time.Minute.Seconds()), 0)

			in.Log("others", "INF", fmt.Sprintf("Time until next adventure: %d minutes", cooldownMinutes))
		}
		return
	} else if strings.Contains(embed.Title, "choose items you want to bring along") {
		if !message.Components[1].(*types.ActionsRow).Components[0].(*types.Button).Disabled {
			in.PauseCommands(false)
			err := in.Client.ClickButton(message.MessageData, 1, 0)
			if err != nil {
				in.Log("discord", "ERR", fmt.Sprintf("Failed to click start adventure button: %s", err.Error()))
			} else {
				in.Log("others", "INF", fmt.Sprintf("Started %s adventure", adventureOption))
			}

			return
		} else {
			in.Log("others", "ERR", fmt.Sprintf("Not enough tickets to start %s adventure", adventureOption))
			return
		}
	}

	for i := 0; i < 2; i++ {
		if button, ok := message.Components[i].(*types.ActionsRow).Components[1].(*types.Button); ok {
			if !button.Disabled && button.Emoji.ID == "1067941108568567818" {
				err := in.Client.ClickButton(message.MessageData, i, 1)
				if err != nil {
					in.Log("discord", "ERR", fmt.Sprintf("Failed to click next adventure page button: %s", err.Error()))
				}

				return
			}
		}
	}

	if strings.Contains(embed.Description, "Catch one of em!") {
		err := in.Client.ClickButton(message.MessageData, 0, 2)
		if err != nil {
			in.Log("discord", "ERR", `failed to click "Catch one of em!" adventure button`)
		}

		err = in.Client.ClickButton(message.MessageData, 1, 1)
		if err != nil {
			in.Log("discord", "ERR", `failed to click "Catch one of em!" adventure button`)
		}

		return
	}

	var adventureMap map[string]string
	switch adventureOption {
	case "space":
		adventureMap = in.Cfg.Adventure.Space
	case "west":
		adventureMap = in.Cfg.Adventure.West
	case "brazil":
		adventureMap = in.Cfg.Adventure.Brazil
	case "vacation":
		adventureMap = in.Cfg.Adventure.Vacation
	}

	question := strings.Split(embed.Description, "\n")[0]
	for q, ans := range adventureMap {
		if strings.Contains(strings.ToLower(question), strings.ToLower(q)) {
			for columnIndex, button := range message.Components[0].(*types.ActionsRow).Components {
				if strings.EqualFold(button.(*types.Button).Label, ans) {
					err := in.Client.ClickButton(message.MessageData, 0, columnIndex)
					if err != nil {
						in.Log("discord", "ERR", fmt.Sprintf("Failed to click adventure answer button: %s", err.Error()))
					}
					return
				}
			}
			in.Client.ClickButton(message.MessageData, 0, 0)
			in.Log("important", "ERR", fmt.Sprintf("Failed to find answer in config.json for adventure question: %s", q))
		}
	}
}

func (in *Instance) AdventureMessageCreate(message *types.MessageEventData) {
	in.Adventure(message)
}

func (in *Instance) AdventureMessageUpdate(message *types.MessageEventData) {
	in.Adventure(message)
}
