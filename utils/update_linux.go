//go:build linux

package utils

import (
	"fmt"
	"os"
	"os/exec"
	"syscall"
)

func RunUpdater(updaterTempPath string, newBinaryTempPath string) error {
	current := os.Getenv("APPIMAGE")

	if newBinaryTempPath == "" {
		return fmt.Errorf("new binary path is not set, please run DownloadUpdate first")
	}
	if updaterTempPath == "" {
		return fmt.Errorf("updater binary path is not set, please run DownloadUpdate first")
	}

	cmd := exec.Command(updaterTempPath, current, newBinaryTempPath)
	cmd.SysProcAttr = &syscall.SysProcAttr{
		Setsid: true,
	}
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Start(); err != nil {
		return err
	}
	os.Exit(0)
	return nil
}
