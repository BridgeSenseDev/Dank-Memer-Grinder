package gateway

import (
	"encoding/json"
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"

	"github.com/valyala/fasthttp"
)

const fallbackBuildNumber = "9999"

type DiscordBuild struct {
	BuildNumber       string `json:"build_number"`
	ClientBuildNumber int    `json:"client_build_number"`
}

func (g *gatewayImpl) getLatestBuild() string {
	req := fasthttp.AcquireRequest()
	defer fasthttp.ReleaseRequest(req)

	resp := fasthttp.AcquireResponse()
	defer fasthttp.ReleaseResponse(resp)

	req.SetRequestURI("https://raw.githubusercontent.com/Pixens/Discord-Build-Number/refs/heads/main/discord.json")

	if err := fasthttp.Do(req, resp); err != nil {
		utils.Log(utils.Discord, utils.Error, g.SafeGetUsername(), fmt.Sprintf("Error fetching build number: %v", err))
		return fallbackBuildNumber
	}

	var build DiscordBuild
	if err := json.Unmarshal(resp.Body(), &build); err != nil {
		utils.Log(utils.Discord, utils.Error, g.SafeGetUsername(), fmt.Sprintf("Error parsing build number response: %v", err))
		return fallbackBuildNumber
	}

	if build.ClientBuildNumber == 0 {
		utils.Log(utils.Discord, utils.Error, g.SafeGetUsername(), "Invalid build number format in response")
		return fallbackBuildNumber
	}

	return fmt.Sprintf("%d", build.ClientBuildNumber)
}

func (g *gatewayImpl) mustGetLatestBuild() string {
	build := g.getLatestBuild()
	if build == fallbackBuildNumber {
		panic("Failed to get the latest build number")
	}
	return build
}
