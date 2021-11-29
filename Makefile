VENV ?= venv
REQUIREMENTS ?= requeriments-dev.txt

init: clean init-venv

init-venv: clean-venv create-venv update-venv
	@echo ""
	@echo "Do not forget to activate your new virtual environment"

create-venv:
	@echo "Creating virtual environment: $(VENV)..."
	@python3 -m venv $(VENV)

update-venv:
	@echo "Updating virtual environment: $(VENV)..."
	@( \
		. $(VENV)/bin/activate; \
		pip install --upgrade pip; \
		pip install -r $(REQUIREMENTS) \
	)

clean: clean-venv

clean-venv:
	@echo "Removing virtual environment: $(VENV)..."
	@rm -rf $(VENV)

service-run:
	@echo "Starting server..."
	@uvicorn app.main:app --reload
