build:
	docker-compose build builder

check_compose_override:
	@test -s docker-compose.override.yml || { echo "docker-compose.override.yml não foi encontrado. Você precisa rodar o comando 'make set_env_development' para começar."; exit 1;}

collectstatic:
	docker-compose run web python manage.py collectstatic --noinput

deploy: check_compose_override build restart migrate collectstatic load_fixtures

migrate:
	docker-compose run web python manage.py migrate --noinput

run: check_compose_override
	docker-compose up -d

restart:
	docker-compose stop
	docker-compose up -d

restart_web:
	docker-compose restart web

set_env_development:
	@rm docker-compose.override.yml || true
	ln -s docker-compose.development.yml docker-compose.override.yml
