package main

import (
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"time"
)

func copyFile(src, dst string) error {
	in, err := os.Open(src)
	if err != nil {
		return err
	}
	defer func(in *os.File) {
		err := in.Close()
		if err != nil {
			return
		}
	}(in)

	srcInfo, err := os.Stat(src)
	if err != nil {
		return err
	}

	out, err := os.OpenFile(dst, os.O_CREATE|os.O_WRONLY, srcInfo.Mode())
	if err != nil {
		return err
	}
	defer func(out *os.File) {
		err := out.Close()
		if err != nil {
			return
		}
	}(out)

	if _, err = io.Copy(out, in); err != nil {
		return err
	}

	return out.Sync()
}

func main() {
	if len(os.Args) < 3 {
		fmt.Println("Usage: updater <currentBinary> <newBinary>")
		os.Exit(1)
	}

	currentBinary := os.Args[1]
	newBinary := os.Args[2]

	time.Sleep(2 * time.Second)

	if err := os.Remove(currentBinary); err != nil {
		fmt.Printf("Failed to remove old binary: %v\n", err)
		os.Exit(1)
	}

	if err := copyFile(newBinary, currentBinary); err != nil {
		fmt.Printf("Failed to copy new binary: %v\n", err)
		os.Exit(1)
	}

	if err := os.Remove(newBinary); err != nil {
		fmt.Printf("Warning: unable to remove temporary updated binary: %v\n", err)
	}

	absPath, err := filepath.Abs(currentBinary)
	if err != nil {
		fmt.Printf("Failed to get absolute path for binary: %v\n", err)
		os.Exit(1)
	}

	cmd := exec.Command(absPath)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Start(); err != nil {
		fmt.Printf("Failed to start new binary: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("Update complete. Relaunched new process.")
	os.Exit(0)
}
