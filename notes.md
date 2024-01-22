# Deep Tree Compare

Extendable utility tool to compare a folder structure with a reference structure.

## Build Container

```bash
docker build -t leo/medcmp:v1 -f dockerfiles/Dockerfile .
```

## Run Container in Development Mode

Linked

```bash
docker run -it --rm -v $(pwd)/src:/app/src:ro -v $(pwd)/example_data:/app/test --entrypoint bash leo/medcmp:v1
```

Unlinked

```bash
docker run -it --rm -v $(pwd)/example_data:/app/test --entrypoint bash leo/medcmp:v1
```

## Run Container

```bash
export SOURCE_DIR=/home/leonard/Projects/medcmp/example_data/src
export REFERENCE_DIR=/home/leonard/Projects/medcmp/example_data/ref

docker run -t --rm -v $SOURCE_DIR:/app/test/src:ro -v $REFERENCE_DIR:/app/test/ref:ro leo/medcmp:v1
```
