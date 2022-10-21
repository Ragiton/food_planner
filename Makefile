SRC_DIR := ./food_planner

all: default

.PHONY: default
default:
	python food_planner/food_planner.py

.PHONY: test
test:

.PHONY: docs
docs: 

.PHONY: install-deps
install-deps: #venv
	pip install -r requirements.txt

# can't automate virtual environment yet
# .PHONY: venv
# venv:
# 	python3 -m venv venv

# .PHONY: activate
# activate: venv
# 	source venv/bin/activate

.PHONY: package
package:

.PHONY: format
format:
	./pants fmt $(SRC_DIR)::

.PHONY: complexity
complexity:

.PHONY: coverage
coverage:

.PHONY: clean
clean:

.PHONY: clean-build
clean-build:
	rm -rf venv

### Help Output ###
.PHONY : help
help :
	@echo "usage: make [OPTIONS] <target>"
	@echo "  Options:"
	@echo "    no options implemented yet"
	@echo "Targets:"
	@echo "  default: Builds all default targets"
	@echo "  test: Build and run unit test programs"
	@echo "  docs: Generate documentation"
	@echo "  package: Build the project, generates docs, and create a release package"
	@echo "  clean: cleans build artifacts, keeping build files in place"
	@echo "  distclean: removes the configured build output directory"
	@echo "  Code Formating:"
	@echo "    format: runs autoformatting on codebase"
	@echo "  Static Analysis:"
	@echo "    complexity: runs complexity analysis"
	@echo "    coverage: runs code coverage analysis and generates an HTML & XML reports"