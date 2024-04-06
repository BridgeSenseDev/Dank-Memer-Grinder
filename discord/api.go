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
	url := fmt.Sprintf("https://discord.com/api/v9/guilds/%s/application-command-index", guildID)

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

func (client *Client) RequestWithLockedBucket(method, urlStr string, b []byte, bucket *Bucket, sequence int) error {
	req := fasthttp.AcquireRequest()
	resp := fasthttp.AcquireResponse()
	defer fasthttp.ReleaseRequest(req)
	defer fasthttp.ReleaseResponse(resp)

	req.SetRequestURI(urlStr)
	req.Header.SetMethod(method)

	if client.Selfbot.Token != "" {
		req.Header.Set("authorization", client.Selfbot.Token)
	}

	if b != nil {
		req.Header.Set("Content-Type", "application/json")
		req.SetBody(b)
	}

	req.Header.Set("User-Agent", client.Config.UserAgent)

	err := fasthttp.Do(req, resp)
	if err != nil {
		bucket.Release(nil)
		return err
	}

	err = bucket.Release(&resp.Header)
	if err != nil {
		return err
	}

	response := resp.Body()

	switch resp.StatusCode() {
	case fasthttp.StatusOK, fasthttp.StatusCreated, fasthttp.StatusNoContent:
	case fasthttp.StatusBadGateway:
		if sequence < 3 {
			client.Log("INF", fmt.Sprintf("%s Failed (%d), Retrying...", urlStr, resp.StatusCode()))
			err = client.RequestWithLockedBucket(method, urlStr, b, client.RateLimiter.LockBucketObject(bucket), sequence+1)
		} else {
			client.Log("ERR", fmt.Sprintf("Exceeded Max retries HTTP %d, %s", resp.StatusCode(), response))
		}
	case fasthttp.StatusTooManyRequests:
		rl := TooManyRequests{}
		err = json.Unmarshal(response, &rl)
		if err != nil {
			client.Log("ERR", fmt.Sprintf("rate limit unmarshal error, %s", err))
			return err
		}

		client.Log("INF", fmt.Sprintf("Rate Limiting %s, retry in %v", urlStr, rl.RetryAfter))

		time.Sleep(time.Duration(rl.RetryAfter * float64(time.Second)))
		err = client.RequestWithLockedBucket(method, urlStr, b, client.RateLimiter.LockBucketObject(bucket), sequence)
	default:
		err = fmt.Errorf("request failed with status code %d: %s", resp.StatusCode(), string(response))
	}

	return err
}
