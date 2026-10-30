.PHONY: test example

test:
	python3 -m unittest discover -s tests -v

example:
	python3 tools/audit_csv.py examples/applications.csv --required id,date,people --unique id || true

