package instance

import (
	"fmt"
	"strings"
	"time"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
)

func (in *Instance) CommandsLoop() {
	ticker := time.NewTicker(2500 * time.Millisecond)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			if !in.Pause && in.Cfg.State && in.AccountCfg.State {
				commandsMap := in.Cfg.Commands.GetCommandsMap()
				for command := range commandsMap {
					select {
					case <-in.StopChan:
						return
					default:
						if !shouldExecuteCommand(in, command) {
							continue
						}

						in.LastRan[command] = time.Now().Add(2 * time.Second)
						var err error
						if command == "Work" {
							err = in.SendSubCommand("work", "shift", nil)
						} else if command == "Deposit" {
							err = in.SendCommand("deposit", map[string]string{"amount": "max"})
						} else {
							err = in.SendCommand(strings.ToLower(command), nil)
						}

						if err != nil {
							in.Log("discord", "ERR", fmt.Sprintf("Failed to send %s command: %s", command, err.Error()))
						}
					}
				}
			} else {
				<-utils.Sleep(1 * time.Second)
			}
		case <-in.StopChan:
			return
		}
	}
}

func shouldExecuteCommand(in *Instance, command string) bool {
	commandConfig := in.Cfg.Commands.GetCommandsMap()[command]
	if time.Since(in.LastRan[command]) < time.Duration(commandConfig.Delay)*time.Second || !commandConfig.State || in.Pause || !in.Cfg.State || !in.AccountCfg.State {
		return false
	}

	switch command {
	case "Pet":
		return false
	default:
		return true
	}
}
