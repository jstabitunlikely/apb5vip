import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, First
from pyuvm import uvm_monitor, uvm_analysis_port, UVMConfigItemNotFound

from .Apb5Types import *
from .Apb5Transfer import Apb5Transfer
from .Apb5Interface import Apb5Interface
from .Apb5CoverageCollector import Apb5CoverageCollector


class Apb5Monitor(uvm_monitor):

    def __init__(self, name="monitor", agent=None):
        super().__init__(name, agent)
        self.transfer_ap = uvm_analysis_port("transfer_ap", self)
        self.request_ap = uvm_analysis_port("request_ap", self)

    def build_phase(self):
        try:
            self.has_coverage = self.cdb_get("has_coverage", self.get_full_name())

        except UVMConfigItemNotFound:
            self.has_coverage = False
        if self.has_coverage:
            self.coverage = Apb5CoverageCollector("coverage_collector", parent=self)

    def connect_phase(self):
        self.vif = self.cdb_get("vif", self.get_full_name())
        if self.has_coverage:
            self.transfer_ap.connect(self.coverage.analysis_export)

    async def monitor_setup_phase(self, tr: Apb5Transfer):
        assert isinstance(self.vif, Apb5Interface)

        # Wait for a transfer to start
        while not self.vif.psel.value:
            await RisingEdge(self.vif.pclk)

        tr.begin_tr(parent_handle=self)

        # Address
        tr.address = self.vif.get_value("paddr")
        # Protection
        tr.protection.privilege = Privilege(self.vif.pprot.value[2])
        tr.protection.transaction = Transaction(self.vif.pprot.value[0])
        if self.vif.RME_SUPPORT:
            nse = self.vif.get_value("pnse")
        else:
            nse = 0
        tr.protection.security = Security(nse << 1 | self.vif.pprot.value[1])
        # Direction
        tr.direction = Direction(self.vif.pwrite.value)
        # Data and user data
        if tr.direction == Direction.WRITE:
            tr.data = self.vif.get_value("pwdata")
            if self.vif.USER_DATA_WIDTH:
                tr.wuser = self.vif.get_value("pwuser")
        # Strobe
        tr.strobe = self.vif.get_value("pstrb")
        # Wakeup
        if self.vif.WAKEUP_SUPPORT:
            tr.wakeup_mode = self.vif.get_value("pwakeup")
        # User signals
        if self.vif.USER_REQ_WIDTH:
            tr.auser = self.vif.get_value("pauser")

    async def monitor_access_phase(self, tr: Apb5Transfer):
        assert isinstance(self.vif, Apb5Interface)

        # Wait one cycle for the Access phase and
        #   for any additional Wait states inserted by the subordinate
        while True:
            await RisingEdge(self.vif.pclk)
            if self.vif.pready.value:
                break

        # Response
        if self.vif.pslverr.value:
            tr.response = Response.ERROR
        else:
            tr.response = Response.OKAY
        # Data and user data
        if tr.direction == Direction.READ:
            tr.data = self.vif.get_value("prdata")
            if self.vif.USER_DATA_WIDTH:
                tr.ruser = self.vif.get_value("pruser")
        # User response
        if self.vif.USER_RESP_WIDTH:
            tr.buser = self.vif.get_value("pbuser")

        tr.end_tr()

    async def monitor_transfers(self):
        assert isinstance(self.vif, Apb5Interface)
        while True:
            tr = Apb5Transfer(vif=self.vif)
            await self.monitor_setup_phase(tr)
            self.request_ap.write(tr)
            await self.monitor_access_phase(tr)
            self.transfer_ap.write(tr)
            await RisingEdge(self.vif.pclk)
            self.logger.debug(tr)

    async def wait_reset_start(self):
        assert isinstance(self.vif, Apb5Interface)
        if self.vif.presetn.value:
            await FallingEdge(self.vif.presetn)

    async def wait_reset_end(self):
        assert isinstance(self.vif, Apb5Interface)
        if not self.vif.presetn.value:
            await RisingEdge(self.vif.presetn)

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
