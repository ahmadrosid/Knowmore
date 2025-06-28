.PHONY: build

build: ui backend

ui:
	python3 build_frontend.py

serve-ui:
	cd frontend && bun run dev

backend:
	docker build . -t knowmore
	docker run --env-file .env -p 7000:8000 knowmore
