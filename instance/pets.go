package instance

import (
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"regexp"
	"strconv"
	"strings"
)

func (in *Instance) getRequiredAction(fields []types.EmbedField) int {
	for i, field := range fields {
		re := regexp.MustCompile(`\s(\d+)%`)
		matches := re.FindStringSubmatch(field.Value)

		if len(matches) < 2 {
			return 3
		}

		percentage, err := strconv.Atoi(matches[1])
		if err != nil {
			return 3
		}

		if percentage <= 90 {
			return i
		}
	}

	return 3
}

func getNextPet(petsChooseMenu *types.SelectMenu) int {
	for i, option := range petsChooseMenu.Options {
		if option.Default {
			if len(petsChooseMenu.Options) > i+1 {
				return i + 1
			} else {
				return 0
			}
		}
	}

	return 0
}

func (in *Instance) handlePetsCare(message gateway.EventMessage) {
	embed := message.Embeds[0]
	petsChooseMenu := message.Components[0].(*types.ActionsRow).Components[0].(*types.SelectMenu)
	nextPet := getNextPet(petsChooseMenu)

	if message.Components[1].(*types.ActionsRow).Components[0].(*types.Button).Disabled {
		if nextPet != 0 {
			err := in.ChooseSelectMenu(message, 0, 0, []string{petsChooseMenu.Options[nextPet].Value})
			if err != nil {
				in.Log("discord", "ERR", fmt.Sprintf("Failed to choose pets menu: %s", err.Error()))
			}
		} else {
			in.UnpauseCommands()
			return
		}
	}

	requiredAction := in.getRequiredAction(embed.Fields)
	if requiredAction != 3 {
		err := in.ClickButton(message, 1, requiredAction)
		if err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to click pets button: %s", err.Error()))
		}
	} else {
		for i := 0; i < 3; i++ {
			err := in.ClickButton(message, 2, i)
			if err != nil {
				in.Log("discord", "ERR", fmt.Sprintf("Failed to click pets button: %s", err.Error()))
			}
		}

		if nextPet != 0 {
			err := in.ChooseSelectMenu(message, 0, 0, []string{petsChooseMenu.Options[nextPet].Value})
			if err != nil {
				in.Log("discord", "ERR", fmt.Sprintf("Failed to choose pets menu: %s", err.Error()))
			}
		} else {
			in.UnpauseCommands()
		}
	}
}

func (in *Instance) PetsMessageCreate(message gateway.EventMessage) {
	if strings.Split(message.Interaction.Name, " ")[1] != "care" {
		return
	}

	in.PauseCommands(false)
	in.handlePetsCare(message)
}

func (in *Instance) PetsMessageUpdate(message gateway.EventMessage) {
	if strings.Split(message.Interaction.Name, " ")[1] != "care" {
		return
	}

	in.handlePetsCare(message)
}
