package utils

import (
	"archive/zip"
	"encoding/json"
	"fmt"
	"github.com/valyala/fasthttp"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
)

var newBinaryTempPath string
var updaterTempPath string

type Change struct {
	Version   string   `json:"version"`
	Changelog []string `json:"changelog"`
}

type VersionResponse struct {
	Version string   `json:"version"`
	Changes []Change `json:"changes"`
}

func CheckForUpdates(currentVersion string) (string, []Change) {
	req := fasthttp.AcquireRequest()
	defer fasthttp.ReleaseRequest(req)
	req.SetRequestURI("https://api.dankmemer.tools/version")
	req.Header.Add("version", currentVersion)

	resp := fasthttp.AcquireResponse()
	defer fasthttp.ReleaseResponse(resp)

	if err := fasthttp.Do(req, resp); err != nil {
		Log(Important, Info, "", fmt.Sprintf("Failed to check for updates: %s", err.Error()))
		return "", nil
	}

	var versionResp VersionResponse
	if err := json.Unmarshal(resp.Body(), &versionResp); err != nil {
		Log(Important, Info, "", fmt.Sprintf("Failed to parse version response: %s", err.Error()))
		return "", nil
	}

	return versionResp.Version, versionResp.Changes
}

type ProgressReader struct {
	reader   io.Reader
	total    int64
	read     int64
	callback func(percentage int)
}

func NewProgressReader(r io.Reader, total int64, callback func(int)) *ProgressReader {
	return &ProgressReader{
		reader:   r,
		total:    total,
		callback: callback,
	}
}

func (pr *ProgressReader) Read(p []byte) (int, error) {
	n, err := pr.reader.Read(p)
	if n > 0 && pr.total > 0 {
		pr.read += int64(n)
		perc := int(float64(pr.read) / float64(pr.total) * 100)
		pr.callback(perc)
	}
	return n, err
}

func extractZip(zipPath, targetDir string) error {
	r, err := zip.OpenReader(zipPath)
	if err != nil {
		return err
	}
	defer func(r *zip.ReadCloser) {
		err := r.Close()
		if err != nil {
			return
		}
	}(r)

	for _, f := range r.File {
		fpath := filepath.Join(targetDir, f.Name)
		if !strings.HasPrefix(fpath, filepath.Clean(targetDir)+string(os.PathSeparator)) {
			return fmt.Errorf("illegal file path: %s", fpath)
		}
		if f.FileInfo().IsDir() {
			if err := os.MkdirAll(fpath, os.ModePerm); err != nil {
				return err
			}
			continue
		}

		if err := os.MkdirAll(filepath.Dir(fpath), os.ModePerm); err != nil {
			return err
		}

		outFile, err := os.OpenFile(fpath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, f.Mode())
		if err != nil {
			return err
		}

		rc, err := f.Open()
		if err != nil {
			cerr := outFile.Close()
			if cerr != nil {
				return cerr
			}
			return err
		}

		_, err = io.Copy(outFile, rc)
		if err != nil {
			return err
		}

		cerr := outFile.Close()
		if cerr != nil {
			return cerr
		}
		cerr = rc.Close()
		if cerr != nil {
			return cerr
		}
	}
	return nil
}

func DownloadUpdate() error {
	osName := runtime.GOOS
	if osName == "darwin" {
		osName = "macos"
	}
	EmitEventIfNotCLI("downloadProgress", 0)

	dmgURL := fmt.Sprintf(
		"https://nightly.link/BridgeSenseDev/Dank-Memer-Grinder/workflows/build/main/DMG-%s.zip",
		osName,
	)

	updaterSuffix := osName
	if osName == "windows" {
		updaterSuffix = "windows.exe"
	}
	updaterURL := fmt.Sprintf(
		"https://github.com/BridgeSenseDev/Dank-Memer-Grinder/raw/refs/heads/main/build/updater-%s",
		updaterSuffix,
	)

	resp, err := http.Get(dmgURL)
	if err != nil {
		return err
	}
	if resp.StatusCode != http.StatusOK {
		cerr := resp.Body.Close()
		if cerr != nil {
			return cerr
		}
		return fmt.Errorf("failed to download DMG: %s", resp.Status)
	}
	totalSize, err := strconv.Atoi(resp.Header.Get("Content-Length"))
	if err != nil {
		totalSize = 0
	}
	progressReader := NewProgressReader(resp.Body, int64(totalSize), func(perc int) {
		EmitEventIfNotCLI("downloadProgress", perc)
	})

	tempZip, err := os.CreateTemp("", "dmg-update-*.zip")
	if err != nil {
		cerr := resp.Body.Close()
		if cerr != nil {
			return cerr
		}
		return err
	}
	zipFileName := tempZip.Name()
	_, err = io.Copy(tempZip, progressReader)
	if err != nil {
		cerr := tempZip.Close()
		if cerr != nil {
			err = resp.Body.Close()
			if err != nil {
				return err
			}
			return cerr
		}
		rerr := os.Remove(zipFileName)
		if rerr != nil {
			err = resp.Body.Close()
			if err != nil {
				return err
			}
			return rerr
		}
		cerr = resp.Body.Close()
		if cerr != nil {
			return cerr
		}
		return err
	}
	if err := tempZip.Close(); err != nil {
		cerr := resp.Body.Close()
		if cerr != nil {
			return cerr
		}
		return err
	}
	if err := resp.Body.Close(); err != nil {
		return err
	}

	targetDir, err := os.MkdirTemp("", "dmg-update-extract-*")
	if err != nil {
		return err
	}
	defer func(path string) {
		err := os.RemoveAll(path)
		if err != nil {
			return
		}
	}(targetDir)

	if err := extractZip(zipFileName, targetDir); err != nil {
		return err
	}
	if err := os.Remove(zipFileName); err != nil {
		return err
	}

	entries, err := os.ReadDir(targetDir)
	if err != nil {
		return err
	}
	var extractedFile string
	for _, entry := range entries {
		if !entry.IsDir() {
			extractedFile = entry.Name()
			break
		}
	}
	if extractedFile == "" {
		return fmt.Errorf("no file extracted from zip")
	}
	oldPath := filepath.Join(targetDir, extractedFile)

	tempDirForBinary, err := os.MkdirTemp("", "dmg-update-binary-*")
	if err != nil {
		return err
	}
	newBinaryTempPath = filepath.Join(tempDirForBinary, "updated-"+extractedFile)
	if err := os.Rename(oldPath, newBinaryTempPath); err != nil {
		return err
	}

	respUpdater, err := http.Get(updaterURL)
	if err != nil {
		return err
	}
	if respUpdater.StatusCode != http.StatusOK {
		cerr := respUpdater.Body.Close()
		if cerr != nil {
			return cerr
		}
		return fmt.Errorf("failed to download updater: %s", respUpdater.Status)
	}
	ext := filepath.Ext(updaterURL)
	updaterName := "updated-updater" + ext
	tempDirForUpdater, err := os.MkdirTemp("", "dmg-update-updater-*")
	if err != nil {
		return err
	}
	updaterTempPath = filepath.Join(tempDirForUpdater, updaterName)
	updaterFile, err := os.Create(updaterTempPath)
	if err != nil {
		cerr := respUpdater.Body.Close()
		if cerr != nil {
			return cerr
		}
		return err
	}
	if _, err := io.Copy(updaterFile, respUpdater.Body); err != nil {
		cerr := updaterFile.Close()
		if cerr != nil {
			err = respUpdater.Body.Close()
			if err != nil {
				return err
			}
			return cerr
		}
		cerr = respUpdater.Body.Close()
		if cerr != nil {
			return cerr
		}
		return err
	}
	if err := updaterFile.Close(); err != nil {
		cerr := respUpdater.Body.Close()
		if cerr != nil {
			return cerr
		}
		return err
	}
	if err := respUpdater.Body.Close(); err != nil {
		return err
	}
	if err := os.Chmod(updaterTempPath, 0755); err != nil {
		return err
	}

	EmitEventIfNotCLI("downloadProgress", 100)
	return RunUpdater(updaterTempPath, newBinaryTempPath)
}
