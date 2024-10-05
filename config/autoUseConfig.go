package config

type GeneralAutoUseConfig struct {
	State bool `json:"state"`
}

type AutoUseConfig struct {
	Apple          GeneralAutoUseConfig `json:"apple"`
	LuckyHorseshoe GeneralAutoUseConfig `json:"luckyHorseshoe"`
	PizzaSlice     GeneralAutoUseConfig `json:"pizzaSlice"`
}
