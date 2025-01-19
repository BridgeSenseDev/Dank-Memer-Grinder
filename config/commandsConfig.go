package config

type CommandsConfig struct {
	Adventure AdventureCommandConfig `json:"adventure"`
	Beg       GeneralCommandConfig   `json:"beg"`
	Blackjack BlackjackCommandConfig `json:"blackjack"`
	Crime     CrimeCommandConfig     `json:"crime"`
	Daily     GeneralCommandConfig   `json:"daily"`
	Deposit   GeneralCommandConfig   `json:"deposit"`
	Dig       GeneralCommandConfig   `json:"dig"`
	Fish      FishCommandConfig      `json:"fish"`
	HighLow   GeneralCommandConfig   `json:"highlow"`
	Hunt      GeneralCommandConfig   `json:"hunt"`
	Pets      GeneralCommandConfig   `json:"pets"`
	PostMemes PostMemesCommandConfig `json:"postmemes"`
	Scratch   GeneralCommandConfig   `json:"scratch"`
	Search    SearchCommandConfig    `json:"search"`
	Stream    StreamCommandConfig    `json:"stream"`
	Trivia    TriviaCommandConfig    `json:"trivia"`
	Work      WorkCommandConfig      `json:"work"`
}

func (c *CommandsConfig) GetCommandsMap() map[string]GeneralCommandConfig {
	return map[string]GeneralCommandConfig{
		"Adventure": c.Adventure.GeneralCommandConfig,
		"Beg":       c.Beg,
		"Blackjack": c.Blackjack.GeneralCommandConfig,
		"Crime":     c.Crime.GeneralCommandConfig,
		"Daily":     c.Daily,
		"Deposit":   c.Deposit,
		"Dig":       c.Dig,
		"Fish":      c.Fish.GeneralCommandConfig,
		"HighLow":   c.HighLow,
		"Hunt":      c.Hunt,
		"Pets":      c.Pets,
		"PostMemes": c.PostMemes.GeneralCommandConfig,
		"Scratch":   c.Scratch,
		"Search":    c.Search.GeneralCommandConfig,
		"Stream":    c.Stream.GeneralCommandConfig,
		"Trivia":    c.Trivia.GeneralCommandConfig,
		"Work":      c.Work.GeneralCommandConfig,
		"Profile":   {State: true, Delay: 1800},
	}
}

type GeneralCommandConfig struct {
	State bool  `json:"state"`
	Delay int64 `json:"delay"`
}

type Adventure string

const (
	Brazil   Adventure = "brazil"
	Space    Adventure = "space"
	Vacation Adventure = "vacation"
	West     Adventure = "west"
)

type AdventureCommandConfig struct {
	GeneralCommandConfig
	AdventureOption Adventure `json:"adventureOption"`
}

type BlackjackCommandConfig struct {
	GeneralCommandConfig
	Amount              string `json:"amount"`
	ManuallyRunCommands bool   `json:"manuallyRunCommands"`
}

type CrimeCommandConfig struct {
	GeneralCommandConfig
	Priority       []string `json:"priority"`
	SecondPriority []string `json:"secondPriority"`
	Avoid          []string `json:"avoid"`
}

type FishCommandConfig struct {
	GeneralCommandConfig
	SellCoinsValue int `json:"sellCoinsValue"`
}

type StreamCommandConfig struct {
	GeneralCommandConfig
	Order []int `json:"order"`
}

type SearchCommandConfig struct {
	GeneralCommandConfig
	Priority       []string `json:"priority"`
	SecondPriority []string `json:"secondPriority"`
	Avoid          []string `json:"avoid"`
}

type PostMemesCommandConfig struct {
	GeneralCommandConfig
	Platform []int `json:"platform"`
}

type TriviaCommandConfig struct {
	GeneralCommandConfig
	TriviaCorrectChance float64 `json:"triviaCorrectChance"`
}

type WorkCommandConfig struct {
	GeneralCommandConfig
	AutoWorkApply bool `json:"autoWorkApply"`
}
