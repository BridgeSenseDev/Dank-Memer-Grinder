package instance

import (
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"github.com/valyala/fasthttp"
	"strconv"
	"strings"
	"time"
)

var trendingGame string
var currentOrderIndex int

func (in *Instance) handleOrderedClick(message gateway.EventMessage) error {
	order := in.Cfg.Commands.Stream.Order
	buttonIndex := order[currentOrderIndex]

	if err := in.ClickButton(message, 0, buttonIndex); err != nil {
		in.Log("discord", "ERR", fmt.Sprintf("Failed to click stream button: %s", err.Error()))
		return err
	}

	currentOrderIndex = (currentOrderIndex + 1) % len(order)
	return nil
}

func (in *Instance) StreamMessageCreate(message gateway.EventMessage) {
	embed := message.Embeds[0]

	if !strings.Contains(embed.Author.Name, "Stream Manager") {
		return
	}

	if embed.Fields[1].Name == "Last Live" {
		if err := in.ClickButton(message, 0, 0); err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to click stream button: %s", err.Error()))
			return
		}

		resp := fasthttp.AcquireResponse()
		req := fasthttp.AcquireRequest()
		defer fasthttp.ReleaseResponse(resp)
		defer fasthttp.ReleaseRequest(req)

		req.SetRequestURI("https://api.dankmemer.tools/trending")
		req.Header.SetMethod(fasthttp.MethodGet)

		if err := fasthttp.Do(req, resp); err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to get games: %s", err.Error()))
			return
		}

		trendingGame = string(resp.Body())
	} else if embed.Fields[1].Name == "Live Since" {
		if err := in.handleOrderedClick(message); err != nil {
			return
		}
	}
}

func (in *Instance) StreamMessageUpdate(message gateway.EventMessage) {
	embed := message.Embeds[0]

	if strings.Contains(embed.Description, "What game do you want to stream?") {
		chooseMenu := message.Components[0].(*types.ActionsRow).Components[0].(*types.SelectMenu)

		for _, option := range chooseMenu.Options {
			if option.Default {
				if option.Value == trendingGame {
					if err := in.ClickButton(message, 1, 0); err != nil {
						in.Log("discord", "ERR", fmt.Sprintf("Failed to click go live button: %s", err.Error()))
						return
					}
				} else {
					err := in.ChooseSelectMenu(message, 0, 0, []string{trendingGame})
					if err != nil {
						in.Log("discord", "ERR", fmt.Sprintf("Failed to choose stream game: %s", err.Error()))
					}
				}
			}
		}
	}

	if len(embed.Fields) > 2 && embed.Fields[1].Name == "Live Since" {
		timestampStr := embed.Fields[1].Value[3 : len(embed.Fields[1].Value)-3]
		timestamp, err := strconv.ParseInt(timestampStr, 10, 64)
		if err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to parse timestamp: %s", err.Error()))
			return
		}

		if time.Since(time.Unix(timestamp, 0)) > time.Minute {
			return
		}

		if err = in.handleOrderedClick(message); err != nil {
			return
		}
	}
}
