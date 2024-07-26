run:
	uvicorn app:app --reload

test:
	pytest test_*.py
