.PHONY: clean

all: .build

.build: Dockerfile handler/*
	docker build -t serf-redis .
	touch .build

clean:
	rm .build
