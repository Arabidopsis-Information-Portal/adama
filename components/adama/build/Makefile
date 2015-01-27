.PHONY: clean

all: .build

.build: Dockerfile handler/* serfnode.yml
	docker build -t adama .
	touch .build

clean:
	rm .build
