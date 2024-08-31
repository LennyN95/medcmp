
# variables
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# docker 
docker-build:
	docker build -t $(IMAGE_NAME) .

docker-run:
	docker run -t --rm -v $(SOURCE_DIR):/app/test/src:ro -v $(REFERENCE_DIR):/app/test/ref:ro $(IMAGE_NAME)

# poetry 
poetry-setup:
	poetry env use 3.8
	poetry install

poetry-install:
	poetry install

poetry-run:
	poetry run medcmp $(SOURCE_DIR) $(REFERENCE_DIR)

# test & code quality
test:
	poetry run pytest

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

mypy:
	poetry run mypy .

code-quality: lint format test mypy
