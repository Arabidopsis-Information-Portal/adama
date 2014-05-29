# Build 'python' image to run Python apps

.PHONY: clean

build: Dockerfile ../common
	docker build -t python .
	touch build
	touch .

clean:
	rm build
