# Master makefile to build all containers

CONTAINERS=common \
	python \
	ruby

.PHONY: build
build:
	@set -e; for container in $(CONTAINERS); \
	do \
		echo "========================"; \
		echo "Building: $$container"; \
		echo "========================"; \
		$(MAKE) --directory=$$container; \
	done
