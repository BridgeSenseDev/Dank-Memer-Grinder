//go:build linux

package utils

import (
	"os"
	"os/exec"
	"syscall"
)

func RunUpdater(updaterTempPath string, newBinaryTempPath string) error {
	current := os.Getenv("APPIMAGE")

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
