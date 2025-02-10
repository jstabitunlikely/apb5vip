CWD=$(shell pwd)
export COCOTB_REDUCED_LOG_FMT = 1
SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES = $(CWD)/b2b_tb.sv
# MODULE := "$(patsubst %.py,%,$(wildcard Apb5Test*.py))"
MODULE := "Apb5TestBase, Apb5TestSimple"
TOPLEVEL ?= b2b_tb
# SIM_CMD_SUFFIX := 2>&1 | tee cocotb.log
# SIM_ARGS := -l icarus.log
COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps
# REVISIT doesn't seem to work
# WAVES := 1
include $(shell cocotb-config --makefiles)/Makefile.sim
