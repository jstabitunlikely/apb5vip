.PHONY: run_b2b_tb
run_b2b_tb:
	make -C test/b2b SIM=icarus

.PHONY: init
init:
	pip install -r requirements.txt
	# pip install -e .

.PHONY: lint
lint:
	@pylint apb5vip

.PHONY: test
test:
	pytest
