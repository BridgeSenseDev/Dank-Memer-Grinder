package instance

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/config"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/rs/zerolog/log"
	"github.com/wailsapp/wails/v2/pkg/runtime"
)

type LogLevel string

const (
	Important LogLevel = "important"
	Others    LogLevel = "others"
	Discord   LogLevel = "discord"
)

type LogType string

const (
	Info  LogType = "INF"
	Error LogType = "ERR"
)

func (in *Instance) Log(level LogLevel, logType LogType, msg string) {
	switch level {
	case Important:
		runtime.EventsEmit(in.Ctx, "logImportant", logType, in.User.Username, msg)
	case Others:
		runtime.EventsEmit(in.Ctx, "logOthers", logType, in.User.Username, msg)
	case Discord:
		runtime.EventsEmit(in.Ctx, "logDiscord", logType, in.User.Username, msg)
	}

	switch logType {
	case Info:
		log.Info().Msg(fmt.Sprintf("%s %s %s", level, in.User.Username, msg))
	case Error:
		log.Error().Msg(fmt.Sprintf("%s %s %s", level, in.User.Username, msg))
	}
}

type Client interface {
	SendMessage(payload []byte) error
	Close()
	AddHandler(event string, handler interface{}) error
	SendCommand(name string, options map[string]string) error
	SendSubCommand(name string, subCommandName string, options map[string]string) error
	ClickButton(message types.MessageData, row int, column int) error
	ChooseSelectMenu(message types.MessageData, row int, column int, values []string) error
	SubmitModal(modal types.ModalData) error
}

type Instance struct {
	User       types.User            `json:"user"`
	Client     Client                `json:"client"`
	ChannelID  string                `json:"channelID"`
	GuildID    string                `json:"guildID"`
	Cfg        config.Config         `json:"config"`
	AccountCfg config.AccountsConfig `json:"accountCfg"`
	LastRan    map[string]time.Time  `json:"lastRan"`
	Pause      bool                  `json:"pause"`
	StopChan   chan struct{}         `json:"stopChan"`
	Error      string                `json:"error,omitempty"`
	Ctx        context.Context
	pauseToken int
}

func (in *Instance) Start() error {
	if in.Client == nil {
		return fmt.Errorf("no client")
	}

	go in.CommandsLoop()

	in.Client.AddHandler(types.GatewayEventMessageCreate, func(event *types.MessageEventData) {
		in.HandleMessageCreate(event)
	})

	in.Client.AddHandler(types.GatewayEventMessageUpdate, func(event *types.MessageEventData) {
		in.HandleMessageUpdate(event)
	})

	in.Client.AddHandler(types.GatewayEventModalCreate, func(event *types.ModalData) {
		in.HandleModalCreate(event)
	})

	return nil
}

func (in *Instance) Stop() {
	in.Log("important", "INF", fmt.Sprintf("Stopping instance "+in.User.Username))
	close(in.StopChan)
	in.Client.Close()
}

func (in *Instance) PauseCommands(indefinite bool) {
	if indefinite {
		in.Log("others", "INF", "Paused commands indefinitely")
	} else {
		in.Log("others", "INF", "Paused commands")
	}

	in.Pause = true

	if !indefinite {
		in.pauseToken++

		token := in.pauseToken

		go func() {
			time.Sleep(time.Minute)

			if in.Pause && in.pauseToken == token {
				in.Log("others", "ERR", "Force unpaused commands after being paused for 1 minute")
				in.Pause = false
			}
		}()
	}
}

func (in *Instance) UnpauseCommands() {
	in.Log("others", "INF", "Unpaused commands")
	in.Pause = false
}

func (in *Instance) UpdateConfig(newConfig config.Config) {
	in.Cfg = newConfig
	for _, newAccount := range newConfig.Accounts {
		if newAccount.Token == in.AccountCfg.Token {
			in.AccountCfg = newAccount
			break
		}
	}
}

type MessageHandler func(*Instance, *types.MessageEventData)

var messageCreateHandlers = map[string]MessageHandler{
	"adventure": (*Instance).AdventureMessageCreate,
	"highlow":   (*Instance).HighLow,
	"scratch":   (*Instance).ScratchMessageCreate,
	"crime":     (*Instance).Crime,
	"search":    (*Instance).Search,
	"trivia":    (*Instance).Trivia,
	"postmemes": (*Instance).PostMemesMessageCreate,
}

var messageUpdateHandlers = map[string]MessageHandler{
	"adventure": (*Instance).AdventureMessageUpdate,
	"scratch":   (*Instance).ScratchMessageUpdate,
	"postmemes": (*Instance).PostMemesMessageUpdate,
}

func (in *Instance) shouldHandleMessage(message *types.MessageEventData) bool {
	return message.Author.ID == "270904126974590976" &&
		len(message.Embeds) > 0 &&
		!strings.Contains(message.Embeds[0].Description, "cooldown is")
}

func (in *Instance) getMessageType(message *types.MessageEventData) string {
	if message.ChannelID == in.ChannelID {
		return "channel"
	} else if message.GuildID == "" {
		return "dm"
	} else {
		return "global"
	}
}

func (in *Instance) handleInteraction(message *types.MessageEventData, handlers map[string]MessageHandler) {
	if message.Interaction != (types.MessageInteraction{}) && message.Interaction.User.ID == in.User.ID && message.Flags != 64 {
		if handler, ok := handlers[message.Interaction.Name]; ok {
			handler(in, message)
		}
	}
}

func (in *Instance) HandleMessageCreate(message *types.MessageEventData) {
	if in.shouldHandleMessage(message) {
		// Apply to all messages
		if in.Captcha(message) {
			return
		}

		in.Others(message)

		messageType := in.getMessageType(message)

		if messageType == "channel" {
			// Only apply to channel_id channel
			in.handleInteraction(message, messageCreateHandlers)
			in.MinigamesMessageCreate(message)
			in.AutoBuyMessageCreate(message)
		} else if messageType == "dm" {
			// Only apply to dank dm's
			in.AutoBuyMessageCreate(message)
		}
	}
}

func (in *Instance) HandleMessageUpdate(message *types.MessageEventData) {
	if in.shouldHandleMessage(message) {
		messageType := in.getMessageType(message)

		if messageType == "channel" {
			// Only apply to channel_id channel
			in.handleInteraction(message, messageUpdateHandlers)
			in.MinigamesMessageUpdate(message)
			in.AutoBuyMessageUpdate(message)
		} else if messageType == "dm" {
			// Only apply to dank dm's
			in.AutoBuyMessageUpdate(message)
		}
	}
}

func (in *Instance) HandleModalCreate(modal *types.ModalData) {
	in.AutoBuyModalCreate(modal)
}
