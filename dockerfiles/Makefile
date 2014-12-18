
COMPONENTS=\
	minion \
	zookeeper \
	rabbitmq \
	registry

.PHONY: build

build:
	@set -e; for component in $(COMPONENTS); \
	do \
		$(MAKE) --directory=$$component; \
	done

