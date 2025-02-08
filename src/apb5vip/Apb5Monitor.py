import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, First
from pyuvm import uvm_monitor, uvm_analysis_port

from .Apb5Types import *
from .Apb5Transfer import Apb5Transfer
from .Apb5Utils import get_int


class Apb5Monitor(uvm_monitor):
    def __init__(self, name="monitor", agent=None):
        super().__init__(name, agent)
        self.transfer_ap = uvm_analysis_port("transfer_ap", self)
        self.request_ap = uvm_analysis_port("request_ap", self)

    def connect_phase(self):
        self.if_ = cocotb.top

    async def monitor_setup_phase(self, tr: Apb5Transfer):
        assert self.if_ is not None

        # Wait for a transfer to start
        while not self.if_.PSEL.value:
            await RisingEdge(self.if_.PCLK)

        tr.begin_tr(parent_handle=self)

        # Address
        tr.address = get_int(self.if_.PADDR)
        # Protection
        tr.protection.privilege = Privilege(self.if_.PPROT.value[2])
        tr.protection.transaction = Transaction(self.if_.PPROT.value[0])
        if self.if_.RME_SUPPORT.value:
            nse = get_int(self.if_.PNSE)
        else:
            nse = 0
        tr.protection.security = Security(nse << 1 | self.if_.PPROT.value[1])
        # Direction
        tr.direction = Direction(self.if_.PWRITE.value)
        # Data and user data
        if tr.direction == Direction.WRITE:
            tr.data = get_int(self.if_.PWDATA)
            if get_int(self.if_.USER_DATA_WIDTH):
                tr.wuser = get_int(self.if_.PWUSER)
        # Strobe
        tr.strobe = get_int(self.if_.PSTRB)
        # Wakeup
        if self.if_.WAKEUP_SUPPORT.value:
            tr.wakeup = get_int(self.if_.PWAKEUP)
        # User signals
        if get_int(self.if_.USER_REQ_WIDTH):
            tr.auser = get_int(self.if_.PAUSER)

    async def monitor_access_phase(self, tr: Apb5Transfer):
        assert self.if_ is not None

        # Wait one cycle for the Access phase and
        #   for any additional Wait states inserted by the subordinate
        while True:
            await RisingEdge(self.if_.PCLK)
            if self.if_.PREADY.value:
                break

        # Response
        if self.if_.PSLVERR.value:
            tr.response = Response.ERROR
        else:
            tr.response = Response.OKAY
        # Data and user data
        if tr.direction == Direction.READ:
            tr.data = get_int(self.if_.PRDATA)
            if get_int(self.if_.USER_DATA_WIDTH):
                tr.ruser = get_int(self.if_.PRUSER)
        # User response
        if get_int(self.if_.USER_RESP_WIDTH):
            tr.buser = get_int(self.if_.PBUSER)

        tr.end_tr()

    async def monitor_transfers(self):
        assert self.if_ is not None
        while True:
            tr = Apb5Transfer()
            await self.monitor_setup_phase(tr)
            self.request_ap.write(tr)
            await self.monitor_access_phase(tr)
            self.transfer_ap.write(tr)
            await RisingEdge(self.if_.PCLK)
            self.logger.debug(tr)

    async def wait_reset_start(self):
        assert self.if_ is not None
        if self.if_.PRESETN.value:
            await FallingEdge(self.if_.PRESETN)

    async def wait_reset_end(self):
        assert self.if_ is not None
        if not self.if_.PRESETN.value:
            await RisingEdge(self.if_.PRESETN)

    async def run_phase(self):
        while True:
            await self.wait_reset_end()
            monitor_thread = cocotb.start_soon(self.monitor_transfers())
            reset_thread = cocotb.start_soon(self.wait_reset_start())
            await First(
                monitor_thread,
                reset_thread
            )
            monitor_thread.kill()
