all: default

clean: clean-output clean-test

clean-output: 

clean-test: 

deps:
	pip install -r requirements.txt

dev_deps:
	pip install -r requirements-dev.txt

check-format: dev_deps
	yapf -rd pulpo-beanstalk-cli

format: dev_deps
	yapf -ri pulpo-beanstalk-cli

lint: check-format
	pylint -r n pulpo-beanstalk-cli

lint-no-error: 
	pylint --exit-zero -r n pulpo-beanstalk-cli

test: build dev_deps
	python3 -m pytest -v --durations=0 --cov=pulpo-beanstalk-cli --cov-report html

build: deps
	# might re-add clean 
