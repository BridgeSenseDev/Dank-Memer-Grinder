package instance

import (
	"fmt"
	"reflect"
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
			minBreakCooldown := in.Cfg.Cooldowns.BreakCooldown.MinHours
			maxBreakCooldown := in.Cfg.Cooldowns.BreakCooldown.MaxHours
			minBreakDuration := in.Cfg.Cooldowns.BreakDuration.MinHours
			maxBreakDuration := in.Cfg.Cooldowns.BreakDuration.MaxHours
			breakOff := minBreakDuration == 0 && maxBreakDuration == 0

			if in.State == "ready" {
				in.State = "running"
				if !breakOff {
					in.BreakUpdateTime = time.Now().Add(utils.RandHours(minBreakCooldown, maxBreakCooldown))
				}
				utils.EmitEventIfNotCLI("instanceUpdate", in.GetView())
			} else if in.State == "running" && !breakOff {
				if time.Now().After(in.BreakUpdateTime) {
					in.State = "sleeping"
					in.BreakUpdateTime = time.Now().Add(utils.RandHours(minBreakDuration, maxBreakDuration))
					in.PauseCommands(true)
					utils.EmitEventIfNotCLI("instanceUpdate", in.GetView())
				}
			} else if in.State == "sleeping" && !breakOff {
				if time.Now().After(in.BreakUpdateTime) {
					in.State = "running"
					in.BreakUpdateTime = time.Now().Add(utils.RandHours(minBreakCooldown, maxBreakCooldown))
					in.UnpauseCommands()
					utils.EmitEventIfNotCLI("instanceUpdate", in.GetView())
				} else if !in.IsPaused() {
					in.PauseCommands(true)
				}
			} else if in.State == "waitingReady" {
				if time.Now().After(in.BreakUpdateTime) {
					in.State = "ready"
					utils.EmitEventIfNotCLI("instanceUpdate", in.GetView())
				}
			}

			if !in.IsPaused() && in.Cfg.State && in.AccountCfg.State {
				commandsMap := in.Cfg.Commands.GetCommandsMap()
				var readyCommands []string

				for command := range commandsMap {
					if shouldExecuteCommand(in, command) {
						readyCommands = append(readyCommands, command)
					}
				}

				for _, command := range readyCommands {
					select {
					case <-in.StopChan:
						return
					default:
						if in.IsPaused() || !in.Cfg.State || !in.AccountCfg.State {
							break
						}

						<-utils.Sleep(utils.RandSeconds(in.Cfg.Cooldowns.CommandInterval.MinSeconds, in.Cfg.Cooldowns.CommandInterval.MaxSeconds))

						in.LastRan[command] = time.Now().Add(2 * time.Second)
						var err error
						if command == "Blackjack" {
							err = in.SendCommand("blackjack", map[string]string{"bet": in.Cfg.Commands.Blackjack.Amount}, false)
						} else if command == "Pets" {
							err = in.SendSubCommand("pets", "care", nil, false)
						} else if command == "Work" {
							err = in.SendSubCommand("work", "shift", nil, false)
						} else if command == "Deposit" {
							err = in.SendCommand("deposit", map[string]string{"amount": "max"}, false)
						} else if command == "Fish" {
							err = in.SendSubCommand("fish", "catch", nil, false)
						} else {
							err = in.SendCommand(strings.ToLower(command), nil, false)
						}

						if err != nil {
							utils.Log(utils.Others, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to send %s command: %s", command, err.Error()))
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
	if time.Since(in.LastRan[command]) < time.Duration(commandConfig.Delay)*time.Second || !commandConfig.State || in.IsPaused() || !in.Cfg.State || !in.AccountCfg.State {
		return false
	}

	switch command {
	case "Blackjack":
		return !in.Cfg.Commands.Blackjack.ManuallyRunCommands
	case "Profile":
		val := reflect.ValueOf(in.Cfg.AutoUse)
		for i := 0; i < val.NumField(); i++ {
			if val.Field(i).FieldByName("State").Bool() {
				return true
			}
		}
		return false
	default:
		return true
	}
}
