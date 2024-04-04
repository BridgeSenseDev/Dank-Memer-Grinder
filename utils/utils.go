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
	var max = -2
	var maxIndices []int

	for i, priority := range buttonPriority {
		if priority > max {
			max = priority
			maxIndices = []int{i}
		} else if priority == max {
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
