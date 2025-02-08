CWD=$(shell pwd)
export COCOTB_REDUCED_LOG_FMT = 1
SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES = $(CWD)/b2b_tb.sv
MODULE := Apb5TestBase
TOP_LEVEL ?= b2b_tb
GHDL_ARGS := --ieee=synopsys
COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps
include $(shell cocotb-config --makefiles)/Makefile.sim
# include ../../checkclean.mk
