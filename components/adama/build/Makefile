.PHONY: clean

all: .build

.build: Dockerfile handler/* serfnode.yml adama-app/.build
	$(MAKE) --directory=adama-app
	docker build -t adama .
	touch .build

clean:
	rm .build
