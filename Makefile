.PHONY: test suite demo zipapp dashboard verify

test:
	PYTHONPATH=src python -m unittest discover -s tests -v

suite:
	PYTHONPATH=src python -m qingyuan_os suite --examples examples --output outputs/reference

demo:
	PYTHONPATH=src python -m qingyuan_os demo --output outputs/demo

zipapp:
	python scripts/build_zipapp.py

dashboard:
	python scripts/build_offline_dashboard.py

verify:
	PYTHONPATH=src python scripts/verify_release.py
