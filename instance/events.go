package instance

import (
	_ "embed"
	"encoding/json"
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
	"regexp"
	"strings"
	"time"
)

//go:embed emojis.json
var emojisJson []byte

var emojis map[string]interface{}

func init() {
	err := json.Unmarshal(emojisJson, &emojis)
	if err != nil {
		utils.Log(utils.Important, utils.Error, "", fmt.Sprintf("Failed to unmarshal emoji data: %v", err))
	}
}

func (in *Instance) EventsMessageCreate(message gateway.EventMessage) {
	embed := message.Embeds[0]

	if embed.Color == 16044763 {
		// General random events color
		if embed.Title == "Trivia Night" {
			re := regexp.MustCompile(`\*\*(.*?)\*\*`)
			question := strings.Trim(re.FindStringSubmatch(embed.Description)[0], "*")
			var answer string

			for _, category := range trivia {
				ans, ok := category.(map[string]interface{})[question]
				if !ok {
					continue
				}

				condition := utils.Rng.Float64() > in.Cfg.Commands.Trivia.TriviaCorrectChance
				if !condition {
					answer = ans.(string)
				} else {
					answer = ""
				}
			}

			lines := strings.Split(embed.Description, "\n")

			if answer == "" {
				var choices []string
				for _, line := range lines {
					choice := strings.TrimSpace(strings.TrimPrefix(line, "-"))
					if choice != "" && choice != question {
						choices = append(choices, choice)
					}
				}
				if len(choices) > 0 {
					answer = choices[utils.Rng.Intn(len(choices))]
				}
			}

			for _, line := range lines {
				line = strings.TrimSpace(strings.TrimPrefix(line, "-"))
				if line == answer {
					<-utils.Sleep(time.Duration(utils.Rng.Intn(5-2)+2) * time.Second)
					err := in.SendChatMessage(strings.ToLower(answer), true)
					if err != nil {
						utils.Log(utils.Important, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to send trivia night chat message: %s", err.Error()))
						return
					}
				}
			}
		} else if embed.Title == "Fortnite Attack" || embed.Title == "Dank Memer Corp" || embed.Title == "Anti-Rizz" {
			re := regexp.MustCompile(`"([^"]+)"`)
			match := re.FindStringSubmatch(embed.Description)
			if len(match) > 1 {
				<-utils.Sleep(time.Duration(utils.Rng.Intn(5-2)+2) * time.Second)
				err := in.SendChatMessage(strings.ToLower(match[1]), true)
				if err != nil {
					utils.Log(utils.Important, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to send first to say chat message: %s", err.Error()))
				}
			} else {
				utils.Log(utils.Important, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to find first to say quote: %s", embed.Description))
			}
		} else if embed.Title == "Reverse Reverse" {
			if phrase := strings.TrimSpace(strings.Split(embed.Description, "#")[1]); phrase != "" {
				runes := []rune(phrase)
				for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
					runes[i], runes[j] = runes[j], runes[i]
				}

				<-utils.Sleep(time.Duration(utils.Rng.Intn(5-2)+2) * time.Second)
				err := in.SendChatMessage(strings.ToLower(string(runes)), true)
				if err != nil {
					utils.Log(utils.Important, utils.Error, in.SafeGetUsername(),
						fmt.Sprintf("Failed to send reverse reverse message: %s", err.Error()))
				}
			}
		} else if embed.Title == "Dice Champs" {
			err := in.ClickButton(message, 0, 0)
			if err != nil {
				utils.Log(utils.Important, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click dice champs button: %s", err.Error()))
			}
		} else if embed.Title == "Fortnite Dance Mode" {
			directions := map[string]string{
				"AR": "right",
				"AL": "left",
				"AU": "up",
				"AD": "down",
			}

			combo := strings.Split(embed.Description, "#")[2]
			re := regexp.MustCompile(`<:(A[RLUD]):\d+>`)
			matches := re.FindAllStringSubmatch(combo, -1)

			var result []string
			for _, match := range matches {
				if dir, ok := directions[match[1]]; ok {
					result = append(result, dir)
				}
			}

			<-utils.Sleep(time.Duration(utils.Rng.Intn(5-2)+2) * time.Second)
			err := in.SendChatMessage(strings.ToLower(strings.Join(result, " ")), true)
			if err != nil {
				utils.Log(utils.Important, utils.Error, in.SafeGetUsername(),
					fmt.Sprintf("Failed to send fortnite dance message: %s", err.Error()))
			}
		} else if embed.Title == "Punch Pepe" {
			lines := strings.Split(embed.Description, "\n")
			for row := 0; row < 3; row++ {
				line := lines[row+3]
				if strings.Contains(line, "pepeBoxer") {
					parts := strings.Split(line, ":")
					for i, part := range parts {
						if strings.Contains(part, "pepeBoxer") {
							col := (i - 1) / 2

							err := in.ClickButton(message, row, col)
							if err != nil {
								utils.Log(utils.Important, utils.Error, in.SafeGetUsername(),
									fmt.Sprintf("Failed to click punch pepe button: %s", err.Error()))
							}

							break
						}
					}
				}
			}
		} else if embed.Title == "Fish Guesser" || embed.Title == "Item Guesser" {
			re := regexp.MustCompile(`(\d+)\.(png|gif)$`)
			matches := re.FindStringSubmatch(embed.Image.URL)

			if matches == nil || len(matches) < 2 {
				utils.Log(utils.Important, utils.Error, in.SafeGetUsername(),
					"Failed to extract image ID from URL")
				return
			}

			imageId := matches[1]

			imageName, ok := emojis[imageId].(string)
			if !ok {
				utils.Log(utils.Important, utils.Error, in.SafeGetUsername(),
					fmt.Sprintf("Image ID %s not found in emojis map", imageId))
				return
			}

			err := in.SendChatMessage(strings.ToLower(imageName), true)
			if err != nil {
				utils.Log(utils.Important, utils.Error, in.SafeGetUsername(),
					fmt.Sprintf("Failed to send fish guesser chat message: %s", err.Error()))
			}
		} else if embed.Title == "Dice Champs" {
			err := in.ClickButton(message, 0, 0)
			if err != nil {
				utils.Log(utils.Important, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click dice champs button: %s", err.Error()))
			}
		}
	}

	// Non general random events color
	if strings.Contains(embed.Title, "says...") {
		if strings.Contains(embed.Footer.Text, "time limit") && in.Cfg.Commands.Fish.AutoCompleteTasks {
			components := message.Components[0].(*types.ActionsRow).Components
			if len(components) >= 2 && components[1].(*types.Button).Label == "Accept" {
				err := in.ClickButton(message, 0, 1)
				if err != nil {
					utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click accept task button: %s", err.Error()))
				}

			}
		} else if strings.Contains(embed.Footer.Text, "to trade the item") && in.Cfg.Commands.Fish.AutoCompleteTradeOffers {
			// Randomly click a button if button is not "Decline"
			validIndices := make([]int, 0)
			for i, cmp := range message.Components[0].(*types.ActionsRow).Components {
				btn, ok := cmp.(*types.Button)
				if !ok {
					continue
				}

				if btn.Label != "Decline" {
					validIndices = append(validIndices, i)
				}
			}

			if len(validIndices) > 0 {
				utils.Rng.Seed(time.Now().UnixNano())
				randomIndex := validIndices[utils.Rng.Intn(len(validIndices))]
				err := in.ClickButton(message, 0, randomIndex)
				if err != nil {
					utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click random task button: %s", err.Error()))
				}
			}
		} else if len(embed.Fields) > 0 && strings.Contains(embed.Fields[0].Name, "requests:") && in.Cfg.Commands.Fish.AutoCompleteTasks {
			components := message.Components[0].(*types.ActionsRow).Components
			if len(components) >= 2 {
				if components[1].(*types.Button).Label == "Accept" {
					err := in.ClickButton(message, 0, 0)
					if err != nil {
						utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click accept request button: %s", err.Error()))
					}
				}
			}
		}
	}
}
