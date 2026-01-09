.PHONY: flake8 black isort migrate makemigrations showmigrations runserver shell

flake8:
	uv run python -m flake8 . --extend-exclude=dist,build --show-source --statistics

black:
	uv run python -m black $(if $(filter-out $@,$(MAKECMDGOALS)), $(filter-out $@,$(MAKECMDGOALS)), .)

isort:
	uv run python -m isort . --check-only

isort_fix:
	uv run python -m isort $(if $(filter-out $@,$(MAKECMDGOALS)), $(filter-out $@,$(MAKECMDGOALS)), .)

migrate:
	uv run python manage.py migrate

makemigrations:
	uv run python manage.py makemigrations

showmigrations:
	uv run python manage.py showmigrations --settings=mainapps.settings.dev

runserver:
	uv run python manage.py runserver 0.0.0.0:9090

shell:
	uv run python manage.py shell
