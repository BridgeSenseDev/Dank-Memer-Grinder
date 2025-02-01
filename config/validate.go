package config

import (
	"errors"
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
)

func (c *Config) Validate() error {
	if !isValidOnlineStatus(c.DiscordStatus) {
		return fmt.Errorf("invalid discordStatus: %s", c.DiscordStatus)
	}

	if err := c.Gui.Validate(); err != nil {
		return fmt.Errorf("gui: %w", err)
	}

	if err := c.Cooldowns.Validate(); err != nil {
		return fmt.Errorf("cooldowns: %w", err)
	}

	for i, account := range c.Accounts {
		if err := account.Validate(); err != nil {
			return fmt.Errorf("accounts[%d]: %w", i, err)
		}
	}

	if err := c.AutoBuy.Validate(); err != nil {
		return fmt.Errorf("autoBuy: %w", err)
	}

	if err := c.Commands.Validate(); err != nil {
		return fmt.Errorf("commands: %w", err)
	}

	return nil
}

func isValidOnlineStatus(status types.OnlineStatus) bool {
	switch status {
	case types.OnlineStatusOnline, types.OnlineStatusDND,
		types.OnlineStatusIdle, types.OnlineStatusInvisible,
		types.OnlineStatusOffline:
		return true
	default:
		return false
	}
}

func (g *GuiConfig) Validate() error {
	switch g.Theme {
	case System, Dark, Light:
		return nil
	default:
		return fmt.Errorf("invalid theme: %s", g.Theme)
	}
}

func (c *Cooldowns) Validate() error {
	if err := c.ButtonClickDelay.Validate(); err != nil {
		return fmt.Errorf("buttonClickDelay: %w", err)
	}
	if err := c.CommandInterval.Validate(); err != nil {
		return fmt.Errorf("commandInterval: %w", err)
	}
	return nil
}

func (d *Delays) Validate() error {
	if d.MinDelay < 0 || d.MaxDelay < 0 {
		return errors.New("delays cannot be negative")
	}
	if d.MinDelay > d.MaxDelay {
		return errors.New("minDelay cannot be greater than maxDelay")
	}
	return nil
}

func (a *AccountsConfig) Validate() error {
	if a.Token == "" {
		return errors.New("token is required")
	}
	if a.ChannelID == "" {
		return errors.New("channelID is required")
	}
	return nil
}

func (ab *AutoBuyConfig) Validate() error {
	if err := ab.HuntingRifle.Validate(); err != nil {
		return fmt.Errorf("huntingRifle: %w", err)
	}
	if err := ab.Shovel.Validate(); err != nil {
		return fmt.Errorf("shovel: %w", err)
	}
	if err := ab.LifeSavers.Validate(); err != nil {
		return fmt.Errorf("lifeSavers: %w", err)
	}
	return nil
}

func (g *GeneralAutobuyConfig) Validate() error {
	if g.State && g.Amount < 0 {
		return errors.New("amount must be >= 0 when enabled")
	}
	return nil
}

func (c *CommandsConfig) Validate() error {
	commandsMap := c.GetCommandsMap()

	for name, cmd := range commandsMap {
		if cmd.Delay < 0 {
			return fmt.Errorf("%s: delay cannot be negative", name)
		}
	}

	if err := c.Adventure.Validate(); err != nil {
		return fmt.Errorf("adventure: %w", err)
	}

	if err := c.Blackjack.Validate(); err != nil {
		return fmt.Errorf("blackjack: %w", err)
	}

	if err := c.Crime.Validate(); err != nil {
		return fmt.Errorf("crime: %w", err)
	}

	if err := c.Fish.Validate(); err != nil {
		return fmt.Errorf("fish: %w", err)
	}

	if err := c.Stream.Validate(); err != nil {
		return fmt.Errorf("stream: %w", err)
	}

	if err := c.Search.Validate(); err != nil {
		return fmt.Errorf("search: %w", err)
	}

	if err := c.PostMemes.Validate(); err != nil {
		return fmt.Errorf("postMemes: %w", err)
	}

	if err := c.Trivia.Validate(); err != nil {
		return fmt.Errorf("trivia: %w", err)
	}

	return nil
}

func (a *AdventureCommandConfig) Validate() error {
	validOptions := map[AdventureOption]bool{
		Brazil:   true,
		Space:    true,
		Vacation: true,
		West:     true,
	}

	if !validOptions[a.AdventureOption] {
		return fmt.Errorf("invalid adventure option: %s", a.AdventureOption)
	}
	return nil
}

func (b *BlackjackCommandConfig) Validate() error {
	if b.Amount == "" {
		return errors.New("amount is required")
	}
	return nil
}

func (c *CrimeCommandConfig) Validate() error {
	if len(c.Priority) == 0 && len(c.SecondPriority) == 0 {
		return errors.New("must have at least one priority or secondPriority crime")
	}
	return nil
}

func (f *FishCommandConfig) Validate() error {
	validLocations := map[FishLocation]bool{
		VertigoBeach:        true,
		WilyRiver:           true,
		UnderwaterSanctuary: true,
		CampGuillermo:       true,
		MysticPond:          true,
		IceCaves:            true,
		SnowyMountain:       true,
		ScurvyWaters:        true,
		NorthpointCabin:     true,
	}

	if len(f.FishLocation) == 0 {
		return errors.New("at least one fish location must be specified")
	}

	for _, location := range f.FishLocation {
		if !validLocations[location] {
			return fmt.Errorf("invalid fish location: %s", location)
		}
	}

	if f.SellCoinsValue < 0 {
		return errors.New("sellCoinsValue cannot be negative")
	}

	return nil
}

func (s *StreamCommandConfig) Validate() error {
	if len(s.Order) == 0 {
		return errors.New("order cannot be empty")
	}
	return nil
}

func (s *SearchCommandConfig) Validate() error {
	if len(s.Priority) == 0 && len(s.SecondPriority) == 0 {
		return errors.New("must have at least one priority or secondPriority search")
	}
	return nil
}

func (p *PostMemesCommandConfig) Validate() error {
	if len(p.Platform) == 0 {
		return errors.New("platform cannot be empty")
	}
	return nil
}

func (t *TriviaCommandConfig) Validate() error {
	if t.TriviaCorrectChance < 0 || t.TriviaCorrectChance > 1 {
		return errors.New("triviaCorrectChance must be between 0 and 1")
	}
	return nil
}
