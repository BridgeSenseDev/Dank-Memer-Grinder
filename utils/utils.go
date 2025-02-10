package utils

import (
	"encoding/json"
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/config"
	"github.com/valyala/fasthttp"
	"github.com/wailsapp/wails/v3/pkg/application"
	"log/slog"
	"math/rand"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

var src = rand.NewSource(time.Now().UnixNano())
var Rng = rand.New(src)

func RandSeconds(min, max float32) time.Duration {
	return time.Duration((min + Rng.Float32()*(max-min)) * float32(time.Second))
}

func RandMinutes(min, max float32) time.Duration {
	return time.Duration((min + Rng.Float32()*(max-min)) * float32(time.Minute))
}

func RandHours(min, max float32) time.Duration {
	return time.Duration((min + Rng.Float32()*(max-min)) * float32(time.Hour))
}

func Contains(slice []string, item string) bool {
	for _, a := range slice {
		if a == item {
			return true
		}
	}
	return false
}

func GetMaxPriority(buttonPriority map[int]int) int {
	var m = -2
	var maxIndices []int

	for i, priority := range buttonPriority {
		if priority > m {
			m = priority
			maxIndices = []int{i}
		} else if priority == m {
			maxIndices = append(maxIndices, i)
		}
	}

	randomIndex := maxIndices[Rng.Intn(len(maxIndices))]

	return randomIndex
}

func Sleep(duration time.Duration) <-chan bool {
	done := make(chan bool)

	go func() {
		time.Sleep(duration)
		done <- true
	}()

	return done
}

type browserVersionResponse struct {
	Versions []struct {
		Version string `json:"version"`
	} `json:"versions"`
}

func GetUserAgent() string {
	url := "https://versionhistory.googleapis.com/v1/chrome/platforms/win/channels/stable/versions"

	req := fasthttp.AcquireRequest()
	defer fasthttp.ReleaseRequest(req)
	req.SetRequestURI(url)

	resp := fasthttp.AcquireResponse()
	defer fasthttp.ReleaseResponse(resp)

	var version string

	if err := fasthttp.Do(req, resp); err == nil {
		var data browserVersionResponse
		if err = json.Unmarshal(resp.Body(), &data); err == nil {
			major := strings.Split(data.Versions[0].Version, ".")[0]
			version = fmt.Sprintf("%s.0.0.0", major)
		}
	}

	return fmt.Sprintf("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36", version)
}

func FormatNumber(amount int, decimalPlaces int) string {
	format := fmt.Sprintf("%%.%df", decimalPlaces)

	sign := ""
	if amount < 0 {
		sign = "-"
		amount = -amount
	}

	switch {
	case amount >= 1_000_000_000:
		return fmt.Sprintf(sign+format+"b", float64(amount)/1_000_000_000)
	case amount >= 1_000_000:
		return fmt.Sprintf(sign+format+"m", float64(amount)/1_000_000)
	case amount >= 1_000:
		return fmt.Sprintf(sign+format+"k", float64(amount)/1_000)
	default:
		return sign + strconv.Itoa(amount)
	}
}

func ShowErrorDialog(title, message string) {
	if !isCliMode() {
		dialog := application.MessageDialog{MessageDialogOptions: application.MessageDialogOptions{
			DialogType: application.ErrorDialogType,
			Title:      title,
			Message:    message,
		}}
		dialog.Show()
	}
	panic(message)
}

type ApiResponse struct {
	Success bool   `json:"success"`
	Message string `json:"message"`
}

func MakeAPIRequest(url string, headers map[string]string) (*ApiResponse, error) {
	req := fasthttp.AcquireRequest()
	defer fasthttp.ReleaseRequest(req)

	req.SetRequestURI(url)
	req.Header.SetMethod("GET")

	for k, v := range headers {
		req.Header.Set(k, v)
	}

	resp := fasthttp.AcquireResponse()
	defer fasthttp.ReleaseResponse(resp)

	client := &fasthttp.Client{}
	if err := client.Do(req, resp); err != nil {
		return nil, fmt.Errorf("API request failed: %w", err)
	}

	var apiResponse ApiResponse
	if err := json.Unmarshal(resp.Body(), &apiResponse); err != nil {
		return nil, fmt.Errorf("unmarshaling API response failed: %w", err)
	}

	return &apiResponse, nil
}

type LogLevel string

const (
	Important LogLevel = "important"
	Others    LogLevel = "others"
	Discord   LogLevel = "discord"
)

type LogType string

const (
	Info  LogType = "INF"
	Error LogType = "ERR"
)

func Log(level LogLevel, logType LogType, username string, msg string) {
	EmitEventIfNotCLI(
		"log", level, logType, username, msg)

	switch logType {
	case Info:
		slog.Info(fmt.Sprintf("%s %s %s", level, username, msg))
	case Error:
		slog.Error(fmt.Sprintf("%s %s %s", level, username, msg))
	}
}

func GetConfigPath() string {
	if appImagePath := os.Getenv("APPIMAGE"); appImagePath != "" {
		return filepath.Join(filepath.Dir(appImagePath), "config.json")
	}

	return "./config.json"
}

func ReadConfig() (config.Config, error) {
	configFile := GetConfigPath()

	var cfg config.Config
	bytes, err := os.ReadFile(configFile)
	if err != nil {
		return cfg, err
	}
	err = json.Unmarshal(bytes, &cfg)
	return cfg, err
}

func GetAccountNumber(token string) string {
	cfg, err := ReadConfig()
	if err != nil {
		return "Error: Unable to fetch config"
	}
	for i, account := range cfg.Accounts {
		if account.Token == token {
			return fmt.Sprintf("Account %d", i+1)
		}
	}
	return "Unknown Account"
}

var isCliMode = func() bool { return false }

func SetCliMode(checker func() bool) {
	isCliMode = checker
}

func EmitEventIfNotCLI(eventName string, args ...interface{}) {
	if !isCliMode() {
		application.Get().EmitEvent(eventName, args...)
	}
}
