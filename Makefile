css:
	bun tailwindcss -i ./static/src/input.css -o ./static/src/output.css --watch

bundle-css:
	bun tailwindcss -i ./static/src/input.css -o ./static/src/output.css --minify