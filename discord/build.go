package discord

import (
	"fmt"
	"regexp"

	"github.com/valyala/fasthttp"
)

var (
	JsFileRegex    = regexp.MustCompile(`<script src="(/assets/\d{4,5}\.[^"]+\.js)" defer></script>`)
	BuildInfoRegex = regexp.MustCompile(`Build Number: "\).concat\("(\d+)"`)
)

func getLatestBuild() (string, error) {
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
		fmt.Println("build number not found, falling back to 9999")
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

	fmt.Println("build number not found, falling back to 9999")
	return "9999", nil
}

func mustGetLatestBuild() string {
	if build, err := getLatestBuild(); err != nil {
		panic(err)
	} else {
		return build
	}
}
