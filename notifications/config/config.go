package config

import "os"


func getEnv(key, fallback string) string {
    if value, ok := os.LookupEnv(key); ok {
        return value
    }
    return fallback
}

var SecretKey = getEnv("SECRET_KEY", "django-insecure-@dq58qc12(x=tipmduc%hva_ogn^)th_xpz=r&%4hixcw+%_^3")
var RedisUrl = getEnv("REDIS_URL", "redis://localhost:6364/0")
