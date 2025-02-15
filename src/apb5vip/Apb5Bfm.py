import cocotb
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles

from pyuvm import uvm_component
from .Apb5Types import *
from .Apb5Transfer import Apb5Transfer
from .Apb5Interface import Apb5Interface


class Apb5Bfm(uvm_component):

    def __init__(self, name="bfm", parent=None):
        super().__init__(name, parent)

    def connect_phase(self):
        self.vif = self.cdb_get("vif", self.get_full_name())

    async def run_phase(self):
        await self.reset()

    async def wait_cycles(self, cycles):
        assert isinstance(self.vif, Apb5Interface)
        await ClockCycles(self.vif.pclk, cycles)

    async def reset(self):
        ...


class Apb5RequesterBfm(Apb5Bfm):

    def reset_requester_signals(self):
        assert isinstance(self.vif, Apb5Interface)
        self.vif.paddr.value = 0
        self.vif.pprot.value = 0
        if self.vif.RME_SUPPORT:
            self.vif.pnse.value = 0
        self.vif.pwrite.value = 0
        self.vif.pwdata.value = 0
        self.vif.pstrb.value = 0
        if self.vif.WAKEUP_SUPPORT:
            self.vif.pwakeup.value = 0
        if self.vif.USER_REQ_WIDTH:
            self.vif.pauser.value = 0
        if self.vif.USER_DATA_WIDTH:
            self.vif.pwuser.value = 0
        self.vif.psel.value = 0
        self.vif.penable.value = 0

    async def reset(self):
        assert isinstance(self.vif, Apb5Interface)
        self.reset_requester_signals()
        if self.vif.presetn.value:
            await FallingEdge(self.vif.presetn)
        await RisingEdge(self.vif.presetn)
        await RisingEdge(self.vif.pclk)

    async def write_setup_phase(self, transfer: Apb5Transfer):
        assert isinstance(self.vif, Apb5Interface)
        self.vif.paddr.value = transfer.address
        self.vif.pprot.value = transfer.protection.get_pprot()
        if self.vif.RME_SUPPORT:
            self.vif.pnse.value = transfer.protection.get_pnse()
        self.vif.pwrite.value = 1
        self.vif.pwdata.value = transfer.data
        self.vif.pstrb.value = transfer.strobe
        if self.vif.WAKEUP_SUPPORT and transfer.wakeup_mode == WakeupMode.WITH_SEL:
            self.vif.pwakeup.value = 1
        if self.vif.USER_REQ_WIDTH:
            self.vif.pauser.value = transfer.auser
        if self.vif.USER_DATA_WIDTH:
            self.vif.pwuser.value = transfer.wuser
        self.vif.psel.value = 1
        await RisingEdge(self.vif.pclk)
        self.vif.penable.value = 1
        if self.vif.WAKEUP_SUPPORT and transfer.wakeup_mode == WakeupMode.WITH_ENABLE:
            self.vif.pwakeup.value = 1

    async def write_access_phase(self):
        assert isinstance(self.vif, Apb5Interface)
        # Wait states by the completer
        while not self.vif.pready.value:
            await RisingEdge(self.vif.pclk)
        self.vif.psel.value = 0
        self.vif.penable.value = 0
        if self.vif.WAKEUP_SUPPORT:
            self.vif.pwakeup.value = 0
        # TODO drive unqualified signal values: zero, one, 'x', random or hold

    async def write(self, transfer: Apb5Transfer):
        await self.write_setup_phase(transfer)
        await self.write_access_phase()

    async def read_setup_phase(self, transfer: Apb5Transfer):
        assert isinstance(self.vif, Apb5Interface)
        self.vif.paddr.value = transfer.address
        self.vif.pprot.value = transfer.protection.get_pprot()
        if self.vif.RME_SUPPORT:
            self.vif.pnse.value = transfer.protection.get_pnse()
        self.vif.pwrite.value = 0
        self.vif.pstrb.value = transfer.strobe
        if self.vif.WAKEUP_SUPPORT and transfer.wakeup_mode == WakeupMode.WITH_SEL:
            self.vif.pwakeup.value = 1
        if self.vif.USER_REQ_WIDTH:
            self.vif.pauser.value = transfer.auser
        self.vif.psel.value = 1
        await RisingEdge(self.vif.pclk)
        self.vif.penable.value = 1
        if self.vif.WAKEUP_SUPPORT and transfer.wakeup_mode == WakeupMode.WITH_ENABLE:
            self.vif.pwakeup.value = 1

    async def read_access_phase(self, transfer: Apb5Transfer):
        assert isinstance(self.vif, Apb5Interface)
        # Wait states by the completer
        while not self.vif.pready.value:
            await RisingEdge(self.vif.pclk)
        self.vif.psel.value = 0
        self.vif.penable.value = 0
        if self.vif.WAKEUP_SUPPORT:
            self.vif.pwakeup.value = 0
        transfer.data = self.vif.get_value("prdata")
        transfer.response = self.vif.get_value("pslverr", Response)
        # TODO drive unqualified signal values: zero, one, 'x', random or hold

    async def read(self, transfer: Apb5Transfer):
        await self.read_setup_phase(transfer)
        await self.read_access_phase(transfer)

    async def drive(self, transfer: Apb5Transfer):
        await self.wait_cycles(transfer.request_delay)
        match transfer.direction:
            case Direction.READ:
                await self.read(transfer)
            case Direction.WRITE:
                await self.write(transfer)
        return transfer


class Apb5CompleterBfm(Apb5Bfm):

    def reset_completer_signals(self):
        assert isinstance(self.vif, Apb5Interface)
        self.vif.prdata.value = 0
        self.vif.pready.value = 0
        self.vif.pslverr.value = 0
        if self.vif.USER_RESP_WIDTH:
            self.vif.pbuser.value = 0
        if self.vif.USER_DATA_WIDTH:
            self.vif.pruser.value = 0

    async def reset(self):
        assert isinstance(self.vif, Apb5Interface)
        self.reset_completer_signals()
        if self.vif.presetn.value:
            await FallingEdge(self.vif.presetn)
        await RisingEdge(self.vif.presetn)
        await RisingEdge(self.vif.pclk)

    async def respond(self, response: Apb5Transfer):
        assert isinstance(self.vif, Apb5Interface)
        await self.wait_cycles(response.response_delay)
        self.vif.prdata.value = response.data
        self.vif.pslverr.value = response.response
        if self.vif.USER_RESP_WIDTH:
            self.vif.pbuser.value = response.buser
        if self.vif.USER_DATA_WIDTH:
            self.vif.pruser.value = response.ruser
        self.vif.pready.value = 1
        await RisingEdge(self.vif.pclk)
        self.vif.pready.value = 0
