.PHONY: build

build: ui backend

dev: ui backend run-backend

ui:
	./build_frontend.sh

serve-ui:
	cd frontend && bun run dev

backend:
	docker build . -t knowmore

run-backend:
	docker run --env-file .env -p 7000:8000 knowmore