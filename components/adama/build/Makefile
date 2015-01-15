.PHONY: clean

all: .build

.build: Dockerfile handler/*
	docker build -t adama .
	touch .build

clean:
	rm .build
