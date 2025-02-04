# A phony target is not associated with a file;
# instead, it always executes the associated commands, regardless of whether
# a file with the same name exists in the directory

.PHONY: help

help:
# @ syntax is used to suppress the deafult behavior of make,
# which is to echo the command begin executed to the terminal.
# When you prefix a command with @, the command is executed as usual, but
# it is not printed to the terminal before execution
	@echo "Usage:"
	@echo "  make install PACKAGE=<package-name>   Install a package using pipenv"

.PHONY: install lock

install:
	@pipenv install

install-package:
ifndef PACKAGE
	@echo "Error: Please specify a PACKAGE to install."
	@echo "Example: make install PACKAGE=flask"
	exit 1
else
	@pipenv install $(PACKAGE)
	@echo "Successfully installed $(PACKAGE) with pipenv."
endif

lock:
	@pipenv lock
	@pipenv requirements > requirements.txt

.PHONY: run

run:
	pipenv run python main.py