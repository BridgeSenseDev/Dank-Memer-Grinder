package instance

import (
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"regexp"
	"strconv"
	"strings"
)

var wins, losses int

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

func calculateSum(cards []string) (int, bool) {
	sum, hasAce := 0, false
	aceCount := 0

	for _, card := range cards {
		value := 0
		switch card {
		case "A":
			value = 11
			aceCount++
			hasAce = true
		case "K", "Q", "J":
			value = 10
		default:
			value, _ = strconv.Atoi(card)
		}
		sum += value
	}

	for sum > 21 && aceCount > 0 {
		sum -= 10
		aceCount--
	}
	return sum, hasAce
}

func bjFormula(dealer, player []string, canSurrender, canDoubleDown bool, canSplit bool) int {
	playerSum, isSoft := calculateSum(player)

	return bjNewStrategy(player, dealer[0], playerSum, len(player), isSoft, canSurrender, canDoubleDown, canSplit)
}

func bjNewStrategy(playerCards []string, dealerCard string, playerSum, cardCount int, isSoft, canSurrender, canDoubleDown, canSplit bool) int {
	if len(playerCards) == 2 && playerCards[0] == playerCards[1] && canSplit {
		return handlePairs(playerCards[0], dealerCard, canDoubleDown)
	}

	if isSoft {
		return handleSoftHands(playerSum, dealerCard, cardCount, canDoubleDown)
	}

	return handleHardHands(playerSum, dealerCard, cardCount, canSurrender, canDoubleDown)
}

func handlePairs(playerCard, dealerCard string, canDoubleDown bool) int {
	switch playerCard {
	case "A", "8":
		// P
		return 3
	case "10":
		// S
		return 1
	case "9":
		// S
		if dealerCard == "7" || dealerCard == "10" || dealerCard == "A" {
			return 1
		}
		// P
		return 3
	case "7":
		// P
		if dealerCard >= "2" && dealerCard <= "7" {
			return 3
		}
		// H
		return 0
	case "6":
		// P
		if dealerCard >= "2" && dealerCard <= "6" {
			return 3
		}
		// H
		return 0
	case "5":
		// D
		if dealerCard >= "2" && dealerCard <= "9" && canDoubleDown {
			return 2
		}
		// H
		return 0
	case "4":
		// P
		if dealerCard == "5" || dealerCard == "6" {
			return 3
		}
		// H
		return 0
	case "2", "3":
		// P
		if dealerCard >= "2" && dealerCard <= "7" {
			return 3
		}
		// H
		return 0
	}
	return 0
}

func convertFaceCard(card string) string {
	switch card {
	case "K", "Q", "J":
		return "10"
	default:
		return card
	}
}

func handleSoftHands(playerSum int, dealerCard string, cardCount int, canDoubleDown bool) int {
	dealerCard = convertFaceCard(dealerCard)

	switch playerSum {
	case 20, 21:
		// S5
		if cardCount > 5 {
			return 0
		}
		return 1
	case 19:
		// S4
		if dealerCard == "10" {
			if cardCount > 4 {
				return 0
			}
			return 1
		}
		// S5
		if cardCount > 5 {
			return 0
		}
		return 1
	case 18:
		// S4
		if dealerCard == "2" || dealerCard == "8" {
			if cardCount > 4 {
				return 0
			}
			return 1
		}
		// DS4
		if dealerCard >= "3" && dealerCard <= "6" {
			if canDoubleDown {
				return 2
			}
			if cardCount > 4 {
				return 0
			}
			return 1
		}
		// S5
		if dealerCard == "7" {
			if cardCount > 5 {
				return 0
			}
			return 1
		}
		// H
		return 0
	case 17:
		// D
		if dealerCard >= "3" && dealerCard <= "6" && canDoubleDown {
			return 2
		}
		// H
		return 0
	case 16, 15:
		// D
		if dealerCard >= "4" && dealerCard <= "6" && canDoubleDown {
			return 2
		}
		// H
		return 0
	}
	// D
	if dealerCard == "5" || dealerCard == "6" {
		return 2
	}
	// H
	return 0
}

func handleHardHands(playerSum int, dealerCard string, cardCount int, canSurrender, canDoubleDown bool) int {
	dealerCard = convertFaceCard(dealerCard)

	switch {
	case playerSum >= 18:
		// S
		return 1
	case playerSum == 17:
		// S5
		if dealerCard >= "9" && cardCount > 5 {
			return 0
		}
		// S
		return 1
	case playerSum == 16:
		// S5
		if dealerCard == "2" || dealerCard == "3" {
			if cardCount > 5 {
				return 0
			}
			return 1
		}
		// S
		if dealerCard >= "4" && dealerCard <= "6" {
			return 1
		}
		// H
		if dealerCard == "7" || dealerCard == "8" {
			return 0
		}
		// R
		if dealerCard == "9" || dealerCard == "A" {
			if canSurrender {
				return 4
			}
			return 0
		}
		// Rs
		if dealerCard == "10" {
			if canSurrender {
				return 4
			}
			return 1
		}
	case playerSum == 15:
		// S5
		if dealerCard >= "2" && dealerCard <= "6" {
			if cardCount > 5 {
				return 0
			}
			return 1
		}
		// H
		if (dealerCard >= "7" && dealerCard <= "9") || dealerCard == "A" {
			return 0
		}
		// R
		if dealerCard == "10" {
			if canSurrender {
				return 4
			}
			return 0
		}
	case playerSum == 14:
		// S5
		if dealerCard >= "2" && dealerCard <= "6" {
			if cardCount > 5 {
				return 0
			}
			return 1
		}
		// H
		return 0
	case playerSum == 13:
		// S4
		if dealerCard == "2" || dealerCard == "3" {
			if cardCount > 4 {
				return 0
			}
			return 1
		}
		// S5
		if dealerCard >= "4" && dealerCard <= "6" {
			if cardCount > 4 {
				return 0
			}
			return 1
		}
		// H
		return 0
	case playerSum == 12:
		// H
		if dealerCard == "2" || dealerCard == "3" {
			return 0
		}
		// S4
		if dealerCard >= "4" && dealerCard <= "6" {
			if cardCount > 4 {
				return 0
			}
			return 1
		}
		// H
		return 0
	case playerSum == 11:
		// D
		if dealerCard != "A" && canDoubleDown {
			return 2
		}
		// H
		return 0
	case playerSum == 10:
		// D
		if dealerCard != "A" && dealerCard != "10" && canDoubleDown {
			return 2
		}
		// H
		return 0
	case playerSum == 9:
		// D
		if dealerCard >= "3" && dealerCard <= "6" && canDoubleDown {
			return 2
		}
		// H
		return 0
	default:
		// H
		return 0
	}
	return 0
}

func (in *Instance) handleButtonClick(message gateway.EventMessage, result int) {
	var err error
	switch result {
	case 0:
		err = in.ClickButton(message, 0, 0)
	case 1:
		err = in.ClickButton(message, 0, 1)
	case 2:
		err = in.ClickButton(message, 0, 2)
	case 3:
		err = in.ClickButton(message, 0, 3)
	case 4:
		err = in.ClickButton(message, 1, 0)
	}

	if err != nil {
		in.Log("others", "ERR", fmt.Sprintf("Blackjack minigame failed to click button: %s", err.Error()))
	}
}

func (in *Instance) BlackjackMessageCreate(message gateway.EventMessage) {
	in.handleBlackjackMessage(message)
}

func (in *Instance) BlackjackMessageUpdate(message gateway.EventMessage) {
	in.handleBlackjackMessage(message)

	embed := message.Embeds[0]
	var result string
	switch embed.Color {
	case 15022389:
		result = "Lost"
		losses++
	case 16447559:
		result = "Tied"
	case 5025616:
		result = "Won"
		wins++
	default:
		result = ""
	}

	if result != "" {
		netValue, err := extractNetValue(embed.Description)
		if err != nil {
			in.Log("others", "ERR", fmt.Sprintf("Failed to extract net value: %s", err.Error()))
			return
		}

		totalGames := wins + losses
		winPercentage := 0.0
		if totalGames > 0 {
			winPercentage = (float64(wins) / float64(totalGames)) * 100
		}

		in.Log("others", "INF", fmt.Sprintf("%s blackjack minigame with net value: %d, Win %%: %.1f", result, netValue, winPercentage))
	}
}

func (in *Instance) handleBlackjackMessage(message gateway.EventMessage) {
	embed := message.Embeds[0]

	if strings.Contains(embed.Author.Name, "Blackjack Game") && embed.Color == 2829617 {
		var playerHandField types.EmbedField
		for _, field := range embed.Fields {
			if strings.Contains(field.Name, "(Player)") {
				playerHandField = field
				break
			}
		}

		if playerHandField.Name == "" {
			return
		}

		dealerCards := extractCardValues(embed.Fields[0].Value)
		playerCards := extractCardValues(playerHandField.Value)

		canSurrender := false
		canDoubleDown := false
		canSplit := false

		if len(message.Components) > 1 {
			if surrenderRow, ok := message.Components[1].(*types.ActionsRow); ok {
				if len(surrenderRow.Components) > 0 {
					var surrenderButton *types.Button
					if surrenderButton, ok = surrenderRow.Components[0].(*types.Button); ok {
						canSurrender = !surrenderButton.Disabled
					}
				}
			}
		}

		if len(message.Components) > 0 {
			if actionRow, ok := message.Components[0].(*types.ActionsRow); ok {
				if len(actionRow.Components) > 3 {
					var splitButton *types.Button
					if splitButton, ok = actionRow.Components[3].(*types.Button); ok {
						canSplit = !splitButton.Disabled
					}
				}

				if len(actionRow.Components) > 2 {
					var doubleButton *types.Button
					if doubleButton, ok = actionRow.Components[2].(*types.Button); ok {
						canDoubleDown = !doubleButton.Disabled
					}
				}
			}
		}

		result := bjFormula(dealerCards, playerCards, canSurrender, canDoubleDown, canSplit)

		in.handleButtonClick(message, result)
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
