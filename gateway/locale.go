package gateway

import "github.com/jeandeaual/go-locale"

func (g *gatewayImpl) mustGetLocale() string {
	getLocale, err := locale.GetLocale()

	if err != nil {
		panic(err)
	}

	return getLocale
}
