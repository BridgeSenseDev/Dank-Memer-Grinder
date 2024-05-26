package types

import (
	"encoding/json"
	"time"
)

type ReadyEventData struct {
	Version          int     `json:"v"`
	User             User    `json:"user"`
	Guilds           []Guild `json:"guilds"`
	SessionID        string  `json:"session_id"`
	ResumeGatewayURL string  `json:"resume_gateway_url"`
}

type MessageEventData struct {
	// Data is in different struct because it needs to be recursive
	MessageData
	ReferencedMessage MessageData `json:"referenced_message"`
}

type MessageInteraction struct {
	ID   string `json:"id,omitempty"`
	Type int    `json:"type,omitempty"`
	Name string `json:"name,omitempty"`
	User User   `json:"user,omitempty"`
}

type MessageData struct {
	Type             int                `json:"type,omitempty"`
	Content          string             `json:"content,omitempty"`
	ChannelID        string             `json:"channel_id,omitempty"`
	Embeds           []Embed            `json:"embeds,omitempty"`
	Reactions        []Reaction         `json:"reactions,omitempty"`
	Author           User               `json:"author,omitempty"`
	GuildID          string             `json:"guild_id,omitempty"`
	MessageID        string             `json:"id,omitempty"`
	Components       []MessageComponent `json:"-"`
	Attachments      []Attachment       `json:"attachments,omitempty"`
	Flags            int                `json:"flags,omitempty"`
	MessageReference MessageReference   `json:"message_reference,omitempty"`
	Interaction      MessageInteraction `json:"interaction,omitempty"`
	RawComponents    json.RawMessage    `json:"components,omitempty"`
	Timestamp        time.Time          `json:"timestamp"`
}

func (md *MessageData) UnmarshalJSON(b []byte) error {
	type Alias MessageData
	aux := &struct {
		*Alias
	}{
		Alias: (*Alias)(md),
	}
	if err := json.Unmarshal(b, &aux); err != nil {
		return err
	}

	if md.RawComponents != nil {
		var components []unmarshalableMessageComponent
		err := json.Unmarshal(md.RawComponents, &components)
		if err != nil {
			return err
		}

		md.Components = make([]MessageComponent, len(components))
		for i, v := range components {
			md.Components[i] = v.MessageComponent
		}
	}

	return nil
}

type Attachment struct {
	ID                 string `json:"id"`
	Filename           string `json:"filename"`
	Size               int    `json:"size"`
	URL                string `json:"url"`
	ProxyURL           string `json:"proxy_url"`
	Width              int    `json:"width"`
	Height             int    `json:"height"`
	ContentType        string `json:"content_type"`
	Placeholder        string `json:"placeholder"`
	PlaceholderVersion int    `json:"placeholder_version"`
}

type MessageReference struct {
	ChannelID string `json:"channel_id"`
	MessageID string `json:"message_id"`
	GuildID   string `json:"guild_id"`
}

type ModalData struct {
	Components    []MessageComponent `json:"-"`
	CustomID      string             `json:"custom_id"`
	Title         string             `json:"title"`
	ID            string             `json:"id"`
	ChannelID     string             `json:"channel_id"`
	RawComponents json.RawMessage    `json:"components,omitempty"`
}

func (md *ModalData) UnmarshalJSON(b []byte) error {
	type Alias ModalData
	aux := &struct {
		*Alias
	}{
		Alias: (*Alias)(md),
	}
	if err := json.Unmarshal(b, &aux); err != nil {
		return err
	}

	if md.RawComponents != nil {
		var components []unmarshalableMessageComponent
		err := json.Unmarshal(md.RawComponents, &components)
		if err != nil {
			return err
		}

		md.Components = make([]MessageComponent, len(components))
		for i, v := range components {
			md.Components[i] = v.MessageComponent
		}
	}

	return nil
}
