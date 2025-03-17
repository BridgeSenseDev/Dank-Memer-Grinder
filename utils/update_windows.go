//go:build windows

package utils

func RunUpdater(updaterTempPath string, newBinaryTempPath string) error {
	current, err = os.Executable()
	if err != nil {
		return err
	}

	if newBinaryTempPath == "" {
		return fmt.Errorf("new binary path is not set, please run DownloadUpdate first")
	}
	if updaterTempPath == "" {
		return fmt.Errorf("updater binary path is not set, please run DownloadUpdate first")
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
