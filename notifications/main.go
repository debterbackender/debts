package main

import (
	"log"
	"net/http"

	"notifications/redis"
	"notifications/serializers"
	"notifications/users"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{}
var CONNECTION_CREATED_MESSAGE = []byte("Connection created.")


func RedisHandler() {
	client := redis.CreateRedisClient()
	channel := redis.GetChannel(client)
	for message := range channel {
		events, err := serializers.ParseEvents(message.Payload)
		if err != nil {
			log.Println("Error on parse:", err)
			continue
		}
		for _, event := range events {
			if user, ok := users.AllConnections[event.UserId]; ok {
				user.MessageChannel <- event.Data
			}
		}
	}
}


func UserReadHandler() {

}


func UserWriteHandler(user *users.User) {
	for {
		for message := range user.MessageChannel {
			if err := user.Send(websocket.TextMessage, message); err != nil {
				log.Println("Send Fail:", err)
				break
			}
		}
	}
}

func WebSocketHandler(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("Error on upgrade:", err)
		return
	}
	defer conn.Close()

	mt, message, err := conn.ReadMessage()
	if err != nil {
		log.Println("Error on read access:", err)
		return
	}
	if mt != websocket.TextMessage {
		log.Println("Error: Message is not text")
		return
	}
	jwtToken := string(message)
	userId, err := GetUserIdFromJWT(jwtToken)
	if err != nil {
		log.Println("Error on validating token:", err)
		return
	}

	user := users.RegisterConnection(userId, conn)
	defer user.CloseConnection(conn)

	err = conn.WriteMessage(websocket.TextMessage, CONNECTION_CREATED_MESSAGE)
	if err != nil {
		log.Println("Error on OK:", err)
		return
	}
	for {
		for message := range user.MessageChannel {
			if err := user.Send(websocket.TextMessage, message); err != nil {
				log.Println("Send Fail:", err)
				break
			}
		}
	}
}

func main()  {
	go RedisHandler()

	http.HandleFunc("/ws/", WebSocketHandler)
	http.ListenAndServe(":8082", nil)
}
