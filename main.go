package main

import (
	"embed"
	"github.com/grongor/panicwatch"
	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
	"github.com/wailsapp/wails/v3/pkg/application"
	"github.com/wailsapp/wails/v3/pkg/events"
	_ "net/http/pprof"
	"os"
	"sync"
)

//go:embed all:frontend/dist
var assets embed.FS

func main() {
	log.Logger = log.Output(zerolog.ConsoleWriter{Out: os.Stderr})

	dmgService := &DmgService{
		wg:      &sync.WaitGroup{},
		wsMutex: sync.Mutex{},
	}

	err := panicwatch.Start(panicwatch.Config{
		OnPanic: func(p panicwatch.Panic) {
			log.Error().Msgf("panic: %s, stack: %s", p.Message, p.Stack)
		},
		OnWatcherDied: func(err error) {
			log.Fatal().Msg("panicwatch watcher process died")
		},
	})
	if err != nil {
		log.Fatal().Msgf("failed to start panicwatch: " + err.Error())
	}

	app := application.New(application.Options{
		Name: "Dank Memer Grinder",
		Assets: application.AssetOptions{
			Handler: application.AssetFileServerFS(assets),
		},
		Logger: nil,
		Services: []application.Service{
			application.NewService(dmgService),
		},
		Mac: application.MacOptions{
			ApplicationShouldTerminateAfterLastWindowClosed: true,
		},
		Linux: application.LinuxOptions{
			ProgramName: "Dank Memer Grinder"},
	})

	app.NewWebviewWindowWithOptions(application.WebviewWindowOptions{
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
		dmgService.startup()
	})

	err = app.Run()

	if err != nil {
		//runtime.MessageDialog(app.ctx, runtime.MessageDialogOptions{
		//	Type:    runtime.ErrorDialog,
		//	Title:   "A fatal error occurred!",
		//	Message: err.Error(),
		//})
		panic(err.Error())
	}
}
