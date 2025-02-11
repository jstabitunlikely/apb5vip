# AMBA APB5 VIP

This is an attempt to implement a simple Verification IP using PyUVM.

## Back-to-back test bench

There is an integration test bench included, which uses a dummy RTL module to connect a Requester and a Completer
instance of the VIP.

### Prerequisites

A simulator e.g., Icarus Verilog needs to be available in your system. Since PyUVM is using cocotb, any simulator
supported by cocotb should work. That being said, the codebase was tested with Icarus + GTKWave only.

### Installing the VIP

The package is not yet uploaded to PyPi, install it locally.
```
pip install .
```

Consider making it editable in case you want to play around the codebase.
```
pip install -e .
```

This should take care of any dependencies as well. Using a virtual environment is recommended.

### Running tests

The test(s) can be run by using the following make target.
```
make run_b2b_tb
```

# Resources
- [AMBA APB5 Specification](https://developer.arm.com/documentation/ihi0024/e/)
- [PyUVM documentation](https://pyuvm.github.io/pyuvm/)
- [Cocotb documentation](https://docs.cocotb.org/en/stable/)
- [Icarus Verilog documentation](https://steveicarus.github.io/iverilog/index.html)

# Disclaimer

This project serves as a learning exercise with PyUVM.  The goal was to get hands-on experience with the library, rather than building a complete VIP.