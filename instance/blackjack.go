package instance

import (
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"regexp"
	"strconv"
	"strings"
)

func extractCardValues(emojiString string) []string {
	re := regexp.MustCompile(`<:bjFace([0-9JQKA]+)[RB]:[0-9]+>`)
	matches := re.FindAllStringSubmatch(emojiString, -1)

	cardValues := make([]string, 0, len(matches))
	for _, match := range matches {
		if len(match) > 1 {
			cardValues = append(cardValues, match[1])
		}
	}

	return cardValues
}

func bjFormula(dealer, player []string) int {
	dealerSum, _ := calculateSum(dealer)
	playerSum, isSoft := calculateSum(player)

	return bjNewStrategy(playerSum, dealerSum, len(player), isSoft)
}

func calculateSum(cards []string) (int, bool) {
	sum, hasAce := 0, false
	for _, card := range cards {
		value := 0
		switch card {
		case "A":
			value = 11
			hasAce = true
		case "K", "Q", "J":
			value = 10
		default:
			value, _ = strconv.Atoi(card)
		}
		sum += value
	}

	if hasAce && sum > 21 {
		sum -= 10
	}
	return sum, hasAce
}

func bjNewStrategy(playerSum, dealerSum, playerHand int, isSoft bool) int {
	if isSoft {
		switch {
		case playerSum <= 17:
			return 0 // Hit on soft 17 or lower
		case playerSum == 18 && dealerSum >= 9:
			return 0 // Hit on soft 18 against 9, T, A
		case playerSum >= 19:
			return 1 // Stand on soft 19 or higher
		default:
			return 1 // Stand on soft 18 against 2 through 8
		}
	}

	switch {
	case playerSum <= 11:
		return 0 // Hit on 11 or lower
	case playerSum == 12 && dealerSum >= 4 && dealerSum <= 6:
		return 1 // Stand on 12 against 4-6
	case playerSum == 12:
		return 0 // Hit on 12 against 2, 3, or 7+
	case playerSum <= 16 && dealerSum >= 7:
		return 0 // Hit against dealer 7+ for hard 13-16
	default:
		return 1 // Stand on 17 or higher
	}
}

func (in *Instance) handleButtonClick(message gateway.EventMessage, result int) {
	var err error
	switch result {
	case 0:
		err = in.ClickButton(message, 0, 0)
	case 1:
		err = in.ClickButton(message, 0, 1)
	case 2:
		err = in.ClickButton(message, 1, 0)
	}

	if err != nil {
		in.Log("others", "ERR", fmt.Sprintf("Blackjack minigame failed to click button: %s", err.Error()))
	}
}

func (in *Instance) BlackjackMessageCreate(message gateway.EventMessage) {
	embed := message.Embeds[0]
	if strings.Contains(embed.Author.Name, "Blackjack Game") {
		result := bjFormula(extractCardValues(embed.Fields[0].Value), extractCardValues(embed.Fields[1].Value))
		in.handleButtonClick(message, result)
	}
}

func (in *Instance) BlackjackMessageUpdate(message gateway.EventMessage) {
	embed := message.Embeds[0]
	if strings.Contains(embed.Author.Name, "Blackjack Game") &&
		!strings.Contains(message.Components[0].(*types.ActionsRow).Components[0].(*types.Button).Label, "Play Again") {

		result := bjFormula(extractCardValues(embed.Fields[0].Value), extractCardValues(embed.Fields[1].Value))
		in.handleButtonClick(message, result)
	}

	if netValue, err := extractNetValue(embed.Description); err == nil {
		in.Log("others", "INF", fmt.Sprintf("%s blackjack minigame with net value: %d", netResultMessage(netValue), netValue))
	}
}

func extractNetValue(description string) (int, error) {
	re := regexp.MustCompile(`Net:\s\*\*⏣ ([+\-]?[0-9,]+)\*\*`)
	matches := re.FindStringSubmatch(description)
	if len(matches) > 1 {
		return strconv.Atoi(strings.ReplaceAll(matches[1], ",", ""))
	}
	return 0, fmt.Errorf("no match found")
}

func netResultMessage(netValue int) string {
	switch {
	case netValue < 0:
		return "Lost"
	case netValue == 0:
		return "Drawn"
	default:
		return "Won"
	}
}
