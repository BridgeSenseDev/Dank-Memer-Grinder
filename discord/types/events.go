package types

import (
	"encoding/json"
	"time"
)

type Opcode struct {
	Op int `json:"op"`
}

type HelloEvent struct {
	Opcode
	D struct {
		HeartbeatInterval int `json:"heartbeat_interval"`
	} `json:"d"`
}

type ResumePayload struct {
	Op int               `json:"op"`
	D  ResumePayloadData `json:"d"`
}

type ResumePayloadData struct {
	Token     string `json:"token"`
	SessionID string `json:"session_id"`
	Seq       int    `json:"seq"`
}

type IdentifyPayload struct {
	Op int64               `json:"op"`
	D  IdentifyPayloadData `json:"d"`
}

type IdentifyPayloadData struct {
	Token        string          `json:"token"`
	Capabilities int64           `json:"capabilities"`
	Properties   SuperProperties `json:"properties"`
	Compress     bool            `json:"compress"`
	ClientState  ClientState     `json:"client_state"`
}

type ClientState struct {
	GuildVersions            GuildVersions `json:"guild_versions"`
	HighestLastMessageID     string        `json:"highest_last_message_id"`
	ReadStateVersion         int64         `json:"read_state_version"`
	UserGuildSettingsVersion int64         `json:"user_guild_settings_version"`
	UserSettingsVersion      int64         `json:"user_settings_version"`
	PrivateChannelsVersion   string        `json:"private_channels_version"`
	APICodeVersion           int64         `json:"api_code_version"`
}

type GuildVersions struct {
}

type SuperProperties struct {
	OS                     string `json:"os"`
	Browser                string `json:"browser"`
	Device                 string `json:"device"`
	SystemLocale           string `json:"system_locale"`
	BrowserUserAgent       string `json:"browser_user_agent"`
	BrowserVersion         string `json:"browser_version"`
	OSVersion              string `json:"os_version"`
	Referrer               string `json:"referrer"`
	ReferringDomain        string `json:"referring_domain"`
	ReferrerCurrent        string `json:"referrer_current"`
	ReferringDomainCurrent string `json:"referring_domain_current"`
	ReleaseChannel         string `json:"release_channel"`
	ClientBuildNumber      string `json:"client_build_number"`
	ClientEventSource      any    `json:"client_event_source"`
}

// https://discord.com/developers/docs/topics/gateway-events#payload-structure
type DefaultEvent struct {
	Op int    `json:"op"`
	T  string `json:"t,omitempty"`
	S  int    `json:"s,omitempty"`
	D  any    `json:"d,omitempty"`
}

type ReadyEvent struct {
	Op int64          `json:"op"`
	D  ReadyEventData `json:"d"`
}

type ReadyEventData struct {
	Version          int     `json:"v"`
	User             User    `json:"user"`
	Guilds           []Guild `json:"guilds"`
	SessionID        string  `json:"session_id"`
	ResumeGatewayURL string  `json:"resume_gateway_url"`
}

type MessageEvent struct {
	Op int              `json:"op"`
	D  MessageEventData `json:"d"`
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

type ModalEvent struct {
	Op int       `json:"op"`
	D  ModalData `json:"d"`
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
