package utils

import (
	"math/rand"
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
