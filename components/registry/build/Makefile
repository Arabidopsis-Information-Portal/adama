.PHONY: clean

all: .build

.build: Dockerfile handler/*
	docker build -t serf-registry .
	touch .build

clean:
	rm .build

