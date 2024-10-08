package utils

import (
	"encoding/json"
	"fmt"
	"github.com/valyala/fasthttp"
	"math/rand"
	"strconv"
	"strings"
	"time"
)

var src = rand.NewSource(time.Now().UnixNano())
var Rng = rand.New(src)

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

func ExponentialBackoff(attempt int) time.Duration {
	if attempt == 0 {
		return time.Second
	} else if attempt < 5 {
		return time.Duration(2<<uint(attempt-1)) * time.Second
	} else {
		return 30 * time.Second
	}
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

	var version string = "128.0.0.0"

	if err := fasthttp.Do(req, resp); err == nil {
		var data browserVersionResponse
		if err := json.Unmarshal(resp.Body(), &data); err == nil {
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
