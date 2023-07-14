install:
	poetry install -T

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install dist/*.whl

lint:
	poetry run flake8 page_analyzer

pytest:
	coverage run -m pytest tests/tests.py

dev:
	poetry run flask --app page_analyzer:app run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

.PHONY: build
build: install

createdb:
	psql -c "CREATE DATABASE page_analyzer;"