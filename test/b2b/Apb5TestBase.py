import cocotb
import pyuvm
from pyuvm import uvm_test

from apb5vip import *
from Apb5Env import Apb5Env

# import debugpy
# listen_host, listen_port = debugpy.listen(("localhost", 5679))
# debugpy.wait_for_client()
# breakpoint()


@pyuvm.test()
class Apb5TestBase(uvm_test):

    def __init__(self, name="apb5_test_base", parent=None):
        super().__init__(name, parent)

    def build_phase(self):
        self.env = Apb5Env("apb5_env", self)

    def end_of_elaboration_phase(self):
        self.apb5_requester_seq = Apb5Sequence("apb5_requester_seq")
        self.apb5_completer_seq = Apb5ReactiveSequence("apb5_completer_seq")

    async def run_phase(self):
        self.raise_objection()
        completer_seqr = self.env.completer_agent.sequencer
        cocotb.start_soon(self.apb5_completer_seq.start(completer_seqr))
        self.drop_objection()

    async def wait_cycles(self, cycles):
        await self.env.requester_agent.driver.bfm.wait_cycles(cycles)
