package config

type GeneralAutoUseConfig struct {
	State bool `json:"state"`
}

type AutoUseConfig struct {
	Apple      GeneralAutoUseConfig `json:"apple"`
	PizzaSlice GeneralAutoUseConfig `json:"pizzaSlice"`
}
