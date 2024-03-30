package discord

import (
	"fmt"
	"regexp"

	"github.com/valyala/fasthttp"
)

var (
	JS_FILE_REGEX    = regexp.MustCompile(`assets/(sentry\.\w+)\.js`)
	BUILD_INFO_REGEX = regexp.MustCompile(`buildNumber\D+(\d+)"`)
)

func getLatestBuild() (string, error) {
	req := fasthttp.AcquireRequest()
	resp := fasthttp.AcquireResponse()
	defer fasthttp.ReleaseRequest(req)
	defer fasthttp.ReleaseResponse(resp)

	req.Header.SetMethod(fasthttp.MethodGet)
	req.SetRequestURI("https://discord.com/login")

	if err := requestClient.Do(req, resp); err != nil {
		return "", err
	}

	matches := JS_FILE_REGEX.FindStringSubmatch(string(resp.Body()))
	if len(matches) < 2 {
		return "", fmt.Errorf("failed to find JavaScript file URL")
	}
	asset := matches[1]

	req.Header.SetMethod(fasthttp.MethodGet)
	req.SetRequestURI(fmt.Sprintf("https://discord.com/assets/%s.js", asset))

	if err := requestClient.Do(req, resp); err != nil {
		return "", err
	}

	match := BUILD_INFO_REGEX.FindStringSubmatch(string(resp.Body()))
	if len(match) < 2 {
		return "", fmt.Errorf("failed to find build number")
	}
	return match[1], nil
}

func mustGetLatestBuild() string {
	if build, err := getLatestBuild(); err != nil {
		return "279382"
	} else {
		return build
	}
}
