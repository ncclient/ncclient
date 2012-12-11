make:
	pip install -r requirements.txt
	python setup.py install
clean:
	rm -f -r build/
