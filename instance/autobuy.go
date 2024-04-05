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
	price         int
}

var globalAutoBuyState = AutoBuyState{
	shopTypeIndex: 0,
	shopPage:      0,
	count:         0,
	itemEmojiName: "",
}

func (in *Instance) setAutoBuyState(shopTypeIndex, shopPage, count int, itemEmojiName string, price int) {
	globalAutoBuyState.shopTypeIndex = shopTypeIndex
	globalAutoBuyState.shopPage = shopPage
	globalAutoBuyState.count = count
	globalAutoBuyState.itemEmojiName = itemEmojiName
	globalAutoBuyState.price = price
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
				err := in.ClickButton(message.MessageData, rowIndex, columnIndex)
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
	shopTypeOptions := shopMsg.Components[0].(*types.ActionsRow).Components[0].(*types.SelectMenu).Options
	if !shopTypeOptions[globalAutoBuyState.shopTypeIndex].Default {
		err := in.ChooseSelectMenu(shopMsg.MessageData, 0, 0, []string{shopTypeOptions[globalAutoBuyState.shopTypeIndex].Value})
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
			err := in.ClickButton(shopMsg.MessageData, 3, determineDirection(currentPage, globalAutoBuyState.shopPage, totalPages))
			if err != nil {
				in.Log("discord", "ERR", fmt.Sprintf("Failed to click next autobuy page button: %s", err.Error()))
			}
		}
	}
}

func (in *Instance) AutoBuyMessageUpdate(message *types.MessageEventData) {
	if message.Embeds[0].Title == "Dank Memer Shop" && globalAutoBuyState.itemEmojiName != "" {
		in.shopBuy(message)
	}
}

func (in *Instance) AutoBuyMessageCreate(message *types.MessageEventData) {
	embed := message.Embeds[0]
	if strings.Contains(embed.Description, "You don't have a shovel") && in.Cfg.AutoBuy.Shovel.State {
		in.setAutoBuyState(0, 1, 1, "IronShovel", 50000)
	} else if strings.Contains(embed.Description, "You don't have a hunting rifle") && in.Cfg.AutoBuy.HuntingRifle.State {
		in.setAutoBuyState(0, 1, 1, "LowRifle", 50000)
	} else if embed.Title == "Your lifesaver protected you!" && in.Cfg.AutoBuy.LifeSavers.State {
		re := regexp.MustCompile(`You have (\d+)x Life Saver left`)
		match := re.FindStringSubmatch(message.Components[0].(*types.ActionsRow).Components[0].(*types.Button).Label)

		if len(match) > 1 {
			remaining, err := strconv.Atoi(match[1])
			if err != nil {
				in.Log("important", "ERR", fmt.Sprintf("Failed to determine amount of lifesavers required: %s", err.Error()))
			}

			required := in.Cfg.AutoBuy.LifeSavers.Amount

			if remaining < required {
				in.setAutoBuyState(0, 1, required-remaining, "LifeSaver", (required-remaining)*250000)
			}
		} else {
			in.Log("important", "ERR", "Failed to determine amount of lifesavers required")
		}
	} else if embed.Title == "You died!" {
		in.setAutoBuyState(0, 1, in.Cfg.AutoBuy.LifeSavers.Amount, "LifeSaver", in.Cfg.AutoBuy.LifeSavers.Amount*250000)
	} else if embed.Title == "Pending Confirmation" {
		if strings.Contains(embed.Description, "Would you like to use your **<:Coupon:977969734307971132> Shop Coupon**") {
			in.ClickButton(message.MessageData, 0, 0)
		} else if strings.Contains(embed.Description, "Are you sure you want to buy") {
			in.ClickButton(message.MessageData, 0, 1)
		}
		return
	} else if message.Embeds[0].Title == "Dank Memer Shop" && globalAutoBuyState.itemEmojiName != "" {
		in.shopBuy(message)
		return
	} else {
		return
	}

	if globalAutoBuyState.itemEmojiName == "" {
		return
	}

	in.PauseCommands(false)
	in.Log("others", "INF", fmt.Sprintf("Auto buying %s", globalAutoBuyState.itemEmojiName))

	err := in.SendCommand("withdraw", map[string]string{"amount": strconv.Itoa(globalAutoBuyState.price)})
	if err != nil {
		in.Log("discord", "ERR", fmt.Sprintf("Failed to send autobuy /withdraw command: %s", err.Error()))
	}

	err = in.SendSubCommand("shop", "view", nil)
	if err != nil {
		in.Log("discord", "ERR", fmt.Sprintf("Failed to send /shop view command: %s", err.Error()))
	}
}

func (in *Instance) AutoBuyModalCreate(modal *types.ModalData) {
	if modal.Title == "Dank Memer Shop" {
		modal.Components[0].(*types.ActionsRow).Components[0].(*types.TextInput).Label = strconv.Itoa(globalAutoBuyState.count)
		err := in.SubmitModal(*modal)
		if err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to submit autobuy modal: %s", err.Error()))
		}
		in.Log("others", "INF", fmt.Sprintf("Auto bought %s", globalAutoBuyState.itemEmojiName))
		in.setAutoBuyState(0, 0, 0, "", 0)
		in.UnpauseCommands()
	}
}
