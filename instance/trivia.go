package instance

import (
	_ "embed"
	"encoding/json"
	"fmt"
	"regexp"
	"strings"

	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
	"github.com/rs/zerolog/log"
)

//go:embed trivia.json
var triviaJson []byte

var trivia map[string]interface{}

func init() {
	err := json.Unmarshal([]byte(triviaJson), &trivia)
	if err != nil {
		log.Error().Msgf("Failed to unmarshal trivia data: %v", err)
	}
}

func (in *Instance) Trivia(message *types.MessageEventData) {
	buttons := message.Components[0].(*types.ActionsRow).Components
	embed := message.Embeds[0]

	category := embed.Fields[1].Value
	re := regexp.MustCompile(`\*\*(.*?)\*\*`)
	question := strings.Trim(re.FindStringSubmatch(embed.Description)[0], "*")

	answer, ok := trivia[category].(map[string]interface{})[question]
	if !ok {
		in.Log("others", "ERR", fmt.Sprintf("Question not found in trivia data: %v", question))
		in.clickButtonBasedOnCondition(buttons, message, "", false)
		return
	}

	chance := utils.Rng.Float64()

	condition := chance > in.Cfg.Commands.Trivia.TriviaCorrectChance
	in.clickButtonBasedOnCondition(buttons, message, answer.(string), condition)
}

func (in *Instance) clickButtonBasedOnCondition(buttons []types.MessageComponent, message *types.MessageEventData, answer string, condition bool) {
	buttonIndices := make([]int, 0)
	for i, button := range buttons {
		if button.(*types.Button).Label == answer == condition {
			buttonIndices = append(buttonIndices, i)
		}
	}
	if len(buttonIndices) > 0 {
		randomIndex := buttonIndices[utils.Rng.Intn(len(buttonIndices))]
		err := in.ClickButton(message.MessageData, 0, randomIndex)
		if err != nil {
			in.Log("discord", "ERR", fmt.Sprintf("Failed to click trivia answer button: %s", err.Error()))
		}
	}
}
