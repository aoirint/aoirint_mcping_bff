# aoirint_mcping_bff

## Library management

This repository uses [Poetry](https://github.com/python-poetry/poetry).

To dump `requirements*.txt`,

```shell
poetry export --without-hashes -o requirements.txt
poetry export --without-hashes --with dev -o requirements-dev.txt
```
