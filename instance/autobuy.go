package instance

import (
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
)

type AutoBuyState struct {
	shopTypeIndex int
	count         int
	itemEmojiName string
	price         int
}

var globalAutoBuyState = AutoBuyState{
	shopTypeIndex: 0,
	count:         0,
	itemEmojiName: "",
	price:         0,
}

type AutoBuyResult struct {
	Success bool
	Message string
}

func (in *Instance) setAutoBuyState(shopTypeIndex, count int, itemEmojiName string, price int) {
	globalAutoBuyState.shopTypeIndex = shopTypeIndex
	globalAutoBuyState.count = count
	globalAutoBuyState.itemEmojiName = itemEmojiName
	globalAutoBuyState.price = price
}

func (in *Instance) findAndClickButton(message gateway.EventMessage, targetEmojiName string) bool {
	for rowIndex, component := range message.Components {
		if rowIndex == 0 || rowIndex == 3 {
			continue
		}
		for columnIndex, button := range component.(*types.ActionsRow).Components {
			if button.(*types.Button).Emoji.Name == targetEmojiName {
				if button.(*types.Button).Disabled {
					return false
				}

				err := in.ClickButton(message, rowIndex, columnIndex)
				if err != nil {
					utils.Log(utils.Others, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click autobuy button: %s", err.Error()))
				}
				return true
			}
		}
	}

	return false
}

func (in *Instance) shopBuy(shopMsg gateway.EventMessage) {
	shopTypeOptions := shopMsg.Components[0].(*types.ActionsRow).Components[0].(*types.SelectMenu).Options
	if !shopTypeOptions[globalAutoBuyState.shopTypeIndex].Default {
		err := in.ChooseSelectMenu(shopMsg, 0, 0, []string{shopTypeOptions[globalAutoBuyState.shopTypeIndex].Value})
		if err != nil {
			utils.Log(utils.Others, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to choose shop view select menu: %s", err.Error()))
		}
	} else {
		if globalAutoBuyState.price != 0 {
			re := regexp.MustCompile(`<:Coin:\d+>\s+([0-9,]+)`)
			matches := re.FindStringSubmatch(shopMsg.Embeds[0].Description)
			if len(matches) < 2 {
				utils.Log(utils.Others, utils.Error, in.SafeGetUsername(), "Failed to find coins in shop message")
				return
			}

			coins, err := strconv.Atoi(strings.ReplaceAll(matches[1], ",", ""))
			if err != nil {
				utils.Log(utils.Others, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to parse coins: %s", err.Error()))
				return
			}

			if coins < globalAutoBuyState.price {
				in.AutoBuyResultChan <- AutoBuyResult{
					Success: false,
					Message: "Not enough coins",
				}
				return
			}
		}

		if !in.findAndClickButton(shopMsg, globalAutoBuyState.itemEmojiName) {
			err := in.ClickButton(shopMsg, 3, 1)
			if err != nil {
				utils.Log(utils.Others, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click next autobuy page button: %s", err.Error()))
			}
		}
	}
}

func (in *Instance) StartAutoBuy(command string, subCommand string) <-chan AutoBuyResult {
	in.AutoBuyResultChan = make(chan AutoBuyResult, 1)

	if globalAutoBuyState.itemEmojiName == "" {
		in.AutoBuyResultChan <- AutoBuyResult{
			Success: false,
			Message: "No item set for autobuy",
		}
		return in.AutoBuyResultChan
	}

	in.PauseCommands(false)
	utils.Log(utils.Others, utils.Info, in.SafeGetUsername(), fmt.Sprintf("Auto buying %s", globalAutoBuyState.itemEmojiName))

	if globalAutoBuyState.price != 0 {
		err := in.SendCommand("withdraw", map[string]string{"amount": strconv.Itoa(globalAutoBuyState.price)}, true)
		if err != nil {
			utils.Log(utils.Others, utils.Error, in.SafeGetUsername(),
				fmt.Sprintf("Failed to send autobuy /withdraw command: %s", err.Error()))
			in.AutoBuyResultChan <- AutoBuyResult{
				Success: false,
				Message: "Failed to withdraw funds",
			}
			return in.AutoBuyResultChan
		}

		<-utils.Sleep(1 * time.Second)
	}

	err := in.SendSubCommand(command, subCommand, nil, true)
	if err != nil {
		utils.Log(utils.Others, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to send /%s %s command: %s", command, subCommand, err.Error()))
		in.AutoBuyResultChan <- AutoBuyResult{
			Success: false,
			Message: fmt.Sprintf("Failed to send /%s %s command: %s", command, subCommand, err.Error()),
		}
		return in.AutoBuyResultChan
	}
	return in.AutoBuyResultChan
}

func (in *Instance) AutoBuyMessageUpdate(message gateway.EventMessage) {
	embed := message.Embeds[0]

	if embed.Title == "Dank Memer Shop" && globalAutoBuyState.itemEmojiName != "" {
		if strings.Contains(embed.Footer.Text, "Page 1") {
			utils.Log(utils.Others, utils.Error, in.SafeGetUsername(), "Failed to find autobuy button")
			in.setAutoBuyState(0, 0, "", 0)
			in.UnpauseCommands()
			return
		}

		in.shopBuy(message)
	}
}

func (in *Instance) AutoBuyMessageCreate(message gateway.EventMessage) {
	embed := message.Embeds[0]
	if strings.Contains(embed.Description, "You don't have a shovel") && in.Cfg.AutoBuy.Shovel.State {
		in.setAutoBuyState(0, 1, "IronShovel", 50000)
	} else if strings.Contains(embed.Description, "You don't have a hunting rifle") && in.Cfg.AutoBuy.HuntingRifle.State {
		in.setAutoBuyState(0, 1, "LowRifle", 50000)
	} else if embed.Title == "Your lifesaver protected you!" && in.Cfg.AutoBuy.LifeSavers.State {
		re := regexp.MustCompile(`You have (\d+) Life Saver left`)
		match := re.FindStringSubmatch(message.Components[0].(*types.ActionsRow).Components[0].(*types.Button).Label)
		fmt.Println(match)
		if len(match) > 1 {
			remaining, err := strconv.Atoi(match[1])
			if err != nil {
				utils.Log(utils.Important, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to determine amount of lifesavers required: %s", err.Error()))
			}

			required := in.Cfg.AutoBuy.LifeSavers.Amount

			if remaining < required {
				in.setAutoBuyState(0, required-remaining, "LifeSaver", (required-remaining)*250000)
			}
		} else {
			utils.Log(utils.Important, utils.Error, in.SafeGetUsername(), "Failed to determine amount of lifesavers required")
		}
	} else if embed.Title == "You died!" {
		in.setAutoBuyState(0, in.Cfg.AutoBuy.LifeSavers.Amount, "LifeSaver", in.Cfg.AutoBuy.LifeSavers.Amount*250000)
	} else if embed.Title == "Pending Confirmation" {
		if strings.Contains(embed.Description, "Would you like to use your **<:Coupon:977969734307971132> Shop Coupon**") {
			err := in.ClickButton(message, 0, 0)
			if err != nil {
				utils.Log(utils.Important, utils.Error, in.SafeGetUsername(), "Failed to click decline shop coupon button")
			}
		} else if strings.Contains(embed.Description, "Are you sure you want to buy") {
			err := in.ClickButton(message, 0, 1)
			if err != nil {
				utils.Log(utils.Important, utils.Error, in.SafeGetUsername(), "Failed to click shop buy confirmation button")
			}
		}
		return
	} else if embed.Title == "Dank Memer Shop" && globalAutoBuyState.itemEmojiName != "" {
		in.shopBuy(message)
		return
	} else {
		return
	}

	resultChan := in.StartAutoBuy("shop", "view")

	go func() {
		select {
		case result := <-resultChan:
			utils.Log(utils.Others, utils.Info, in.SafeGetUsername(), result.Message)
		case <-time.After(45 * time.Second):
			utils.Log(utils.Others, utils.Info, in.SafeGetUsername(), "Autobuy timed out")
			in.UnpauseCommands()
		}
	}()
}

func (in *Instance) AutoBuyModalCreate(modal gateway.EventModalCreate) {
	if modal.Title == "Dank Memer Shop" {
		if globalAutoBuyState.count != 0 {
			modal.Components[0].(*types.ActionsRow).Components[0].(*types.TextInput).Value = strconv.Itoa(globalAutoBuyState.count)
			err := in.SubmitModal(modal)
			if err != nil {
				utils.Log(utils.Others, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to submit autobuy modal: %s", err.Error()))
				in.AutoBuyResultChan <- AutoBuyResult{
					Success: false,
					Message: "Failed to submit autobuy modal",
				}
				return
			}

			in.AutoBuyResultChan <- AutoBuyResult{
				Success: true,
				Message: fmt.Sprintf("Successfully bought %s", globalAutoBuyState.itemEmojiName),
			}

			in.setAutoBuyState(0, 0, "", 0)
			in.UnpauseCommands()
		}
	}
}
