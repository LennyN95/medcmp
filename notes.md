# Deep Tree Compare

Extendable utility tool to compare a folder structure with a reference structure.

## Build Container

```bash
cd dockerfiles
docker build -t utils/deeptreecompare .
```

## Run Container

```bash
docker run -it --rm -v $(pwd):/app/utils/deeptreecompare utils/deeptreecompare
```
