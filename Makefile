run:
	uvicorn app:app --reload

test:
	pytest test_*.py

startpg:
	docker run --name pg-docker --rm -p 5400:5432 -e POSTGRES_PASSWORD=docker -e POSTGRES_USER=docker -d postgres

stoppg:
	docker stop pg-docker
