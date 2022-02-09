package serializers

import "encoding/json"

type Event struct {
	UserId	string         	`json:"user_id"`
	Data   	json.RawMessage	`json:"data"`
}


func ParseEvents(payload string) ([]Event, error) {
	var events []Event
	err := json.Unmarshal([]byte(payload), &events)
	if err != nil {
		return nil, err
	}
	return events, nil
}
