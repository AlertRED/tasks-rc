.PHONY: all
all: setup run
	

.PHONY: setup
setup:
	python3 -m venv venv
	./venv/bin/pip3 install -r ./requirements.txt

.PHONY: run
run:
	./venv/bin/python app/main.py