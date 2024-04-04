package config

type GeneralAutobuyConfig struct {
	State  bool `json:"state"`
	Amount int  `json:"amount"`
}

type AutoBuyConfig struct {
	HuntingRifle GeneralAutobuyConfig `json:"huntingRifle"`
	Shovel       GeneralAutobuyConfig `json:"shovel"`
	LifeSavers   GeneralAutobuyConfig `json:"lifeSavers"`
}
