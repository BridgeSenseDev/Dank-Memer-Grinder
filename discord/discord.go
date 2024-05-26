package discord

import (
	"context"
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"github.com/rs/zerolog/log"
	"github.com/wailsapp/wails/v2/pkg/runtime"
)

type Client struct {
	Ctx          context.Context
	Token        string
	Handlers     Handlers
	Gateway      gateway.Gateway
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

func NewClient(ctx context.Context, token string) *Client {
	commandsData := make([]CommandData, 0)

	client := &Client{Ctx: ctx, Token: token, CommandsData: &commandsData, RateLimiter: NewRatelimiter()}
	client.Gateway = gateway.New(ctx, token, client.gatewayHandlers)

	return client
}

func (client *Client) gatewayHandlers(gatewayEventType gateway.EventType, event gateway.EventData) {
	switch gatewayEventType {
	case gateway.EventTypeReady:
		for _, handler := range client.Handlers.OnReady {
			handler(event.(gateway.EventReady))
		}
	case gateway.EventTypeResumed:
		client.Log("INF", "Successfully resumed discord gateway")
	case gateway.EventTypeMessageCreate:
		for _, handler := range client.Handlers.OnMessageCreate {
			handler(event.(gateway.EventMessage))
		}
	case gateway.EventTypeMessageUpdate:
		for _, handler := range client.Handlers.OnMessageUpdate {
			handler(event.(gateway.EventMessage))
		}
	case gateway.EventTypeModalCreate:
		for _, handler := range client.Handlers.OnModalCreate {
			handler(event.(gateway.EventModalCreate))
		}
	}
}

func (client *Client) Connect() error {
	return client.Gateway.Open(client.Ctx)
}

func (client *Client) AddHandler(event gateway.EventType, function any) error {
	return client.Handlers.Add(event, function)
}

func (client *Client) Close() {
	client.Gateway.Close(client.Ctx)
}

func (client *Client) SendMessage(op gateway.Opcode, data gateway.MessageData) error {
	return client.Gateway.Send(client.Ctx, op, data)
}

type LogType string

const (
	Info  LogType = "INF"
	Error LogType = "ERR"
)

func (client *Client) Log(logType LogType, msg string) {
	runtime.EventsEmit(client.Ctx, "logDiscord", logType, client.Gateway.User().Username, msg)
	switch logType {
	case Info:
		log.Info().Msg(fmt.Sprintf("discord %s %s", client.Gateway.User().Username, msg))
	case Error:
		log.Error().Msg(fmt.Sprintf("discord %s %s", client.Gateway.User().Username, msg))
	}
}
