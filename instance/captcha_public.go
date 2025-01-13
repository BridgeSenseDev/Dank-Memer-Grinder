//go:build public

package instance

import "github.com/BridgeSenseDev/Dank-Memer-Grinder/gateway"

func (in *Instance) Captcha(message gateway.EventMessage) bool {
	// Public stub implementation
	return false
}
