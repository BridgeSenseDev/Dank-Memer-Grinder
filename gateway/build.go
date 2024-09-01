package gateway

import (
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
	"log"
	"regexp"
	"strings"
	"time"

	"github.com/valyala/fasthttp"
)

const fallbackBuildNumber = "9999"

var requestClient = fasthttp.Client{
	ReadBufferSize:                8192,
	ReadTimeout:                   time.Second * 5,
	WriteTimeout:                  time.Second * 5,
	NoDefaultUserAgentHeader:      true,
	DisableHeaderNamesNormalizing: true,
	DisablePathNormalizing:        true,
}

var headers = map[string]string{
	"Accept":             "*/*",
	"Accept-Language":    "en-GB,en-US;q=0.9,en;q=0.8",
	"Cache-Control":      "no-cache",
	"Pragma":             "no-cache",
	"Referer":            "https://discord.com/login",
	"Sec-Ch-Ua":          `"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"`,
	"Sec-Ch-Ua-Mobile":   "?0",
	"Sec-Ch-Ua-Platform": `"macOS"`,
	"Sec-Fetch-Dest":     "script",
	"Sec-Fetch-Mode":     "no-cors",
	"Sec-Fetch-Site":     "same-origin",
	"User-Agent":         utils.GetUserAgent(),
}

func (g *gatewayImpl) extractAssetFiles() ([]string, error) {
	req := fasthttp.AcquireRequest()
	defer fasthttp.ReleaseRequest(req)

	resp := fasthttp.AcquireResponse()
	defer fasthttp.ReleaseResponse(resp)

	req.SetRequestURI("https://discord.com/login")
	for k, v := range headers {
		req.Header.Set(k, v)
	}

	if err := requestClient.Do(req, resp); err != nil {
		return nil, err
	}

	body := string(resp.Body())
	pattern := `<script\s+src="([^"]+\.js)"\s+defer>\s*</script>`
	re := regexp.MustCompile(pattern)
	matches := re.FindAllStringSubmatch(body, -1)

	var files []string
	for _, match := range matches {
		if len(match) > 1 {
			files = append(files, match[1])
		}
	}
	return files, nil
}

func (g *gatewayImpl) getLatestBuild() string {
	files, err := g.extractAssetFiles()
	if err != nil {
		log.Println("Error extracting asset files:", err)
		return fallbackBuildNumber
	}

	var buildNumber string
	for _, file := range files {
		buildURL := "https://discord.com" + file

		req := fasthttp.AcquireRequest()
		defer fasthttp.ReleaseRequest(req)

		resp := fasthttp.AcquireResponse()
		defer fasthttp.ReleaseResponse(resp)

		req.SetRequestURI(buildURL)
		for k, v := range headers {
			req.Header.Set(k, v)
		}

		if err := requestClient.Do(req, resp); err != nil {
			log.Println("Error fetching JavaScript file:", err)
			continue
		}

		body := string(resp.Body())
		if !strings.Contains(body, "buildNumber") {
			continue
		}

		startIdx := strings.Index(body, "buildNumber:") + len("buildNumber:")
		endIdx := strings.Index(body[startIdx:], ",")
		buildNumber = strings.TrimSpace(body[startIdx : startIdx+endIdx])
		break
	}

	if buildNumber == "" {
		return fallbackBuildNumber
	}

	return buildNumber
}

func (g *gatewayImpl) mustGetLatestBuild() string {
	build := g.getLatestBuild()
	if build == fallbackBuildNumber {
		panic("Failed to get the latest build number")
	}
	return build
}
