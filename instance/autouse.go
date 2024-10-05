package instance

import (
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"reflect"
	"regexp"
	"strings"
	"unicode"
)

func addSpaces(s string) string {
	var result []rune

	for i, r := range s {
		if i > 0 && unicode.IsUpper(r) {
			result = append(result, ' ')
		}
		result = append(result, r)
	}

	return string(result)
}

func extractItems(input string) []string {
	re := regexp.MustCompile(`<.*?>\s*(.*?)\*\*`)

	matches := re.FindAllStringSubmatch(input, -1)

	var items []string
	for _, match := range matches {
		if len(match) > 1 {
			items = append(items, match[1])
		}
	}

	return items
}

func (in *Instance) AutoUse(message gateway.EventMessage) {
	in.Log("discord", "INF", fmt.Sprintf("Auto use triggered for %s", in.User.Username))
	embed := message.Embeds[0]

	err := in.ClickDmButton(message, 0, 0)
	if err != nil {
		in.Log("discord", "ERR", fmt.Sprintf("Failed to click use again button: %s", err.Error()))
	}

	if embed.Title == "Item Expiration" {
		val := reflect.ValueOf(in.Cfg.AutoUse)
		for i := 0; i < val.NumField(); i++ {

			if strings.Contains(embed.Description, addSpaces(val.Type().Field(i).Name)) {
				component := message.Components[0].(*types.ActionsRow).Components[0].(*types.Button)
				if component.Disabled || component.Label != "Use Again" {
					continue
				}

				if err := in.ClickDmButton(message, 0, 0); err != nil {
					in.Log("discord", "ERR", fmt.Sprintf("Failed to click use again button: %s", err.Error()))
				}
				break
			}
		}
	}
}

func (in *Instance) ProfileMessageCreate(message gateway.EventMessage) {
	embed := message.Embeds[0]

	if embed.Title == in.User.Username {
		in.PauseCommands(false)
		err := in.ChooseSelectMenu(message, 0, 0, []string{"activeitems"})
		if err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to choose profile select menu: %s", err.Error()))
		}
	}
}

func (in *Instance) ProfileMessageUpdate(message gateway.EventMessage) {
	embed := message.Embeds[0]

	if embed.Title == fmt.Sprintf(`%s's active items`, in.User.Username) {
		items := extractItems(embed.Description)

		val := reflect.ValueOf(in.Cfg.AutoUse)
		for i := 0; i < val.NumField(); i++ {
			if val.Field(i).FieldByName("State").Bool() {
				itemIsUsed := false
				for _, item := range items {
					if strings.ToLower(strings.ReplaceAll(item, " ", "")) == strings.ToLower(val.Type().Field(i).Name) {
						itemIsUsed = true
						break
					}
				}

				if !itemIsUsed {
					in.Log("others", "INF", fmt.Sprintf("Auto using %s", addSpaces(val.Type().Field(i).Name)))
					err := in.SendCommand("use", map[string]string{"item": addSpaces(val.Type().Field(i).Name)}, true)
					if err != nil {
						in.Log("discord", "ERR", fmt.Sprintf("Failed to send /use command: %s", err.Error()))
					}
					break
				}
			}
		}
		in.UnpauseCommands()
	}
}
