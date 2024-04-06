package discord

import (
	"context"
	"fmt"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/rs/zerolog/log"
	"github.com/wailsapp/wails/v2/pkg/runtime"
)

type Client struct {
	Ctx          context.Context
	Selfbot      *Selfbot
	Gateway      *Gateway
	Config       *types.Config
	ChannelID    string
	GuildID      string
	CommandsData *[]CommandData
	RateLimiter  *RateLimiter
}

type CommandSendOptions struct {
	Type  int    `json:"type"`
	Name  string `json:"name"`
	Value string `json:"value"`
}

func NewClient(ctx context.Context, token string, config *types.Config) *Client {
	selfbot := Selfbot{Token: token}
	gateway := CreateGateway(ctx, &selfbot, config)
	commandsData := make([]CommandData, 0)

	return &Client{ctx, &selfbot, gateway, config, "", "", &commandsData, NewRatelimiter()}
}

func (client *Client) Connect() error {
	return client.Gateway.Connect()
}

func (client *Client) AddHandler(event string, function any) error {
	return client.Gateway.Handlers.Add(event, function)
}

func (client *Client) Close() {
	client.Gateway.Close()
}

func (client *Client) SendMessage(payload []byte) error {
	return client.Gateway.sendMessage(payload)
}

type LogType string

const (
	Info  LogType = "INF"
	Error LogType = "ERR"
)

func (client *Client) Log(logType LogType, msg string) {
	runtime.EventsEmit(client.Ctx, "logDiscord", logType, client.Selfbot.User.Username, msg)
	switch logType {
	case Info:
		log.Info().Msg(fmt.Sprintf("%s %s", client.Selfbot.User.Username, msg))
	case Error:
		log.Error().Msg(fmt.Sprintf("%s %s", client.Selfbot.User.Username, msg))
	}
}
