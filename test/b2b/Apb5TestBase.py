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

    def connect_cocotb_to_vif(self, requester_if: Apb5Interface):
        assert cocotb.top is not None
        requester_if.ADDR_WIDTH = int(cocotb.top.ADDR_WIDTH.value)
        requester_if.DATA_WIDTH = int(cocotb.top.DATA_WIDTH.value)
        requester_if.RME_SUPPORT = int(cocotb.top.RME_SUPPORT.value)
        requester_if.WAKEUP_SUPPORT = int(cocotb.top.WAKEUP_SUPPORT.value)
        requester_if.USER_REQ_WIDTH = int(cocotb.top.USER_REQ_WIDTH.value)
        requester_if.USER_DATA_WIDTH = int(cocotb.top.USER_DATA_WIDTH.value)
        requester_if.USER_RESP_WIDTH = int(cocotb.top.USER_RESP_WIDTH.value)
        if requester_if.WAKEUP_SUPPORT:
            requester_if.pwakeup = cocotb.top.PWAKEUP
        requester_if.psel = cocotb.top.PSEL
        requester_if.penable = cocotb.top.PENABLE
        requester_if.paddr = cocotb.top.PADDR
        requester_if.pwrite = cocotb.top.PWRITE
        requester_if.pwdata = cocotb.top.PWDATA
        requester_if.pstrb = cocotb.top.PSTRB
        requester_if.pprot = cocotb.top.PPROT
        if requester_if.RME_SUPPORT:
            requester_if.pnse = cocotb.top.PNSE
        requester_if.prdata = cocotb.top.PRDATA
        requester_if.pslverr = cocotb.top.PSLVERR
        requester_if.pready = cocotb.top.PREADY
        if requester_if.USER_REQ_WIDTH:
            requester_if.pauser = cocotb.top.PAUSER
        if requester_if.USER_DATA_WIDTH:
            requester_if.pwuser = cocotb.top.PWUSER
            requester_if.pruser = cocotb.top.PRUSER
        if requester_if.USER_RESP_WIDTH:
            requester_if.pbuser = cocotb.top.PBUSER

    def build_phase(self):
        assert cocotb.top is not None

        # APB5 Requester agent (active)
        self.requester_if = Apb5RequesterInterface(cocotb.top.PCLK, cocotb.top.PRESETN)
        self.connect_cocotb_to_vif(self.requester_if)
        self.cdb_set(label="vif", value=self.requester_if, inst_path="env.requester_agent*")
        self.cdb_set(label="vif", value=self.requester_if, inst_path="env*")

        # APB5 Completer agent (reactive)
        self.completer_if = Apb5CompleterInterface(cocotb.top.PCLK, cocotb.top.PRESETN)
        self.connect_cocotb_to_vif(self.completer_if)
        self.cdb_set(label="vif", value=self.completer_if, inst_path="env.completer_agent*")

        # APB5 Completer agent (passive with coverage)
        self.completer_cov_if = Apb5CompleterInterface(cocotb.top.PCLK, cocotb.top.PRESETN)
        self.connect_cocotb_to_vif(self.completer_cov_if)
        self.cdb_set(label="vif", value=self.completer_cov_if, inst_path="env.completer_agent_cov*")

        # Create the environment
        self.env = Apb5Env("env", self)

    def end_of_elaboration_phase(self):
        self.apb5_completer_seq = Apb5ReactiveSequence("apb5_completer_seq")

    async def run_phase(self):
        self.raise_objection()
        completer_seqr = self.env.completer_agent.sequencer
        cocotb.start_soon(self.apb5_completer_seq.start(completer_seqr))
        self.drop_objection()

    async def wait_cycles(self, cycles):
        await self.env.requester_agent.driver.bfm.wait_cycles(cycles)
