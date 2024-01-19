# Deep Tree Compare

Extendable utility tool to compare a folder structure with a reference structure.

## Build Container

```bash
docker build -t leo/medcmp:v1 -f dockerfiles/Dockerfile .
```

## Run Container in Development Mode

```bash
docker run -it --rm -v $(pwd)/src:/app/src:ro -v $(pwd)/example_data:/app/test --entrypoint bash leo/medcmp:v1
```

## Run Container

```bash
docker run -it --rm leo/medcmp:v1
```
