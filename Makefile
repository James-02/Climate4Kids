SHELL=/bin/bash
CONFIG = .env

all: install

.PHONY: install run clean db env cleanall

venv: 
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt

env: 
	touch $(CONFIG)
	@printf "SECRET_KEY='your_secret_key'\n\
	SQLALCHEMY_DATABASE_URI='sqlite:///sqlite.db'\n\
	SMTP_EMAIL='your_email'\n\
	SMTP_PASSWORD='your_email_password'" > $(CONFIG)

install: venv env db
	@echo "----------------------------------------------------------"
	@echo "Install completed, please update .env before running\n"

db:
	touch sqlite.db
	venv/bin/python3 models.py

run:
	venv/bin/python3 app.py

clean:
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '.pytest_cache' -type d | xargs rm -rf
	find . -name '__pycache__' -type d | xargs rm -rf

cleanall: clean
	rm -rf venv
	rm -f .env
	rm -f sqlite.db