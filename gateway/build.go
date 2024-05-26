package gateway

import (
	"fmt"
	"regexp"
	"time"

	"github.com/valyala/fasthttp"
)

var requestClient = fasthttp.Client{
	ReadBufferSize:                8192,
	ReadTimeout:                   time.Second * 5,
	WriteTimeout:                  time.Second * 5,
	NoDefaultUserAgentHeader:      true,
	DisableHeaderNamesNormalizing: true,
	DisablePathNormalizing:        true,
}

var (
	JsFileRegex    = regexp.MustCompile(`<script src="(/assets/\d{4,5}\.[^"]+\.js)" defer></script>`)
	BuildInfoRegex = regexp.MustCompile(`Build Number: "\).concat\("(\d+)"`)
)

func (g *gatewayImpl) getLatestBuild() (string, error) {
	req := fasthttp.AcquireRequest()
	resp := fasthttp.AcquireResponse()
	defer fasthttp.ReleaseRequest(req)
	defer fasthttp.ReleaseResponse(resp)

	req.Header.SetMethod(fasthttp.MethodGet)
	req.SetRequestURI("https://discord.com/app")

	if err := requestClient.Do(req, resp); err != nil {
		return "", err
	}

	matches := JsFileRegex.FindAllStringSubmatch(string(resp.Body()), -1)
	if len(matches) == 0 {
		g.Log("ERR", "Build number not found, falling back to 9999")
		return "9999", nil
	}
	for _, match := range matches {
		if len(match) < 2 {
			continue
		}
		asset := match[1]
		if asset == "" {
			continue
		}
		req.Header.SetMethod(fasthttp.MethodGet)
		req.SetRequestURI(fmt.Sprintf("https://discord.com%s", asset))
		if err := requestClient.Do(req, resp); err != nil {
			continue
		}
		match := BuildInfoRegex.FindStringSubmatch(string(resp.Body()))
		if len(match) < 2 {
			continue
		}
		return match[1], nil
	}

	g.Log("ERR", "Build number not found, falling back to 9999")
	return "9999", nil
}

func (g *gatewayImpl) mustGetLatestBuild() string {
	if build, err := g.getLatestBuild(); err != nil {
		panic(err)
	} else {
		return build
	}
}
