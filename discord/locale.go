package discord

import "github.com/jeandeaual/go-locale"

func mustGetLocale() string {
	getLocale, err := locale.GetLocale()

	if err != nil {
		panic(err)
	}

	return getLocale
}
