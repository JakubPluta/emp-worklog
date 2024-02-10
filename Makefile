

pretty:
	black worklog/
	black tests/
	isort worklog/
	isort tests/

lint:
	flake8 worklog/
	flake8 tests/