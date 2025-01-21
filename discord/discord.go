package discord

import (
	"context"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
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

func (client *Client) SafeGetUsername() string {
	if client.Gateway != nil {
		return client.Gateway.SafeGetUsername()
	} else {
		return utils.GetAccountNumber(client.Token)
	}
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
		utils.Log(utils.Discord, utils.Info, client.SafeGetUsername(), "Successfully resumed discord gateway")
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
