.PHONY: docs test

docs:
	uv run --group docs sphinx-build -b html docs docs/_build/html

test:
	uv run pytest test_pytheory.py -v
