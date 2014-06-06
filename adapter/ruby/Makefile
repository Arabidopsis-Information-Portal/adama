# Build 'ruby' image to run Ruby apps

.PHONY: clean

build: Dockerfile ../common *.rb
	docker build -t ruby .
	touch build
	touch .

clean:
	rm build
