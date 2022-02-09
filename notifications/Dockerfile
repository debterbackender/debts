FROM golang:1.17.6-alpine AS build_base

RUN apk add --no-cache git

WORKDIR /tmp/notifications

COPY go.mod .
COPY go.sum .

RUN go mod download

COPY . .

RUN go build -o ./notifications .

FROM alpine:3.9 
RUN apk add ca-certificates

COPY --from=build_base /tmp/notifications/notifications /app/notifications


CMD ["/app/notifications"]
