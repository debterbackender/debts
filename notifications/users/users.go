package users

import (
	"errors"
	"sync"

	"github.com/gorilla/websocket"
)

type UserId = string
var AllConnections = map[UserId](*User){}

type User struct {
	MessageChannel 	chan []byte
	connections 	[]*websocket.Conn
	lock 			*sync.Mutex
}


func (u *User) Send(mt int, message []byte) error {
	u.lock.Lock()
	defer u.lock.Unlock()
	for _, connection := range u.connections {
		if err := connection.WriteMessage(mt, message); err != nil {
			return err
		}
	}
	return nil
}

func (u *User) CloseConnection(removedConn *websocket.Conn) error {
	u.lock.Lock()
	defer u.lock.Unlock()
	for i, connection := range u.connections {
		if removedConn == connection {
			connectionsCount := len(u.connections)
			u.connections[i] = u.connections[connectionsCount-1]
			u.connections = u.connections[:connectionsCount-1]
			return nil
		}
	}
	return errors.New("connection not found")
}

func (u *User) Close() {
	u.lock.Lock()
	defer u.lock.Unlock()
	for _, connection := range u.connections {
		connection.Close()
	}
}

func RegisterConnection(userId UserId, conn *websocket.Conn) *User {
	user, ok := AllConnections[userId]
	if !ok {
		AllConnections[userId] = &User{
			MessageChannel: make(chan []byte),
			connections: []*websocket.Conn{conn},
			lock: &sync.Mutex{},
		}
		return AllConnections[userId]
	} else {
		user.lock.Lock()
		user.connections = append(user.connections, conn)
		user.lock.Unlock()
		return user
	}
}
