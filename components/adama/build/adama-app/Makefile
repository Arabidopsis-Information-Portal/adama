.PHONY: clean

all: .build

.build: Dockerfile adama-package/*
	docker build -t adama_app .
	touch .build

clean:
	rm .build
