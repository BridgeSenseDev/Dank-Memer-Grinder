package instance

import (
	"context"
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
	"github.com/wailsapp/wails/v3/pkg/application"
	"strings"
	"sync"
	"time"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/config"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/rs/zerolog/log"
)

func (in *Instance) Log(level utils.LogLevel, logType utils.LogType, msg string) {
	switch level {
	case utils.Important:
		application.Get().EmitEvent("logImportant", logType, in.User.Username, msg)
	case utils.Others:
		application.Get().EmitEvent("logOthers", logType, in.User.Username, msg)
	case utils.Discord:
		if strings.Contains(msg, "COMPONENT_VALIDATION_FAILED") {
			return
		}
		application.Get().EmitEvent("logDiscord", logType, in.User.Username, msg)
	}

	switch logType {
	case utils.Info:
		log.Info().Msg(fmt.Sprintf("%s %s %s", level, in.User.Username, msg))
	case utils.Error:
		log.Error().Msg(fmt.Sprintf("%s %s %s", level, in.User.Username, msg))
	}
}

type Client interface {
	SendMessage(op gateway.Opcode, data gateway.MessageData) error
	Close()
	AddHandler(event gateway.EventType, handler interface{}) error
	SendCommand(name string, options map[string]string) error
	SendSubCommand(name string, subCommandName string, options map[string]string) error
	ClickButton(message gateway.EventMessage, row int, column int) error
	ClickDmButton(message gateway.EventMessage, row int, column int) error
	ChooseSelectMenu(message gateway.EventMessage, row int, column int, values []string) error
	SubmitModal(modal gateway.EventModalCreate) error
	GetAuthorizationCode() (string, error)
}

type Instance struct {
	User       *types.User           `json:"user"`
	Client     Client                `json:"client"`
	ChannelID  string                `json:"channelID"`
	GuildID    string                `json:"guildID"`
	Cfg        config.Config         `json:"config"`
	AccountCfg config.AccountsConfig `json:"accountCfg"`
	LastRan    map[string]time.Time  `json:"lastRan"`
	StopChan   chan struct{}         `json:"stopChan"`
	Error      string                `json:"error,omitempty"`
	Ctx        context.Context
	pauseCount int
	pauseMutex sync.Mutex
}

func (in *Instance) Start() error {
	if in.Client == nil {
		return fmt.Errorf("no client")
	}

	go in.CommandsLoop()

	in.Client.AddHandler(gateway.EventTypeMessageCreate, func(event gateway.EventMessage) {
		in.HandleMessageCreate(event)
	})

	in.Client.AddHandler(gateway.EventTypeMessageUpdate, func(event gateway.EventMessage) {
		in.HandleMessageUpdate(event)
	})

	in.Client.AddHandler(gateway.EventTypeModalCreate, func(event gateway.EventModalCreate) {
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
	in.pauseMutex.Lock()
	defer in.pauseMutex.Unlock()

	in.pauseCount++

	if in.pauseCount == 1 {
		if indefinite {
			in.Log("others", "INF", "Paused commands indefinitely")
		} else {
			in.Log("others", "INF", "Paused commands")
		}
	}

	if !indefinite {
		token := in.pauseCount

		go func() {
			time.Sleep(time.Minute)

			in.pauseMutex.Lock()
			defer in.pauseMutex.Unlock()

			if in.pauseCount == token {
				in.Log("others", "ERR", "Force unpaused commands after being paused for 1 minute")
				in.pauseCount = 0
			}
		}()
	}
}

func (in *Instance) UnpauseCommands() {
	in.pauseMutex.Lock()
	defer in.pauseMutex.Unlock()

	if in.pauseCount > 0 {
		in.pauseCount--
	}

	if in.pauseCount == 0 {
		in.Log("others", "INF", "Unpaused commands")
	}
}

func (in *Instance) IsPaused() bool {
	in.pauseMutex.Lock()
	defer in.pauseMutex.Unlock()
	return in.pauseCount > 0
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

type MessageHandler func(*Instance, gateway.EventMessage)

var messageCreateHandlers = map[string]MessageHandler{
	"adventure": (*Instance).AdventureMessageCreate,
	"blackjack": (*Instance).BlackjackMessageCreate,
	"highlow":   (*Instance).HighLow,
	"scratch":   (*Instance).ScratchMessageCreate,
	"crime":     (*Instance).Crime,
	"search":    (*Instance).Search,
	"stream":    (*Instance).StreamMessageCreate,
	"trivia":    (*Instance).Trivia,
	"pets":      (*Instance).PetsMessageCreate,
	"postmemes": (*Instance).PostMemesMessageCreate,
	"work":      (*Instance).WorkMessageCreate,
	"profile":   (*Instance).ProfileMessageCreate,
}

var messageUpdateHandlers = map[string]MessageHandler{
	"adventure": (*Instance).AdventureMessageUpdate,
	"blackjack": (*Instance).BlackjackMessageUpdate,
	"scratch":   (*Instance).ScratchMessageUpdate,
	"stream":    (*Instance).StreamMessageUpdate,
	"pets":      (*Instance).PetsMessageUpdate,
	"postmemes": (*Instance).PostMemesMessageUpdate,
	"work":      (*Instance).WorkMessageUpdate,
	"profile":   (*Instance).ProfileMessageUpdate,
}

func (in *Instance) shouldHandleMessage(message gateway.EventMessage) bool {
	return in.Cfg.State && in.AccountCfg.State && message.Author.ID == "270904126974590976" &&
		len(message.Embeds) > 0 &&
		!strings.Contains(message.Embeds[0].Description, "cooldown is")
}

func (in *Instance) getMessageType(message gateway.EventMessage) string {
	if message.ChannelID == in.ChannelID {
		return "channel"
	} else if message.GuildID == "" {
		return "dm"
	} else {
		return "global"
	}
}

func (in *Instance) handleInteraction(message gateway.EventMessage, handlers map[string]MessageHandler) {
	if message.Interaction != (types.MessageInteraction{}) && message.Interaction.User.ID == in.User.ID && message.Flags != 64 {
		if handler, ok := handlers[strings.Split(message.Interaction.Name, " ")[0]]; ok {
			handler(in, message)
		}
	}
}

func (in *Instance) HandleMessageCreate(message gateway.EventMessage) {
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
			in.AutoUse(message)
		}
	}
}

func (in *Instance) HandleMessageUpdate(message gateway.EventMessage) {
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

func (in *Instance) HandleModalCreate(modal gateway.EventModalCreate) {
	in.AutoBuyModalCreate(modal)
}
