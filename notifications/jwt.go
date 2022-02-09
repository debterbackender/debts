package main

import (
	"errors"

	"notifications/config"
	"notifications/users"

	"github.com/golang-jwt/jwt"
)

func getSecretKey(t *jwt.Token) (interface{}, error) {
	return []byte(config.SecretKey), nil
}

func GetUserIdFromJWT(accessToken string) (users.UserId, error) {
	claims := jwt.MapClaims{}
	token, err := jwt.ParseWithClaims(accessToken, claims, getSecretKey)
	if err != nil {
		return "", err
	}
	if !token.Valid {
		return "", errors.New("invalid token")
	}
	userId := claims["user_id"].(users.UserId)
	return userId, nil
}
