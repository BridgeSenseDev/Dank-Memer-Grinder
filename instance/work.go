package instance

import (
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
	"regexp"
	"strings"
)

const (
	cross = "<:CX:1071484097957994587>"
	tick  = "<:CY:1071484103762915348>"
)

var highestJob string

func getLastUnlockedCYJob(input string) string {
	reCY := regexp.MustCompile(fmt.Sprintf(`%s \[\*\*(.*?)\*\*]`, tick))
	reCX := regexp.MustCompile(fmt.Sprintf(`%s \*\*(.*?)\*\*`, cross))

	cyJobs := reCY.FindAllStringSubmatch(input, -1)
	cxJobs := reCX.FindAllStringSubmatch(input, -1)

	lockedJobs := make(map[string]bool)
	for _, job := range cxJobs {
		lockedJobs[job[1]] = true
	}

	for i := len(cyJobs) - 1; i >= 0; i-- {
		jobName := cyJobs[i][1]
		if !lockedJobs[jobName] {
			return jobName
		}
	}

	return ""
}

func (in *Instance) WorkMessageCreate(message gateway.EventMessage) {
	if !in.Cfg.Commands.Work.AutoWorkApply {
		return
	}
	embed := message.Embeds[0]

	if strings.Contains(embed.Description, "You don't currently have a job to work at") {
		utils.Log(utils.Others, utils.Info, in.SafeGetUsername(), "Applying for new job")
		in.PauseCommands(false)
		err := in.SendSubCommand("work", "list", nil, true)

		if err != nil {
			utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to send /work list command: %s", err.Error()))
		}
		return
	}

	if strings.Contains(embed.Title, "Available Jobs") {
		if len(strings.TrimSpace(getLastUnlockedCYJob(embed.Description))) != 0 {
			highestJob = getLastUnlockedCYJob(embed.Description)
		}

		err := in.ClickButton(message, 0, 2)
		if err != nil {
			utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click initial jobs button: %s", err.Error()))
		}
		return
	}

	if strings.Contains(embed.Title, "Congratulations, you are now working as a") {
		err := in.SendSubCommand("work", "shift", nil, true)
		if err != nil {
			utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to send /work shift command: %s", err.Error()))
		}
		in.UnpauseCommands()
	}
}

func (in *Instance) WorkMessageUpdate(message gateway.EventMessage) {
	if !in.Cfg.Commands.Work.AutoWorkApply {
		return
	}
	embed := message.Embeds[0]

	if strings.Contains(embed.Title, "Available Jobs") {
		if len(strings.TrimSpace(getLastUnlockedCYJob(embed.Description))) != 0 {
			highestJob = getLastUnlockedCYJob(embed.Description)
		}

		if strings.Count(embed.Description, cross) > 1 || message.Components[0].(*types.ActionsRow).Components[2].(*types.Button).Disabled {
			err := in.SendSubCommand("work", "apply", map[string]string{"job": highestJob}, true)
			if err != nil {
				utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to send /work apply command: %s", err.Error()))
			}

			utils.Log(utils.Others, utils.Info, in.SafeGetUsername(), fmt.Sprintf("Applied for job: %s", highestJob))
		} else {
			err := in.ClickButton(message, 0, 2)
			if err != nil {
				utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click next job button: %s", err.Error()))
			}
		}
	}
}
