//go:build windows

package utils

import (
	"os"
	"os/exec"
	"syscall"
)

func RunUpdater(updaterTempPath string, newBinaryTempPath string) error {
	current, err := os.Executable()
	if err != nil {
		return err
	}

	cmd := exec.Command("cmd.exe", "/C", "start", "", "/B", updaterTempPath, current, newBinaryTempPath)
	cmd.SysProcAttr = &syscall.SysProcAttr{
		HideWindow: true,
	}
	if err := cmd.Start(); err != nil {
		return err
	}
	os.Exit(0)

	return nil
}
