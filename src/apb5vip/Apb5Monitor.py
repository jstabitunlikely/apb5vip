import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, First
from pyuvm import uvm_monitor, uvm_analysis_port, ConfigDB

from .Apb5Types import *
from .Apb5Transfer import Apb5Transfer
from .Apb5Interface import Apb5Interface


class Apb5Monitor(uvm_monitor):
    def __init__(self, name="monitor", agent=None):
        super().__init__(name, agent)
        self.transfer_ap = uvm_analysis_port("transfer_ap", self)
        self.request_ap = uvm_analysis_port("request_ap", self)

    def connect_phase(self):
        self.if_ = ConfigDB().get(None, self.get_full_name(), "vif")

    async def monitor_setup_phase(self, tr: Apb5Transfer):
        assert isinstance(self.if_, Apb5Interface)

        # Wait for a transfer to start
        while not self.if_.psel.value:
            await RisingEdge(self.if_.pclk)

        tr.begin_tr(parent_handle=self)

        # Address
        tr.address = self.if_.get_value("paddr")
        # Protection
        tr.protection.privilege = Privilege(self.if_.pprot.value[2])
        tr.protection.transaction = Transaction(self.if_.pprot.value[0])
        if self.if_.RME_SUPPORT.value:
            nse = self.if_.get_value("pnse")
        else:
            nse = 0
        tr.protection.security = Security(nse << 1 | self.if_.pprot.value[1])
        # Direction
        tr.direction = Direction(self.if_.pwrite.value)
        # Data and user data
        if tr.direction == Direction.WRITE:
            tr.data = self.if_.get_value("pwdata")
            if self.if_.get_value("USER_DATA_WIDTH"):
                tr.wuser = self.if_.get_value("pwuser")
        # Strobe
        tr.strobe = self.if_.get_value("pstrb")
        # Wakeup
        if self.if_.WAKEUP_SUPPORT.value:
            tr.wakeup = self.if_.get_value("pwakeup")
        # User signals
        if self.if_.get_value("USER_REQ_WIDTH"):
            tr.auser = self.if_.get_value("pauser")

    async def monitor_access_phase(self, tr: Apb5Transfer):
        assert isinstance(self.if_, Apb5Interface)

        # Wait one cycle for the Access phase and
        #   for any additional Wait states inserted by the subordinate
        while True:
            await RisingEdge(self.if_.pclk)
            if self.if_.pready.value:
                break

        # Response
        if self.if_.pslverr.value:
            tr.response = Response.ERROR
        else:
            tr.response = Response.OKAY
        # Data and user data
        if tr.direction == Direction.READ:
            tr.data = self.if_.get_value("prdata")
            if self.if_.get_value("USER_DATA_WIDTH"):
                tr.ruser = self.if_.get_value("pruser")
        # User response
        if self.if_.get_value("USER_RESP_WIDTH"):
            tr.buser = self.if_.get_value("pbuser")

        tr.end_tr()

    async def monitor_transfers(self):
        assert isinstance(self.if_, Apb5Interface)
        while True:
            tr = Apb5Transfer()
            await self.monitor_setup_phase(tr)
            self.request_ap.write(tr)
            await self.monitor_access_phase(tr)
            self.transfer_ap.write(tr)
            await RisingEdge(self.if_.pclk)
            self.logger.debug(tr)

    async def wait_reset_start(self):
        assert isinstance(self.if_, Apb5Interface)
        if self.if_.presetn.value:
            await FallingEdge(self.if_.presetn)

    async def wait_reset_end(self):
        assert isinstance(self.if_, Apb5Interface)
        if not self.if_.presetn.value:
            await RisingEdge(self.if_.presetn)

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
