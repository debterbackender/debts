package redis

import (
	"context"
	"notifications/config"

	"github.com/go-redis/redis/v8"
)

var ctx = context.Background()

func CreateRedisClient() *redis.Client {
	opt, err := redis.ParseURL(config.RedisUrl)
	if err != nil {
		panic(err)
	}

	redisClient := redis.NewClient(opt)
	if err := redisClient.Ping(ctx).Err(); err != nil {
		panic(err)
	}
	return redisClient
}

func GetChannel(redisClient *redis.Client) <- chan *redis.Message {
	topic := redisClient.Subscribe(ctx, "events")
	channel := topic.Channel()

	return channel
}
