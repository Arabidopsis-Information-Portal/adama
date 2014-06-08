# Build 'ruby' image to run Ruby apps

.PHONY: clean

build: Dockerfile ../common *.rb
	docker build --no-cache=$(NO_CACHE) -t ruby .
	touch build
	touch .

clean:
	rm build
