package commands

import (
    "fmt"
    "time"
    // ... other imports
)

func (c *Commands) ServerEvents() error {
    if !c.cfg.Commands.ServerEvents.State {
        return nil
    }
    
    // Get wallet balance
    balance := c.getWalletBalance()
    
    // Check if balance > minimum
    if balance <= c.cfg.Commands.ServerEvents.MinimumWalletBalance {
        return nil
    }
    
    // Calculate donation amount
    donateAmount := balance - c.cfg.Commands.ServerEvents.MinimumWalletBalance
    
    // Send command
    err := c.sendCommand(fmt.Sprintf("/serverevents donate quantity:%d", donateAmount))
    if err != nil {
        return err
    }
    
    // Wait for confirmation embed and click confirm
    if c.cfg.Commands.ServerEvents.AutoConfirm {
        time.Sleep(randomDelay(c.cfg.Commands.ServerEvents.ConfirmDelay))
        err = c.clickButton("Confirm")
    }
    
    return err
}
