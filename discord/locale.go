package discord

import "github.com/jeandeaual/go-locale"

func mustGetLocale() string {
	locale, err := locale.GetLocale()

	if err != nil {
		panic(err)
	}

	return locale
}
