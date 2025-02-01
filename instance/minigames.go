package instance

import (
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"regexp"
	"strconv"
	"strings"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
)

var (
	emoji                       = ""
	colorMatchOptions           = make(map[string]string)
	repeatOrder                 []string
	repeatOrderLastClickedIndex int
	wordRegex                   = regexp.MustCompile(`(.+?)`)
	colorRegex                  = regexp.MustCompile(`:([^:]+):`)
	highlowRegex                = regexp.MustCompile(`\*\*(.*?)\*\*`)
)

const (
	emptyspace        = "<:emptyspace:827651824739156030>"
	levitate          = ":levitate:"
	basketball        = ":basketball:"
	fireBall          = "<:FireBall:883714770748964864>"
	worm              = "<:Worm:864261394920898600>"
	PinkBits          = "<:PinkBits:975398146152738906>"
	PinkSludgeMonster = "<:PinkSludgeMonster:1127334051422937240>"
)

func generateEmojiActions(emojis []string) map[string]int {
	emojiActions := make(map[string]int)
	for _, emoji := range emojis {
		if emoji == levitate {
			// Miss the goalkeeper
			emojiActions[emoji] = 2
			emojiActions[emptyspace+emoji] = 2
			emojiActions[emptyspace+emptyspace+emoji] = 0
		} else if emoji == fireBall || emoji == worm || emoji == PinkBits {
			// Dodge the fireball / dodge the worm // dodge the pink bits
			emojiActions["# "+emptyspace+emoji] = 2
			emojiActions["# "+emptyspace+emptyspace+emoji] = 2
			emojiActions["# "+
				emptyspace+emptyspace+emptyspace+emoji] = 0
		} else {
			emojiActions[emoji] = 0
			emojiActions[emptyspace+emoji] = 1
			emojiActions[emptyspace+emptyspace+emoji] = 2
		}
	}
	return emojiActions
}

func (in *Instance) solveMinigame(message gateway.EventMessage, gameName string, gameTrigger string, emojis []string) {
	embed := message.Embeds[0]

	if strings.Contains(embed.Description, gameTrigger) {
		in.Log("others", "INF", fmt.Sprintf("Solving %s minigame", gameName))
		gameActions := generateEmojiActions(emojis)
		for emoji, button := range gameActions {
			if strings.Split(embed.Description, "\n")[2] == emoji {
				err := in.ClickButton(message, 0, button)
				if err != nil {
					in.Log("discord", "ERR", fmt.Sprintf("Failed to click %s minigame button", gameName))
				}
				break
			}
		}
		in.Log("others", "INF", fmt.Sprintf("Solved %s minigame", gameName))
	}
}

func (in *Instance) MinigamesMessageCreate(message gateway.EventMessage) {
	embed := message.Embeds[0]

	// Dragon
	in.solveMinigame(message, "Dragon", "Dodge the Dragon's Fireball", []string{fireBall})

	// Pink sludge monster
	in.solveMinigame(message, "Pink Sludge Monster", "Dodge the Sludge Monster's Pink Bits", []string{PinkBits})

	// Moleman
	in.solveMinigame(message, "Moleman", "Dodge the Moleman's Worm", []string{worm})

	// Attack boss
	if strings.Contains(embed.Description, "Attack the boss by clicking") {
		in.Log("others", "INF", "Solving attack boss minigame")
		in.PauseCommands(false)
		err := in.ClickButton(message, 0, 0)
		if err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to click attack boss minigame button: %s", err.Error()))
		}
		return
	}

	// Emoji match
	if strings.Contains(embed.Description, "Look at the emoji closely!") {
		in.PauseCommands(false)
		in.Log("others", "INF", "Solving emoji minigame")

		lines := strings.Split(embed.Description, "\n")
		emoji = lines[1]
	}

	// Color match
	if strings.Contains(embed.Description, "Look at each color next to the words closely!") {
		in.PauseCommands(false)
		in.Log("others", "INF", "Solving color match minigame")

		lines := strings.Split(embed.Description, "\n")[1:]

		for _, line := range lines {
			matchWord := wordRegex.FindStringSubmatch(line)
			matchColor := colorRegex.FindStringSubmatch(line)

			if len(matchWord) > 1 && len(matchColor) > 1 {
				colorMatchOptions[matchWord[1]] = matchColor[1]
			}
		}
	}

	// Repeat order
	if strings.Contains(embed.Description, "Repeat Order") ||
		strings.Contains(embed.Description, "word order.") ||
		strings.Contains(embed.Description, "words order") {
		in.Log("others", "INF", "Solving repeat order minigame")
		in.PauseCommands(false)

		lines := strings.Split(embed.Description, "\n")[1:6]
		repeatOrder = make([]string, len(lines))
		for i, line := range lines {
			repeatOrder[i] = strings.Trim(line, "`")
		}
		repeatOrderLastClickedIndex = 0
	}

	// F in the chat
	if embed.Description == "F" {
		err := in.ClickButton(message, 0, 0)
		if err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to click F in the chat minigame button: %s", err.Error()))
		}
		in.Log("others", "INF", "Solved F in the chat minigame")
	}

	// HighLow
	if strings.Contains(embed.Description, "I just chose a secret number") && message.Interaction.Name != "highlow" {
		matches := highlowRegex.FindStringSubmatch(embed.Description)
		if len(matches) > 1 {
			numStr := matches[1]
			num, _ := strconv.Atoi(numStr)

			if num >= 50 {
				err := in.ClickButton(message, 0, 0)
				if err != nil {
					in.Log("discord", "ERR", fmt.Sprintf("Failed to click highlow minigame button: %s", err.Error()))
				}
			} else {
				err := in.ClickButton(message, 0, 2)
				if err != nil {
					in.Log("discord", "ERR", fmt.Sprintf("Failed to click highlow minigame button: %s", err.Error()))
				}
			}

			in.Log("others", "INF", "Solved highlow minigame")
		} else {
			in.Log("others", "ERR", "Failed to solve highlow minigame")
		}
	}
}

func (in *Instance) MinigamesMessageUpdate(message gateway.EventMessage) {
	embed := message.Embeds[0]

	// Football
	in.solveMinigame(message, "Football", "Hit the ball!", []string{levitate})

	// Basketball
	in.solveMinigame(message, "Basketball", "Dunk the ball!", []string{basketball})

	// Attack boss
	if strings.Contains(embed.Description, "Attack the boss by clicking") {
		if !message.Components[0].(*types.ActionsRow).Components[0].(*types.Button).Disabled {
			err := in.ClickButton(message, 0, 0)
			if err != nil {
				in.Log("discord", "ERR", fmt.Sprintf("Failed to click attack boss minigame button: %s", err.Error()))
			}
		} else {
			in.Log("others", "INF", "Solved attack boss minigame")
			in.UnpauseCommands()
			return
		}
	}

	// Emoji match
	if strings.Contains(embed.Description, "What was the emoji?") {
		for rowIndex, row := range message.Components {
			for columnIndex, button := range row.(*types.ActionsRow).Components {
				if button.(*types.Button).Emoji.Name == emoji {
					err := in.ClickButton(message, rowIndex, columnIndex)
					if err != nil {
						in.Log("discord", "ERR", fmt.Sprintf("Failed to click emoji match minigame button: %s", err.Error()))
					}
					in.Log("others", "INF", "Solved emoji minigame")
					in.UnpauseCommands()
				}
			}
		}
	}

	// Color match
	if strings.Contains(embed.Description, "What color was next to the word") {
		matches := wordRegex.FindStringSubmatch(embed.Description)
		if len(matches) > 1 {
			word := matches[1]
			color := colorMatchOptions[word]

			for columnIndex, button := range message.Components[0].(*types.ActionsRow).Components {
				if button.(*types.Button).Label == color {
					err := in.ClickButton(message, 0, columnIndex)
					if err != nil {
						in.Log("discord", "ERR", fmt.Sprintf("Failed to click color match minigame button: %s", err.Error()))
					}
					break
				}
			}

			in.UnpauseCommands()
			in.Log("others", "INF", "Solved color match minigame")
		} else {
			in.Log("others", "ERR", "Failed to solve color match minigame")
		}
	}

	// Repeat order
	if strings.Contains(embed.Description, "Click the buttons in correct order") {
		answers := make(map[string]int)
		for i, button := range message.Components[0].(*types.ActionsRow).Components {
			answers[button.(*types.Button).Label] = i
		}

		if repeatOrderLastClickedIndex < len(repeatOrder) {
			choice := repeatOrder[repeatOrderLastClickedIndex]
			err := in.ClickButton(message, 0, answers[choice])
			if err != nil {
				in.Log("discord", "ERR", fmt.Sprintf("Failed to click repeat order minigame button: %s", err.Error()))
			} else {
				repeatOrderLastClickedIndex++
				if repeatOrderLastClickedIndex >= len(repeatOrder) {
					in.Log("others", "INF", "Solved repeat order minigame")
					in.UnpauseCommands()
				}
			}
		}
	}
}
