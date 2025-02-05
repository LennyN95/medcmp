
# --- variables
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# --- container / docker 
docker-build:
	docker build -t $(IMAGE_NAME) .

docker-run:
	docker run -t --rm -v $(SOURCE_DIR):/app/test/src:ro -v $(REFERENCE_DIR):/app/test/ref:ro $(IMAGE_NAME)

# --- local / uv 
uv-setup:
	uv venv -p 3.11
	uv sync

uv-install:
	uv sync

uv-run:
	uv run medcmp $(SOURCE_DIR) $(REFERENCE_DIR) $(REPORT_FILE)

# --- test & code quality
test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

mypy:
	uv run mypy .

code-quality: lint format test mypy
