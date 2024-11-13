run:
	uvicorn app:app --reload

test:
	pytest tests --ignore=tests/test_dispatcher_with_postgres.py 

test_pg_e2e:
	./run_postgres_e2e.sh

test_all: test test_pg_e2e

startpg:
	docker run --name pg-docker --rm -p 5400:5432 -e POSTGRES_PASSWORD=docker -e POSTGRES_USER=docker -d postgres

stoppg:
	docker stop pg-docker
