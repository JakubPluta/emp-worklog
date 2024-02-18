

pretty:
	black worklog/
	black tests/
	isort worklog/
	isort tests/

lint:
	flake8 worklog/
	flake8 tests/


initsu:
	python -m worklog.scripts.initsu
listusers:
	python -m worklog.scripts.list_users

docker-up:
	docker compose up -d

docker-down:
	docker compose down


dev:
	python -m worklog.server