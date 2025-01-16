package discord

import (
	"encoding/json"
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"math/big"
	"net/url"
	"strings"
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
		if cmd.Name == commandName && cmd.ApplicationID == "270904126974590976" {
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

	jsonData, err := json.Marshal(payload)
	if err != nil {
		return err
	}

	_, err = client.RequestWithLockedBucket("POST", url, jsonData, client.RateLimiter.LockBucket(url), 0)
	if err != nil {
		return err
	}

	return err
}

func (client *Client) SendCommand(commandName string, options map[string]string) error {
	interactionsUrl := "https://discord.com/api/v9/interactions"
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

	var commandSendOptions []CommandSendOptions
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
		"session_id":     *client.Gateway.SessionID(),
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

	return client.sendRequest(interactionsUrl, payload)
}

func (client *Client) SendSubCommand(commandName string, subCommandName string, options map[string]string) error {
	interactionsUrl := "https://discord.com/api/v9/interactions"
	commandInfo := client.GetCommandInfo(commandName)

	if commandInfo == nil {
		return fmt.Errorf("failed to send /%s %s command: Could not get command info", commandName, subCommandName)
	}

	var commandSendOptions []CommandSendOptions
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
		"session_id":     *client.Gateway.SessionID(),
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

	return client.sendRequest(interactionsUrl, payload)
}

func (client *Client) ClickButton(message gateway.EventMessage, row int, column int) error {
	if message.GuildID == "" {
		message.GuildID = client.GuildID
	}

	payload := map[string]interface{}{
		"type":           3,
		"application_id": "270904126974590976",
		"guild_id":       message.GuildID,
		"channel_id":     message.ChannelID,
		"message_id":     message.MessageID,
		"session_id":     *client.Gateway.SessionID(),
		"message_flags":  message.Flags,
		"data": map[string]interface{}{
			"component_type": 2,
			"custom_id":      message.Components[row].(*types.ActionsRow).Components[column].(*types.Button).CustomID,
		},
	}

	return client.sendRequest("https://discord.com/api/v9/interactions", payload)
}

func (client *Client) ClickDmButton(message gateway.EventMessage, row int, column int) error {
	payload := map[string]interface{}{
		"type":           3,
		"application_id": "270904126974590976",
		"guild_id":       nil,
		"channel_id":     message.ChannelID,
		"message_id":     message.MessageID,
		"session_id":     *client.Gateway.SessionID(),
		"message_flags":  message.Flags,
		"data": map[string]interface{}{
			"component_type": 2,
			"custom_id":      message.Components[row].(*types.ActionsRow).Components[column].(*types.Button).CustomID,
		},
	}

	return client.sendRequest("https://discord.com/api/v9/interactions", payload)
}

func (client *Client) ChooseSelectMenu(message gateway.EventMessage, row int, column int, values []string) error {
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
		"session_id": *client.Gateway.SessionID(),
		"type":       3,
	}

	return client.sendRequest("https://discord.com/api/v9/interactions", payload)
}

func (client *Client) SubmitModal(modal gateway.EventModalCreate) error {
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
		"session_id": *client.Gateway.SessionID(),
		"nonce":      generateNonce(),
	}

	return client.sendRequest("https://discord.com/api/v9/interactions", payload)
}

func addParamsToURL(baseURL string, params map[string]interface{}) string {
	var queryParams []string
	for key, value := range params {
		queryParams = append(queryParams, fmt.Sprintf("%s=%s",
			url.QueryEscape(key),
			url.QueryEscape(fmt.Sprint(value))))
	}

	if strings.Contains(baseURL, "?") {
		return baseURL + "&" + strings.Join(queryParams, "&")
	}
	return baseURL + "?" + strings.Join(queryParams, "&")
}

func (client *Client) GetAuthorizationCode() (string, error) {
	urlParameters := map[string]interface{}{
		"client_id":     "270904126974590976",
		"response_type": "code",
		"redirect_uri":  "https://dankmemer.lol/api/auth/callback",
		"scope":         "identify",
		"state":         "redirect:/",
	}

	fullUrl := addParamsToURL("https://discord.com/api/v9/oauth2/authorize", urlParameters)

	payload := map[string]interface{}{
		"authorize":        true,
		"guild_id":         "846362236658515998",
		"integration_type": 0,
		"location_context": map[string]interface{}{
			"guild_id":     "10000",
			"channel_id":   "10000",
			"channel_type": "10000",
		},
	}

	jsonPayload, err := json.Marshal(payload)
	if err != nil {
		return "", fmt.Errorf("failed to marshal payload: %v", err)
	}

	bucket := client.RateLimiter.GetBucket(fullUrl)

	response, err := client.RequestWithLockedBucket("POST", fullUrl, jsonPayload, bucket, 0)
	if err != nil {
		return "", fmt.Errorf("authorization request failed: %v", err)
	}

	var authResponse struct {
		Location string `json:"location"`
	}
	err = json.Unmarshal(response, &authResponse)
	if err != nil {
		return "", fmt.Errorf("failed to parse authorization response: %v", err)
	}

	locationURL, err := url.Parse(authResponse.Location)
	if err != nil {
		return "", fmt.Errorf("failed to parse location URL: %v", err)
	}

	code := locationURL.Query().Get("code")
	if code == "" {
		return "", fmt.Errorf("authorization code not found in response")
	}

	return code, nil
}
