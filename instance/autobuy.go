package instance

import (
	"errors"
	"fmt"
	"regexp"
	"strconv"
	"strings"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
)

type AutoBuyState struct {
	shopTypeIndex int
	shopPage      int
	count         int
	itemEmojiName string
}

var globalAutoBuyState = AutoBuyState{
	shopTypeIndex: 0,
	shopPage:      0,
	count:         0,
	itemEmojiName: "",
}

func (in *Instance) setAutoBuyState(shopTypeIndex, shopPage, count int, itemEmojiName string) {
	globalAutoBuyState.shopTypeIndex = shopTypeIndex
	globalAutoBuyState.shopPage = shopPage
	globalAutoBuyState.count = count
	globalAutoBuyState.itemEmojiName = itemEmojiName
}

func determineDirection(currentPage, targetPage, totalPages int) int {
	current := currentPage % totalPages
	if current == 0 {
		current = totalPages
	}

	forwardDistance := targetPage - current
	backwardDistance := current - targetPage
	if backwardDistance < 0 {
		backwardDistance += totalPages
	}

	if forwardDistance <= backwardDistance {
		return 1
	} else {
		return 0
	}
}

func (in *Instance) findAndClickButton(message *types.MessageEventData, targetEmojiName string) bool {
	for rowIndex, component := range message.Components {
		if rowIndex == 0 || rowIndex == 3 {
			continue
		}
		for columnIndex, button := range component.(*types.ActionsRow).Components {
			if button.(*types.Button).Emoji.Name == targetEmojiName {
				err := in.Client.ClickButton(message.MessageData, rowIndex, columnIndex)
				if err != nil {
					in.Log("discord", "ERR", fmt.Sprintf("Failed to click autobuy button: %s", err.Error()))
				}
				return true
			}
		}
	}
	return false
}

func parsePageInfo(footerText string) (currentPage, totalPages int, err error) {
	re := regexp.MustCompile(`Page (\d+) of (\d+)`).FindStringSubmatch(footerText)
	if len(re) > 2 {
		currentPage, err = strconv.Atoi(re[1])
		if err != nil {
			return 0, 0, err
		}
		totalPages, err = strconv.Atoi(re[2])
		if err != nil {
			return 0, 0, err
		}
	} else {
		return 0, 0, errors.New("failed to parse page info")
	}
	return currentPage, totalPages, nil
}

func (in *Instance) shopBuy(shopMsg *types.MessageEventData) {
	if shopMsg.Embeds[0].Title != "Dank Memer Shop" || globalAutoBuyState.itemEmojiName == "" {
		return
	}

	shopTypeOptions := shopMsg.Components[0].(*types.ActionsRow).Components[0].(*types.SelectMenu).Options
	if !shopTypeOptions[globalAutoBuyState.shopTypeIndex].Default {
		err := in.Client.ChooseSelectMenu(shopMsg.MessageData, 0, 0, []string{shopTypeOptions[globalAutoBuyState.shopTypeIndex].Value})
		if err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to choose shop view select menu: %s", err.Error()))
		}
	} else {
		currentPage, totalPages, err := parsePageInfo(shopMsg.Embeds[0].Footer.Text)
		if err != nil {
			in.Log("others", "ERR", fmt.Sprintf("Failed to buy %s: %s", globalAutoBuyState.itemEmojiName, err.Error()))
		}

		if currentPage == globalAutoBuyState.shopPage {
			if !in.findAndClickButton(shopMsg, globalAutoBuyState.itemEmojiName) {
				if err != nil {
					in.Log("others", "ERR", fmt.Sprintf("Failed to buy %s: Could not find button in page %d", globalAutoBuyState.itemEmojiName, globalAutoBuyState.shopPage))
				}
			}
		} else {
			err := in.Client.ClickButton(shopMsg.MessageData, 3, determineDirection(currentPage, globalAutoBuyState.shopPage, totalPages))
			if err != nil {
				in.Log("discord", "ERR", fmt.Sprintf("Failed to click next autobuy page button: %s", err.Error()))
			}
		}
	}
}

func (in *Instance) AutoBuyMessageUpdate(message *types.MessageEventData) {
	in.shopBuy(message)
}

func (in *Instance) AutoBuyMessageCreate(message *types.MessageEventData) {
	embed := message.Embeds[0]
	if strings.Contains(embed.Description, "You don't have a shovel") && in.Cfg.AutoBuy.Shovel {
		in.setAutoBuyState(0, 1, 1, "IronShovel")
	} else if strings.Contains(embed.Description, "You don't have a hunting rifle") && in.Cfg.AutoBuy.HuntingRifle {
		in.setAutoBuyState(0, 1, 1, "LowRifle")
	} else {
		in.shopBuy(message)
		return
	}

	in.Log("others", "INF", fmt.Sprintf("Auto buying %s", globalAutoBuyState.itemEmojiName))
	err := in.Client.SendSubCommand("shop", "view", nil)

	if err != nil {
		in.Log("discord", "ERR", fmt.Sprintf("Failed to send /shop view command: %s", err.Error()))
	}
}

func (in *Instance) AutoBuyModalCreate(modal *types.ModalData) {
	if modal.Title == "Dank Memer Shop" {
		modal.Components[0].(*types.ActionsRow).Components[0].(*types.TextInput).Label = strconv.Itoa(globalAutoBuyState.count)
		err := in.Client.SubmitModal(*modal)
		if err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to submit autobuy modal: %s", err.Error()))
		}
		in.Log("others", "INF", fmt.Sprintf("Auto bought %s", globalAutoBuyState.itemEmojiName))
		in.setAutoBuyState(0, 0, 0, "")
	}
}
