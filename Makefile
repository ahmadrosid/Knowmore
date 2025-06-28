.PHONY: build

build: ui backend

dev: ui backend run-backend

ui:
	./build_ui.sh

serve-ui:
	cd ui && bun run dev

backend:
	docker build . -t knowmore

run-backend:
	docker run --env-file .env -p 7000:8000 knowmore