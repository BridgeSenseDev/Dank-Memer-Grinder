package discord

import (
	"encoding/json"
	"fmt"
	"math/big"
	"time"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
)

func generateNonce() string {
	now := time.Now().UnixNano() / int64(time.Millisecond)
	a := now - 1420070400000
	r := big.NewInt(a)
	r.Lsh(r, 22)
	return r.String()
}

func (client *Client) GetCommandInfo(commandName string) *CommandData {
	for _, cmd := range *client.CommandsData {
		if cmd.Name == commandName {
			return &cmd
		}
	}
	client.Log("ERR", fmt.Sprintf("Command %s not found", commandName))
	return nil
}

func (client *Client) sendRequest(url string, payload map[string]interface{}) error {
	if payload["guild_id"] == "" {
		payload["guild_id"] = nil
	}

	payload["nonce"] = generateNonce()

	json_data, err := json.Marshal(payload)
	if err != nil {
		return err
	}

	err = client.RequestWithLockedBucket("POST", url, json_data, client.RateLimiter.LockBucket(url), 0)
	if err != nil {
		return err
	}

	return err
}

func (client *Client) SendCommand(commandName string, options map[string]string) error {
	url := "https://discord.com/api/v9/interactions"
	commandInfo := client.GetCommandInfo(commandName)

	if commandInfo == nil {
		commands, err := client.GetCommands(client.GuildID)
		if err != nil {
			client.Log("ERR", fmt.Sprintf("Failed to get commands: %s", err.Error()))
		} else {
			commandDataSlice := make([]CommandData, 0, len(commands))
			for _, cmd := range commands {
				commandDataSlice = append(commandDataSlice, cmd)
			}

			client.CommandsData = &commandDataSlice
		}

		commandInfo := client.GetCommandInfo(commandName)
		if commandInfo == nil {
			return fmt.Errorf("failed to send /%s command: Could not get command info", commandName)
		}
	}

	var commandSendOptions = []CommandSendOptions{}
	if options != nil {
		commandSendOptions = make([]CommandSendOptions, 0, len(options))
		for k, v := range options {
			commandSendOptions = append(commandSendOptions, CommandSendOptions{
				Type:  3,
				Name:  k,
				Value: v,
			})
		}
	}

	payload := map[string]interface{}{
		"type":           2,
		"application_id": "270904126974590976",
		"guild_id":       client.GuildID,
		"channel_id":     client.ChannelID,
		"session_id":     client.Gateway.SessionID,
		"data": map[string]interface{}{
			"version": commandInfo.Version,
			"id":      commandInfo.ID,
			"name":    commandInfo.Name,
			"type":    1,
			"options": commandSendOptions,
			"application_command": CommandData{
				ID:                   commandInfo.ID,
				Type:                 1,
				ApplicationID:        "270904126974590976",
				Version:              commandInfo.Version,
				Name:                 commandInfo.Name,
				Description:          commandInfo.Description,
				DmPermission:         commandInfo.DmPermission,
				IntegrationTypes:     commandInfo.IntegrationTypes,
				GlobalPopularityRank: commandInfo.GlobalPopularityRank,
				Options:              commandInfo.Options,
			},
			"attachments": []string{},
		},
	}

	return client.sendRequest(url, payload)
}

func (client *Client) SendSubCommand(commandName string, subCommandName string, options map[string]string) error {
	url := "https://discord.com/api/v9/interactions"
	commandInfo := client.GetCommandInfo(commandName)

	if commandInfo == nil {
		return fmt.Errorf("failed to send /%s %s command: Could not get command info", commandName, subCommandName)
	}

	var commandSendOptions = []CommandSendOptions{}
	if options != nil {
		commandSendOptions = make([]CommandSendOptions, 0, len(options))
		for k, v := range options {
			commandSendOptions = append(commandSendOptions, CommandSendOptions{
				Type:  3,
				Name:  k,
				Value: v,
			})
		}
	}

	payload := map[string]interface{}{
		"type":           2,
		"application_id": "270904126974590976",
		"guild_id":       client.GuildID,
		"channel_id":     client.ChannelID,
		"session_id":     client.Gateway.SessionID,
		"data": map[string]interface{}{
			"version": commandInfo.Version,
			"id":      commandInfo.ID,
			"name":    commandInfo.Name,
			"type":    1,
			"options": []map[string]interface{}{
				{
					"type":    1,
					"name":    subCommandName,
					"options": commandSendOptions,
				},
			},
			"application_command": CommandData{
				ID:                   commandInfo.ID,
				Type:                 1,
				ApplicationID:        "270904126974590976",
				Version:              commandInfo.Version,
				Name:                 commandInfo.Name,
				Description:          commandInfo.Description,
				DmPermission:         commandInfo.DmPermission,
				IntegrationTypes:     commandInfo.IntegrationTypes,
				GlobalPopularityRank: commandInfo.GlobalPopularityRank,
				Options:              commandInfo.Options,
			},
			"attachments": []string{},
		},
	}

	return client.sendRequest(url, payload)
}

func (client *Client) ClickButton(message types.MessageData, row int, column int) error {
	if message.GuildID == "" {
		message.GuildID = client.GuildID
	}

	payload := map[string]interface{}{
		"type":           3,
		"application_id": "270904126974590976",
		"guild_id":       message.GuildID,
		"channel_id":     message.ChannelID,
		"message_id":     message.MessageID,
		"session_id":     client.Gateway.SessionID,
		"message_flags":  message.Flags,
		"data": map[string]interface{}{
			"component_type": 2,
			"custom_id":      message.Components[row].(*types.ActionsRow).Components[column].(*types.Button).CustomID,
		},
	}

	return client.sendRequest("https://discord.com/api/v9/interactions", payload)
}

func (client *Client) ChooseSelectMenu(message types.MessageData, row int, column int, values []string) error {
	payload := map[string]interface{}{
		"application_id": "270904126974590976",
		"channel_id":     message.ChannelID,
		"data": map[string]interface{}{
			"component_type": 3,
			"custom_id":      message.Components[row].(*types.ActionsRow).Components[column].(*types.SelectMenu).CustomID,
			"type":           3,
			"values":         values,
		},
		"guild_id":   message.GuildID,
		"message_id": message.MessageID,
		"session_id": client.Gateway.SessionID,
		"type":       3,
	}

	return client.sendRequest("https://discord.com/api/v9/interactions", payload)
}

func (client *Client) SubmitModal(modal types.ModalData) error {
	payload := map[string]interface{}{
		"type":           5,
		"application_id": "270904126974590976",
		"channel_id":     modal.ChannelID,
		"guild_id":       client.GuildID,
		"data": map[string]interface{}{
			"id":         modal.ID,
			"custom_id":  modal.CustomID,
			"components": modal.Components,
		},
		"session_id": client.Gateway.SessionID,
		"nonce":      generateNonce(),
	}

	return client.sendRequest("https://discord.com/api/v9/interactions", payload)
}
