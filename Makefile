clean:
	find . -name "*.pyc" -exec rm -rf {} \;
	find . -name "*.log" -exec rm -rf {} \;

deps:
	pip install -r requirements.txt

run:
	python executor.py