package main

import (
	"bufio"
	"context"
	"embed"
	"flag"
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/utils"
	"github.com/grongor/panicwatch"
	"github.com/wailsapp/wails/v3/pkg/application"
	"github.com/wailsapp/wails/v3/pkg/events"
	"log/slog"
	_ "net/http/pprof"
	"os"
	"strings"
	"sync"
)

//go:embed all:frontend/dist
var assets embed.FS

func init() {
	redirectStderr()
}

func redirectStderr() {
	reader, writer, err := os.Pipe()
	if err != nil {
		slog.Error("Failed to create pipe for stderr redirection", "error", err)
		return
	}

	os.Stderr = writer

	go func() {
		scanner := bufio.NewScanner(reader)
		for scanner.Scan() {
			line := scanner.Text()

			if strings.Contains(line, "Overriding existing handler for signal") ||
				strings.Contains(line, `Failed to load module "appmenu-gtk-module"`) ||
				strings.Contains(line, "SetProcessDpiAwarenessContext failed 0") {
				continue
			}

			slog.Error(line)
		}

		if err := scanner.Err(); err != nil {
			slog.Error("Error reading from stderr pipe", "error", err)
		}
	}()
}

type CustomHandler struct {
	slog.Handler
}

func (h *CustomHandler) Handle(ctx context.Context, r slog.Record) error {
	timeStr := r.Time.Format("3:04PM")
	level := r.Level.String()[:3]
	msg := r.Message

	const (
		reset  = "\033[0m"
		red    = "\033[31m"
		green  = "\033[32m"
		yellow = "\033[33m"
		blue   = "\033[34m"
	)

	var color string
	switch r.Level {
	case slog.LevelDebug:
		color = blue
	case slog.LevelInfo:
		color = green
	case slog.LevelWarn:
		color = yellow
	case slog.LevelError:
		color = red
	default:
		color = reset
	}

	_, err := fmt.Fprintf(os.Stdout, "%s %s%s%s %s\n", timeStr, color, level, reset, msg)
	return err
}

func main() {
	customHandler := &CustomHandler{
		Handler: slog.NewTextHandler(os.Stdout, nil),
	}
	logger := slog.New(customHandler)
	slog.SetDefault(logger)

	dmgService := &DmgService{
		wg:      &sync.WaitGroup{},
		wsMutex: sync.Mutex{},
	}

	err := panicwatch.Start(panicwatch.Config{
		OnPanic: func(p panicwatch.Panic) {
			slog.Error("panic occurred",
				"message", p.Message,
				"stack", p.Stack)
		},
		OnWatcherDied: func(err error) {
			slog.Error("panicwatch watcher process died")
			os.Exit(1)
		},
	})
	if err != nil {
		slog.Error("failed to start panicwatch: " + err.Error())
	}

	cli := flag.Bool("cli", false, "enable CLI mode")
	flag.Parse()

	utils.SetCliMode(func() bool {
		return *cli
	})

	if *cli {
		dmgService.startup()
		var wg sync.WaitGroup
		wg.Add(1)
		wg.Wait()
		return
	}

	app := application.New(application.Options{
		Name: "Dank Memer Grinder",
		Assets: application.AssetOptions{
			Handler:        application.AssetFileServerFS(assets),
			DisableLogging: true,
		},
		Logger:   nil,
		LogLevel: slog.LevelWarn,
		Services: []application.Service{
			application.NewService(dmgService),
		},
		Mac: application.MacOptions{
			ApplicationShouldTerminateAfterLastWindowClosed: true,
		},
		Linux: application.LinuxOptions{
			ProgramName: "Dank Memer Grinder"},
	})

	window := app.NewWebviewWindowWithOptions(application.WebviewWindowOptions{
		Title:         "Dank Memer Grinder",
		Width:         1024,
		Height:        768,
		MinWidth:      1024,
		MinHeight:     768,
		MaxWidth:      1280,
		MaxHeight:     800,
		DisableResize: false,
		Frameless:     false,
	})

	app.OnApplicationEvent(events.Common.ApplicationStarted, func(event *application.ApplicationEvent) {
		dmgService.CheckForUpdates(window)
		dmgService.startup()
	})

	err = app.Run()

	if err != nil {
		utils.ShowErrorDialog("A fatal error occurred!", err.Error())
	}
}
