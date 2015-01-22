.PHONY: clean

all: .build

.build: Dockerfile handler/* adama-package/*
	docker build -t adama .
	touch .build

clean:
	rm .build
