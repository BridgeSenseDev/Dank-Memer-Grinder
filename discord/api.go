package discord

import (
	"encoding/json"
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
	"strings"
	"time"

	"github.com/valyala/fasthttp"
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
	url := fmt.Sprintf("https://discord.com/api/v9/guilds/%s/application-command-index", guildID)

	req := fasthttp.AcquireRequest()
	defer fasthttp.ReleaseRequest(req)

	req.Header.SetMethod("GET")
	req.SetRequestURI(url)
	req.Header.Set("Authorization", client.Token)
	req.Header.Set("Content-type", "application/json")

	resp := fasthttp.AcquireResponse()
	defer fasthttp.ReleaseResponse(resp)

	err := fasthttp.Do(req, resp)
	if err != nil {
		return nil, err
	} else if resp.StatusCode() != 200 {
		return nil, fmt.Errorf("request failed with status code %d: %s", resp.StatusCode(), string(resp.Body()))
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
	url := fmt.Sprintf("https://discord.com/api/v9/channels/%s", channelID)

	req := fasthttp.AcquireRequest()
	defer fasthttp.ReleaseRequest(req)

	req.Header.SetMethod("GET")
	req.SetRequestURI(url)
	req.Header.Set("Authorization", client.Token)
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

func (client *Client) RequestWithLockedBucket(method, urlStr string, b []byte, bucket *Bucket, sequence int) ([]byte, error) {
	req := fasthttp.AcquireRequest()
	resp := fasthttp.AcquireResponse()
	defer fasthttp.ReleaseRequest(req)
	defer fasthttp.ReleaseResponse(resp)

	req.SetRequestURI(urlStr)
	req.Header.SetMethod(method)

	if client.Token != "" {
		req.Header.Set("Authorization", client.Token)
	}

	if b != nil {
		req.Header.Set("Content-Type", "application/json")
		req.SetBody(b)
	}

	req.Header.Set("User-Agent", client.Gateway.UserAgent())

	if strings.Contains(urlStr, "https://discord.com/api/v9/oauth2/authorize") {
		req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
		req.Header.Set("Accept-Language", "en-US,en;q=0.5")
		req.Header.Set("Connection", "keep-alive")
		req.Header.Set("Referer", "https://discord.com/")
		req.Header.Set("Upgrade-Insecure-Requests", "1")
	}

	err := fasthttp.Do(req, resp)
	if err != nil {
		err := bucket.Release(nil)
		if err != nil {
			return nil, err
		}
		return nil, err
	}

	err = bucket.Release(&resp.Header)
	if err != nil {
		return nil, err
	}

	response := resp.Body()

	switch resp.StatusCode() {
	case fasthttp.StatusOK, fasthttp.StatusCreated, fasthttp.StatusNoContent:
	case fasthttp.StatusBadGateway:
		if sequence < 3 {
			utils.Log(utils.Discord, utils.Info, client.SafeGetUsername(), fmt.Sprintf("%s Failed (%d), Retrying...", urlStr, resp.StatusCode()))
			_, err = client.RequestWithLockedBucket(method, urlStr, b, client.RateLimiter.LockBucketObject(bucket), sequence+1)
		} else {
			utils.Log(utils.Discord, utils.Error, client.SafeGetUsername(), fmt.Sprintf("Exceeded Max retries HTTP %d, %s", resp.StatusCode(), response))
			return response, fmt.Errorf("exceeded max retries HTTP %d: %s", resp.StatusCode(), string(response))
		}
	case fasthttp.StatusTooManyRequests:
		rl := TooManyRequests{}
		err = json.Unmarshal(response, &rl)
		if err != nil {
			utils.Log(utils.Discord, utils.Error, client.SafeGetUsername(), fmt.Sprintf("rate limit unmarshal error, %s", err))
			return response, err
		}

		utils.Log(utils.Discord, utils.Info, client.SafeGetUsername(), fmt.Sprintf("Rate Limiting %s, retry in %v", urlStr, rl.RetryAfter))

		time.Sleep(time.Duration(rl.RetryAfter * float64(time.Second)))
		_, err = client.RequestWithLockedBucket(method, urlStr, b, client.RateLimiter.LockBucketObject(bucket), sequence)
		if err != nil {
			return response, err
		}
	default:
		return response, fmt.Errorf("request failed with status code %d: %s", resp.StatusCode(), string(response))
	}

	return response, nil
}
