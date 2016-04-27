help: ## Shows this help
	@echo "$$(grep -h '#\{2\}' $(MAKEFILE_LIST) | sed 's/: #\{2\} /	/' | column -t -s '	')"

install: ## Install requirements
	@[ -n "${VIRTUAL_ENV}" ] || (echo "ERROR: This should be run from a virtualenv" && exit 1)
	pip install -r requirements.txt
	npm install

requirements.txt: ## Regenerate requirements.txt
requirements.txt: requirements.in
	pip-compile $< > $@

test: ## Run test suite
	coverage run -m unittest test_web
	coverage report --show-missing || true

docker/build: ## Build Docker image
	docker build -t crccheck/jinja2-livepreview .

docker/bash: ## Run a shell in the Docker image
	docker run --rm -it -v ${PWD}:/app -p 8080:8080 crccheck/jinja2-livepreview /bin/sh

docker/run: ## Run Docker image
	docker run --rm -v ${PWD}:/app -p 8080:8080 crccheck/jinja2-livepreview

docker/push: ## Publish Docker image to the registry
	docker push crccheck/jinja2-livepreview
