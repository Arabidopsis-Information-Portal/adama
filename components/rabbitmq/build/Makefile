.PHONY: clean

all: .build

.build: Dockerfile handler/*
	docker build -t rabbitmq .
	touch .build

clean:
	rm .build
