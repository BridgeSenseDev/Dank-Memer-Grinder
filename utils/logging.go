package utils

import (
	"fmt"
	"log/slog"
)

type LogEvent struct {
	Level    LogLevel `json:"level"`
	Type     LogType  `json:"type"`
	Username string   `json:"username"`
	Message  string   `json:"message"`
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
	EmitEventIfNotCLI("log", LogEvent{
		Level:    level,
		Type:     logType,
		Username: username,
		Message:  msg,
	})
	switch logType {
	case Info:
		slog.Info(fmt.Sprintf("%s %s %s", level, username, msg))
	case Error:
		slog.Error(fmt.Sprintf("%s %s %s", level, username, msg))
	}
}
