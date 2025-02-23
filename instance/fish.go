package instance

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
	"github.com/valyala/fasthttp"
	_ "golang.org/x/image/webp"
	"image"
	"regexp"
	"slices"
	"strconv"
	"strings"
	"time"
)

const (
	bombHash = "705646c414efd35eaa8d25ec4d38c2bea01aea5174d5ce8d3644db11de584cd4"
	fishHash = "2e41961de003cdbd29f06f7dd15223599b068b000f214c44f008c833a1114504"
	gridSize = 3
)

var (
	autoBuySuccess = false
	lastAutoBuy    = time.Now().Add(-6 * time.Minute)
)

type Cell struct {
	Row, Col int
}

func (in *Instance) FishMessageCreate(message gateway.EventMessage) {
	// Everything can be a message update
	in.FishMessageUpdate(message)
}

func (in *Instance) FishMessageUpdate(message gateway.EventMessage) {
	embed := message.Embeds[0]

	if strings.Contains(embed.Title, "Fishing Tutorial") && !strings.Contains(embed.Description, "Tutorial is over") {
		embed = message.Embeds[1]

		for row, rowData := range message.Components {
			for col, colData := range rowData.(*types.ActionsRow).Components {
				if button, ok := colData.(*types.Button); ok {
					if button.Disabled || strings.Contains(button.Label, "Season Pass") {
						continue
					}

					err := in.ClickButton(message, row, col)
					if err != nil {
						utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click fishing tutorial button: %s", err.Error()))
					}
					return
				}
			}
		}
	} else if embed.Title == "Fishing" {
		if !in.Cfg.Commands.Fish.FishOnly {
			in.PauseCommands(false)
		}

		// Check location
		currentLocation := strings.TrimSpace(strings.SplitN(embed.Fields[1].Value, ">", 2)[1])
		locationValid := false
		for _, loc := range in.Cfg.Commands.Fish.FishLocation {
			if currentLocation == string(loc) {
				locationValid = true
				break
			}
		}

		if !locationValid {
			err := in.ClickButton(message, 0, 1)
			if err != nil {
				utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(),
					fmt.Sprintf("Failed to click fish location button: %s", err.Error()))
			}
			return
		}

		// Check if buckets full
		re := regexp.MustCompile(`(\d+)\s*/\s*(\d+)`)
		matches := re.FindStringSubmatch(embed.Fields[3].Value)

		if len(matches) == 3 {
			current := matches[1]
			maxSpace := matches[2]

			if current == maxSpace && current != "0" {
				err := in.SendSubCommand("fish", "buckets", nil, false)
				if err != nil {
					utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to send fish buckets command: %s", err.Error()))
				}
				return
			}
		}

		// Check if equipment available, if not already tried to buy equipment in past 5 minutes
		if in.Cfg.Commands.Fish.AutoEquipment && strings.Contains(embed.Fields[0].Value, "Bare Hand") && !(!autoBuySuccess && lastAutoBuy.Add(5*time.Minute).After(time.Now())) {
			// Avoid hold tight error
			<-utils.Sleep(utils.RandSeconds(2, 5))

			err := in.ClickButton(message, 0, 0)
			if err != nil {
				utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click fishing equipment button: %s", err.Error()))
			}
			return
		}

		// Go fishing
		err := in.ClickButton(message, 0, 2)
		if err != nil {
			utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click go fishing button: %s", err.Error()))
		}
	} else if embed.Title == "Viewing Bucket Slots" {
		// Click empty buckets if buckets full
		re := regexp.MustCompile(`All Buckets Space:[\s\S]*?(\d+)\s*/\s*(\d+)`)
		matches := re.FindStringSubmatch(embed.Description)

		if len(matches) == 3 {
			current := matches[1]
			maxSpace := matches[2]
			if current == maxSpace && current != "0" {
				err := in.ClickButton(message, 1, 1)
				if err != nil {
					utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click sell all fish button: %s", err.Error()))
				}
			}
		}
	} else if embed.Title == "Picking Equipment" {
		if embed.Fields[0].Name != "Bare Hand" {
			err := in.ClickButton(message, 2, 0)
			if err != nil {
				utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click go back in fish equipment: %s", err.Error()))
			}
			return
		}

		options := message.Components[0].(*types.ActionsRow).Components[0].(*types.SelectMenu).Options
		slices.Reverse(options)

		for _, option := range options {
			if option.Description == "" {
				continue
			}

			re := regexp.MustCompile(`You own: (\d+)`)
			matches := re.FindStringSubmatch(option.Description)

			if len(matches) < 2 {
				utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to find fishing equipment count from description: %s", option.Description))
				return
			}

			count, _ := strconv.Atoi(matches[1])
			if count > 0 {
				err := in.ChooseSelectMenu(message, 0, 0, []string{option.Value})
				if err != nil {
					utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to choose fishing equipment: %s", err.Error()))
				}
				return
			}
		}

		// Dont autobuy equipment again if last autobuy less than 5 minutes ago
		if lastAutoBuy.Add(5 * time.Minute).After(time.Now()) {
			return
		}

		// No better equipment available, buy fishing rod
		// Make sure fish doesn't run again too soon
		in.LastRan["Fish"] = time.Now()
		in.setAutoBuyState(2, 1, "fishingrodtool", 20)
		resultChan := in.StartAutoBuy("fish", "shop")

		go func() {
			select {
			case result := <-resultChan:
				utils.Log(utils.Others, utils.Info, in.SafeGetUsername(), result.Message)
				lastAutoBuy = time.Now()

				// Avoid hold tight error
				<-utils.Sleep(utils.RandSeconds(2, 5))

				if result.Success {
					autoBuySuccess = true
					err := in.ChooseSelectMenu(message, 0, 0, []string{"fishing-rod"})
					if err != nil {
						utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to select fishing rod: %s", err.Error()))
					}
				} else {
					err := in.ClickDmButton(message, 2, 0)
					if err != nil {
						utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click fishing rod button: %s", err.Error()))
					}
				}
			case <-time.After(45 * time.Second):
				utils.Log(utils.Others, utils.Info, in.SafeGetUsername(), "Fish shop autobuy timed out")
				lastAutoBuy = time.Now()

				// Avoid hold tight error
				<-utils.Sleep(utils.RandSeconds(2, 5))

				in.UnpauseCommands()
			}
		}()
	} else if strings.Contains(embed.Title, "You caught") || embed.Title == "There was nothing to catch." {
		if strings.Contains(embed.Description, "You have no more bucket space") {
			in.LastRan["Fish"] = time.Now()

			<-utils.Sleep(utils.RandSeconds(2, 5))
			err := in.SendSubCommand("fish", "buckets", nil, false)
			if err != nil {
				utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to send fish buckets command: %s", err.Error()))
			}

			// Send new fish command 50% of the time
			if in.Cfg.Commands.Fish.FishOnly && utils.Rng.Intn(2) == 0 {
				return
			}
		} else if strings.Contains(message.Embeds[1].Description, "Bare Hand") && in.Cfg.Commands.Fish.AutoEquipment {
			// Avoid hold tight error
			<-utils.Sleep(utils.RandSeconds(2, 5))
			err := in.ClickButton(message, 0, 0)
			if err != nil {
				utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click go back button: %s", err.Error()))
			}
			return
		}

		if in.Cfg.Commands.Fish.FishOnly {
			in.LastRan["Fish"] = time.Now().Add(time.Minute)

			re := regexp.MustCompile(`<t:(\d+):R>`)
			matches := re.FindStringSubmatch(embed.Description)
			if len(matches) < 2 {
				utils.Log(utils.Important, utils.Error, in.SafeGetUsername(), "Failed to find fish timestamp")
				return
			}

			ts, err := strconv.ParseInt(matches[1], 10, 64)
			if err != nil {
				utils.Log(utils.Important, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to parse fish timestamp: %s", err.Error()))
				return
			}

			cooldown := time.Duration(ts-time.Now().Unix()) * time.Second

			<-utils.Sleep(cooldown + utils.RandSeconds(in.Cfg.Commands.Fish.FishOnlyDelay.MinSeconds, in.Cfg.Commands.Fish.FishOnlyDelay.MaxSeconds))

			if in.IsPaused() {
				return
			}

			err = in.ClickButton(message, 0, 1)
			if err != nil {
				utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click fish again button: %s", err.Error()))
			}
		} else {
			in.UnpauseCommands()
		}
	} else if embed.Image != nil && strings.Contains(embed.Image.URL, "catch.webp") {
		// Move next step in fish game
		img, err := in.downloadAndDecodeImage(embed.Image.URL)
		if err != nil {
			utils.Log(utils.Important, utils.Error, in.SafeGetUsername(), err.Error())
			return
		}

		cellWidth, cellHeight := img.Bounds().Dx()/gridSize, img.Bounds().Dy()/gridSize
		in.handleCatchUpdate(img, cellWidth, cellHeight, message)
	} else if embed.Title == "Selling Creatures" {
		// Choose between coins / tokens
		buttonLabel := message.Components[0].(*types.ActionsRow).Components[1].(*types.Button).Label
		coins, _ := strconv.Atoi(strings.ReplaceAll(regexp.MustCompile(`(\d+(?:\.\d+)?)[kKmM]?`).FindStringSubmatch(strings.ReplaceAll(buttonLabel, ",", ""))[1], ".", ""))
		if coins > in.Cfg.Commands.Fish.SellCoinsValue {
			err := in.ClickButton(message, 0, 1)
			if err != nil {
				utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click sell for coins button: %s", err.Error()))
			}
		} else {
			err := in.ClickButton(message, 0, 2)
			if err != nil {
				utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click sell for tokens button: %s", err.Error()))
			}
		}
		if !in.Cfg.Commands.Fish.FishOnly {
			in.UnpauseCommands()
		}
	} else if embed.Title == "Picking Location" {
		options := message.Components[0].(*types.ActionsRow).Components[0].(*types.SelectMenu).Options
		chosenLocation := in.Cfg.Commands.Fish.FishLocation[utils.Rng.Intn(len(in.Cfg.Commands.Fish.FishLocation))]

		for _, option := range options {
			if option.Label == string(chosenLocation) {
				if option.Default {
					// Click travel to button
					err := in.ClickButton(message, 1, 1)
					if err != nil {
						utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click travel to button: %s", err.Error()))
					}
				} else {
					// Change location select menu
					err := in.ChooseSelectMenu(message, 0, 0, []string{option.Value})
					if err != nil {
						utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to choose fish location: %s", err.Error()))
					}
				}
			}
		}
	} else if embed.Title == "Traveling..." {
		if !in.Cfg.Commands.Fish.FishOnly {
			in.UnpauseCommands()
		}

		match := regexp.MustCompile(`<t:(\d+):[a-zA-Z]>`).FindStringSubmatch(embed.Fields[1].Value)
		ts, _ := strconv.ParseInt(match[1], 10, 64)
		in.LastRan["Fish"] = in.LastRan["Fish"].Add(
			time.Unix(ts, 0).Sub(time.Now()),
		)
	}
}

func (in *Instance) downloadAndDecodeImage(url string) (image.Image, error) {
	statusCode, body, err := fasthttp.Get(nil, url)
	if err != nil {
		return nil, fmt.Errorf("failed to download fish image: %w", err)
	}
	if statusCode != fasthttp.StatusOK {
		return nil, fmt.Errorf("unexpected status code: %d", statusCode)
	}

	img, _, err := image.Decode(bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("error reading downloaded fish image: %w", err)
	}
	return img, nil
}

func (in *Instance) handleCatchUpdate(img image.Image, cellWidth, cellHeight int, message gateway.EventMessage) {
	bombPositions, fishPosition, hookPosition := findPositions(img, cellWidth, cellHeight)

	if fishPosition == nil {
		err := in.ClickButton(message, 0, 2)
		if err != nil {
			utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Error clicking catch button: %s", err))
		}
		return
	}

	grid := initializeGrid(bombPositions, *fishPosition)
	path := findPath(grid, hookPosition, *fishPosition)
	direction := convertPathToDirection(path)

	err := in.ClickButton(message, 0, direction)
	if err != nil {
		utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click fish button: %s", err.Error()))
		return
	}
}

func findPositions(img image.Image, cellWidth, cellHeight int) ([]Cell, *Cell, Cell) {
	var bombPositions []Cell
	var fishPosition *Cell
	var hookPosition Cell

	for i := 0; i < gridSize; i++ {
		for j := 0; j < gridSize; j++ {
			hash := calculateGridHash(img, j*cellWidth, i*cellHeight, cellWidth, cellHeight)
			switch hash {
			case bombHash:
				bombPositions = append(bombPositions, Cell{Row: i, Col: j})
			case fishHash:
				fishPos := Cell{Row: i, Col: j}
				fishPosition = &fishPos
			case "8605b972256b2b2f9774e77c807e2f17782e655bc5a9345229deb74638f53640":
			default:
				hookPosition = Cell{Row: i, Col: j}
			}
		}
	}
	return bombPositions, fishPosition, hookPosition
}

func calculateGridHash(img image.Image, x, y, width, height int) string {
	hasher := sha256.New()
	for dy := 0; dy < height; dy++ {
		for dx := 0; dx < width; dx++ {
			r, g, b, _ := img.At(x+dx, y+dy).RGBA()
			hasher.Write([]byte{byte(r >> 8), byte(g >> 8), byte(b >> 8)})
		}
	}
	return hex.EncodeToString(hasher.Sum(nil))
}

func initializeGrid(bombPositions []Cell, fishPosition Cell) [][]string {
	grid := make([][]string, gridSize)
	for i := range grid {
		grid[i] = make([]string, gridSize)
	}
	for _, bomb := range bombPositions {
		grid[bomb.Row][bomb.Col] = "B"
	}
	grid[fishPosition.Row][fishPosition.Col] = "F"
	return grid
}

func findPath(grid [][]string, start, end Cell) []Cell {
	queue := [][]Cell{{start}}
	visited := make(map[Cell]bool)

	for len(queue) > 0 {
		path := queue[0]
		queue = queue[1:]
		cell := path[len(path)-1]

		if cell == end {
			return path
		}

		if !visited[cell] {
			visited[cell] = true
			neighbors := getValidNeighbors(grid, cell)
			utils.Rng.Shuffle(len(neighbors), func(i, j int) { neighbors[i], neighbors[j] = neighbors[j], neighbors[i] })

			for _, neighbor := range neighbors {
				if !visited[neighbor] {
					newPath := append(append([]Cell{}, path...), neighbor)
					queue = append(queue, newPath)
				}
			}
		}
	}
	return nil
}

func getValidNeighbors(grid [][]string, cell Cell) []Cell {
	neighbors := []Cell{
		{Row: cell.Row - 1, Col: cell.Col}, // Up
		{Row: cell.Row + 1, Col: cell.Col}, // Down
		{Row: cell.Row, Col: cell.Col - 1}, // Left
		{Row: cell.Row, Col: cell.Col + 1}, // Right
	}

	var valid []Cell
	for _, n := range neighbors {
		if n.Row >= 0 && n.Row < gridSize && n.Col >= 0 && n.Col < gridSize && grid[n.Row][n.Col] != "B" {
			valid = append(valid, n)
		}
	}
	return valid
}

func convertPathToDirection(path []Cell) int {
	prev, curr := path[0], path[1]
	switch {
	case curr.Row < prev.Row:
		return 1 // Up
	case curr.Row > prev.Row:
		return 3 // Down
	case curr.Col < prev.Col:
		return 0 // Left
	case curr.Col > prev.Col:
		return 4 // Right
	default:
		return -1
	}
}
