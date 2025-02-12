import cocotb
import pyuvm
from pyuvm import uvm_test, ConfigDB

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

    def connect_cocotb_to_vif(self, requester_if: Apb5Interface):
        assert cocotb.top is not None
        requester_if.ADDR_WIDTH = cocotb.top.ADDR_WIDTH
        requester_if.DATA_WIDTH = cocotb.top.DATA_WIDTH
        requester_if.RME_SUPPORT = cocotb.top.RME_SUPPORT
        requester_if.WAKEUP_SUPPORT = cocotb.top.WAKEUP_SUPPORT
        requester_if.USER_REQ_WIDTH = cocotb.top.USER_REQ_WIDTH
        requester_if.USER_DATA_WIDTH = cocotb.top.USER_DATA_WIDTH
        requester_if.USER_RESP_WIDTH = cocotb.top.USER_RESP_WIDTH
        requester_if.pwakeup = cocotb.top.PWAKEUP
        requester_if.psel = cocotb.top.PSEL
        requester_if.penable = cocotb.top.PENABLE
        requester_if.paddr = cocotb.top.PADDR
        requester_if.pwrite = cocotb.top.PWRITE
        requester_if.pwdata = cocotb.top.PWDATA
        requester_if.pstrb = cocotb.top.PSTRB
        requester_if.pprot = cocotb.top.PPROT
        requester_if.pnse = cocotb.top.PNSE
        requester_if.prdata = cocotb.top.PRDATA
        requester_if.pslverr = cocotb.top.PSLVERR
        requester_if.pready = cocotb.top.PREADY
        requester_if.pauser = cocotb.top.PAUSER
        requester_if.pwuser = cocotb.top.PWUSER
        requester_if.pruser = cocotb.top.PRUSER
        requester_if.pbuser = cocotb.top.PBUSER


    def build_phase(self):
        assert cocotb.top is not None

        self.requester_if = Apb5RequesterInterface(cocotb.top.PCLK, cocotb.top.PRESETN)
        self.connect_cocotb_to_vif(self.requester_if)
        ConfigDB().set(self, "*requester_agent*", "vif", self.requester_if)

        self.completer_if = Apb5CompleterInterface(cocotb.top.PCLK, cocotb.top.PRESETN)
        self.connect_cocotb_to_vif(self.completer_if)
        ConfigDB().set(self, "*completer_agent*", "vif", self.completer_if)
        # TODO use a third, passive agent to collect coverage
        ConfigDB().set(self, "*completer_agent*", "has_coverage", True)

        self.env = Apb5Env("apb5_env", self)

    def end_of_elaboration_phase(self):
        self.apb5_completer_seq = Apb5ReactiveSequence("apb5_completer_seq")

    async def run_phase(self):
        self.raise_objection()
        completer_seqr = self.env.completer_agent.sequencer
        cocotb.start_soon(self.apb5_completer_seq.start(completer_seqr))
        self.drop_objection()

    async def wait_cycles(self, cycles):
        await self.env.requester_agent.driver.bfm.wait_cycles(cycles)
