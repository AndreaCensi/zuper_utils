
coverage_include='*src/zuper_*'
coveralls_repo_token=5eha7C63Y0403x9LRaGscdqQet7yC3WoR

cover_packages=zuper_typing,zuper_typing_tests,zuper_ipce,zuper_ipce_tests

parallel=--processes=8 --process-timeout=1000 --process-restartworker
coverage=--cover-html --cover-tests --with-coverage --cover-package=$(cover_packages)

xunitmp=--with-xunitmp --xunitmp-file=test-results/nose-$(CIRCLE_NODE_INDEX)-xunit.xml
extra=--rednose --immediate

all: test



test:
	rm -f .coverage
	rm -rf cover
	nosetests $(extra) $(coverage) $(xunitmp) src  -v

test-parallel:
	rm -f .coverage
	rm -rf cover
	nosetests $(extra) $(coverage) src  -v  $(parallel)

test-parallel-failed:
	rm -f .coverage
	rm -rf cover
	nosetests  $(extra)  $(coverage) src  -v  $(parallel)

test-parallel-circle:
	NODE_TOTAL=$(CIRCLE_NODE_TOTAL) NODE_INDEX=$(CIRCLE_NODE_INDEX) nosetests $(coverage) $(xunitmp) src  -v  $(parallel)
# 2>&1 | grep -v module-not-measured

test-failed:
	rm -f .coverage
	rm -rf cover
	nosetests $(extra)  --with-id --failed $(coverage) src  -v




docker-36-build:
	docker build -f Dockerfile.python3.6 -t python36 .

docker-36-test:  docker-36-build
	docker run -it -v $(PWD)/src/zuper_json:/project/src/zuper_json -w /project python36 make all

docker-36-shell:
	docker run -it   python36 /bin/bash


docker-37-build:
	docker build -f Dockerfile.python3.7 -t python37 .

docker-37-test: docker-37-build
	docker run -it -v $(PWD)/src/zuper_json:/project/src/zuper_json -w /project python37 make all

docker-37-shell:
	docker run -it   python37 /bin/bash


bump-upload:
	$(MAKE) bump
	$(MAKE) upload

bump:
	bumpversion patch

upload:
	git push --tags
	git push
	rm -f dist/*
	python setup.py sdist
	twine upload dist/*


out=out-comptests
coverage_dir=out-coverage
coverage_run=coverage run

tests-clean:
	rm -rf $(out) $(coverage_dir) .coverage .coverage.*



autogen:
	python3 -m zuper_ipce_tests.test_from_testobjs > src/zuper_ipce_tests/test_z_from_testobjs_autogenerated.py


