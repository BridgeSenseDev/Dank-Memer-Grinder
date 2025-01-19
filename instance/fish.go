package instance

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
	"github.com/valyala/fasthttp"
	_ "golang.org/x/image/webp"
	"image"
	"regexp"
	"strconv"
	"strings"
	"sync"
)

var (
	directions      []int
	currentStep     int
	directionsMutex sync.Mutex
)

const (
	bombHash     = "705646c414efd35eaa8d25ec4d38c2bea01aea5174d5ce8d3644db11de584cd4"
	fishHash     = "2e41961de003cdbd29f06f7dd15223599b068b000f214c44f008c833a1114504"
	startingHash = "c5558c0acbf5307034ba5ae73c1f8a778459a576251a60d419ff6d986c42e851"
	gridSize     = 3
	startRow     = 2
	startCol     = 1
)

type Cell struct {
	Row, Col int
}

func (in *Instance) FishMessageCreate(message gateway.EventMessage) {
	embed := message.Embeds[0]

	if embed.Title == "Fishing" {
		re := regexp.MustCompile(`(\d+)\s*/\s*(\d+)`)
		matches := re.FindStringSubmatch(embed.Fields[3].Value)

		if len(matches) == 3 {
			current := matches[1]
			maxSpace := matches[2]

			if current == maxSpace && current != "0" {
				in.PauseCommands(false)
				err := in.SendSubCommand("fish", "buckets", nil, false)
				if err != nil {
					utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to send fish buckets command: %s", err.Error()))
				}
				return
			}
		}

		in.PauseCommands(false)
		err := in.ClickButton(message, 0, 2)
		if err != nil {
			utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click go fishing button: %s", err.Error()))
		}
		return
	}

	if embed.Title == "Viewing Bucket Slots" {
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
		return
	}
}

func (in *Instance) FishMessageUpdate(message gateway.EventMessage) {
	embed := message.Embeds[0]

	if embed.Image != nil && strings.Contains(embed.Image.URL, "catch.webp") {
		img, err := in.downloadAndDecodeImage(embed.Image.URL)
		if err != nil {
			utils.Log(utils.Important, utils.Error, in.SafeGetUsername(), err.Error())
			return
		}

		cellWidth, cellHeight := img.Bounds().Dx()/gridSize, img.Bounds().Dy()/gridSize
		bottomMiddleHash := calculateGridHash(img, cellWidth, 2*cellHeight, cellWidth, cellHeight)

		if bottomMiddleHash == startingHash {
			in.handleFirstUpdate(img, cellWidth, cellHeight, message)
		} else {
			in.handleSubsequentUpdate(message)
		}
		return
	}

	if embed.Title == "There was nothing to catch." {
		in.UnpauseCommands()
		return
	}

	if strings.Contains(embed.Description, "You have no more bucket space") {
		in.PauseCommands(false)
		err := in.SendSubCommand("fish", "buckets", nil, false)
		if err != nil {
			utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to send fish buckets command: %s", err.Error()))
		}
		return
	}

	if embed.Title == "Selling Creatures" {
		coins, _ := strconv.Atoi(strings.ReplaceAll(regexp.MustCompile(`(\d+(?:\.\d+)?)[kKmM]?`).FindStringSubmatch("Sell for 250,000 Coins")[1], ".", ""))
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
		in.UnpauseCommands()
		return
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

func (in *Instance) handleFirstUpdate(img image.Image, cellWidth, cellHeight int, message gateway.EventMessage) {
	bombPositions, fishPosition := findBombsAndFish(img, cellWidth, cellHeight)

	directionsMutex.Lock()
	defer directionsMutex.Unlock()

	directions = in.SolveFishingGame(bombPositions, fishPosition)
	currentStep = 0

	if len(directions) > 0 {
		err := in.ClickButton(message, 0, directions[currentStep])
		if err != nil {
			utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click fish button: %s", err.Error()))
			return
		}
		currentStep++
	}
}

func (in *Instance) handleSubsequentUpdate(message gateway.EventMessage) {
	directionsMutex.Lock()
	defer directionsMutex.Unlock()

	if currentStep < len(directions) {
		err := in.ClickButton(message, 0, directions[currentStep])
		if err != nil {
			utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click fish button: %s", err.Error()))
			return
		}
		currentStep++
	} else {
		err := in.ClickButton(message, 0, 2)
		if err != nil {
			utils.Log(utils.Discord, utils.Error, in.SafeGetUsername(), fmt.Sprintf("Failed to click fish button: %s", err.Error()))
			return
		}
		in.UnpauseCommands()
	}
}

func findBombsAndFish(img image.Image, cellWidth, cellHeight int) ([]Cell, Cell) {
	var bombPositions []Cell
	var fishPosition Cell

	for i := 0; i < gridSize; i++ {
		for j := 0; j < gridSize; j++ {
			hash := calculateGridHash(img, j*cellWidth, i*cellHeight, cellWidth, cellHeight)
			switch hash {
			case bombHash:
				bombPositions = append(bombPositions, Cell{Row: i, Col: j})
			case fishHash:
				fishPosition = Cell{Row: i, Col: j}
			}
		}
	}
	return bombPositions, fishPosition
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

func (in *Instance) SolveFishingGame(bombPositions []Cell, fishPosition Cell) []int {
	grid := initializeGrid(bombPositions, fishPosition)
	path := findPath(grid, Cell{Row: startRow, Col: startCol}, fishPosition)
	return convertPathToDirections(path)
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

func convertPathToDirections(path []Cell) []int {
	directions = make([]int, 0, len(path)-1)
	for i := 1; i < len(path); i++ {
		prev, curr := path[i-1], path[i]
		switch {
		case curr.Row < prev.Row:
			directions = append(directions, 1) // Up
		case curr.Row > prev.Row:
			directions = append(directions, 3) // Down
		case curr.Col < prev.Col:
			directions = append(directions, 0) // Left
		case curr.Col > prev.Col:
			directions = append(directions, 4) // Right
		}
	}
	return directions
}
