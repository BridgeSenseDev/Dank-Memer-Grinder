package discord

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/valyala/fasthttp"
)

var (
	clientBuildNumber = mustGetLatestBuild()
	clientLocale      = mustGetLocale()
	requestClient     = fasthttp.Client{
		ReadBufferSize:                8192,
		ReadTimeout:                   time.Second * 5,
		WriteTimeout:                  time.Second * 5,
		NoDefaultUserAgentHeader:      true,
		DisableHeaderNamesNormalizing: true,
		DisablePathNormalizing:        true,
	}
)

type CommandOptions []struct {
	Type        int    `json:"type"`
	Name        string `json:"name"`
	Description string `json:"description"`
	Required    bool   `json:"required,omitempty"`
}

type CommandData struct {
	ID                   string         `json:"id"`
	Type                 int            `json:"type"`
	ApplicationID        string         `json:"application_id"`
	Version              string         `json:"version"`
	Name                 string         `json:"name"`
	Description          string         `json:"description"`
	DmPermission         bool           `json:"dm_permission"`
	IntegrationTypes     []int          `json:"integration_types"`
	GlobalPopularityRank int            `json:"global_popularity_rank"`
	Options              CommandOptions `json:"options,omitempty"`
}

func (client *Client) GetCommands(guildID string) (map[string]CommandData, error) {
	url := fmt.Sprintf("https://discord.com/api/v10/guilds/%s/application-command-index", guildID)

	req := fasthttp.AcquireRequest()
	defer fasthttp.ReleaseRequest(req)

	req.Header.SetMethod("GET")
	req.SetRequestURI(url)
	req.Header.Set("Authorization", client.Selfbot.Token)
	req.Header.Set("Content-type", "application/json")

	resp := fasthttp.AcquireResponse()
	defer fasthttp.ReleaseResponse(resp)

	err := fasthttp.Do(req, resp)
	if err != nil {
		return nil, err
	}

	body := resp.Body()

	var data struct {
		ApplicationCommands []CommandData `json:"application_commands"`
	}
	if err := json.Unmarshal(body, &data); err != nil {
		return nil, err
	}

	commands := make(map[string]CommandData)
	for _, cmd := range data.ApplicationCommands {
		commands[cmd.Name] = cmd
	}

	return commands, nil
}

type Channel struct {
	ID      string `json:"id"`
	GuildID string `json:"guild_id"`
}

func (client *Client) GetGuildID(channelID string) string {
	url := fmt.Sprintf("https://discord.com/api/v10/channels/%s", channelID)

	req := fasthttp.AcquireRequest()
	defer fasthttp.ReleaseRequest(req)

	req.Header.SetMethod("GET")
	req.SetRequestURI(url)
	req.Header.Set("Authorization", client.Selfbot.Token)
	req.Header.Set("Content-type", "application/json")

	resp := fasthttp.AcquireResponse()
	defer fasthttp.ReleaseResponse(resp)

	err := fasthttp.Do(req, resp)
	if err != nil {
		return ""
	}

	body := resp.Body()

	var channel Channel
	if err := json.Unmarshal(body, &channel); err != nil {
		return ""
	}

	return channel.GuildID
}
