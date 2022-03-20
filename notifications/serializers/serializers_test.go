package serializers

import (
	"bytes"
	"fmt"
	"testing"
)

func TestParseEvents(t *testing.T) {
	var tests = []struct {
		payload string
		events  []Event
	}{
		{
			payload: "[{\"user_id\":\"1\",\"data\":{}}]", 
			events: []Event{
				{
					UserId: "1", 
					Data: []byte("{}"),
				},
			},
		},
		{
			payload: "[{\"user_id\":\"2\",\"data\":{}},{\"user_id\":\"3\",\"data\":{\"some\":20}}]", 
			events: []Event{
				{
					UserId: "2", 
					Data: []byte("{}"),
				},
				{
					UserId: "3", 
					Data: []byte("{\"some\":20}"),
				},
			},
		},
		{
			payload: "[}", 
			events: []Event{},
		},
	}

	for _, tt := range tests {
		t.Run("test", func(t *testing.T) {
			parsedEvents, err := ParseEvents(tt.payload)
			if err != nil {
				fmt.Println(err)
				t.Error("Error on payload", tt.payload)
			}

			for i := 0; i < len(parsedEvents); i++ {
				event := tt.events[i]
				parsedEvent := parsedEvents[i]
				if (event.UserId != parsedEvent.UserId) {
					t.Error("Wrong parsing with UserId: ", event.UserId, parsedEvent.UserId)
				} 
				if !bytes.Equal(event.Data, parsedEvent.Data) {
					t.Errorf("Wrong parsing with Data: \"%s\", \"%s\"", string(event.Data), string(parsedEvent.Data))
				}
			}

		})
	}
}
