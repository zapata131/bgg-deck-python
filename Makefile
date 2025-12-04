.PHONY: tailwind-watch run

tailwind-watch:
	npx tailwindcss -i ./app/static/src/input.css -o ./app/static/dist/output.css --watch

run:
	flask run
