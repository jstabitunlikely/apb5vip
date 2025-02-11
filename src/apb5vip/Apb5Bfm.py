import cocotb
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles

from pyuvm import uvm_component, ConfigDB
from .Apb5Types import *
from .Apb5Transfer import Apb5Transfer
from .Apb5Interface import Apb5Interface


class Apb5Bfm(uvm_component):

    def __init__(self, name="bfm", parent=None):
        super().__init__(name, parent)

    def connect_phase(self):
        self.if_ = ConfigDB().get(None, self.get_full_name(), "vif")

    async def run_phase(self):
        await self.reset()

    async def wait_cycles(self, cycles):
        assert isinstance(self.if_, Apb5Interface)
        await ClockCycles(self.if_.pclk, cycles)

    async def reset(self):
        ...


class Apb5RequesterBfm(Apb5Bfm):

    def reset_requester_signals(self):
        assert isinstance(self.if_, Apb5Interface)
        self.if_.paddr.value = 0
        self.if_.pprot.value = 0
        if self.if_.RME_SUPPORT.value:
            self.if_.pnse.value = 0
        self.if_.pwrite.value = 0
        self.if_.pwdata.value = 0
        self.if_.pstrb.value = 0
        if self.if_.WAKEUP_SUPPORT.value:
            self.if_.pwakeup.value = 0
        if self.if_.get_value("USER_REQ_WIDTH"):
            self.if_.pauser.value = 0
        if self.if_.get_value("USER_DATA_WIDTH"):
            self.if_.pwuser.value = 0
        self.if_.psel.value = 0
        self.if_.penable.value = 0

    async def reset(self):
        assert isinstance(self.if_, Apb5Interface)
        self.reset_requester_signals()
        if self.if_.presetn.value:
            await FallingEdge(self.if_.presetn)
        await RisingEdge(self.if_.presetn)
        await RisingEdge(self.if_.pclk)

    async def write_setup_phase(self, transfer: Apb5Transfer):
        assert isinstance(self.if_, Apb5Interface)
        self.if_.paddr.value = transfer.address
        self.if_.pprot.value = transfer.protection.get_pprot()
        if self.if_.RME_SUPPORT.value:
            self.if_.pnse.value = transfer.protection.get_pnse()
        self.if_.pwrite.value = 1
        self.if_.pwdata.value = transfer.data
        self.if_.pstrb.value = transfer.strobe
        if self.if_.WAKEUP_SUPPORT.value:
            self.if_.pwakeup.value = transfer.wakeup
        if self.if_.get_value("USER_REQ_WIDTH"):
            self.if_.pauser.value = transfer.auser
        if self.if_.get_value("USER_DATA_WIDTH"):
            self.if_.pwuser.value = transfer.wuser
        self.if_.psel.value = 1
        await RisingEdge(self.if_.pclk)
        self.if_.penable.value = 1

    async def write_access_phase(self):
        assert isinstance(self.if_, Apb5Interface)
        # Wait states by the completer
        while not self.if_.pready.value:
            await RisingEdge(self.if_.pclk)
        self.if_.psel.value = 0
        self.if_.penable.value = 0
        # TODO drive unqualified signal values: zero, one, 'x', random or hold

    async def write(self, transfer: Apb5Transfer):
        await self.write_setup_phase(transfer)
        await self.write_access_phase()

    async def read_setup_phase(self, transfer: Apb5Transfer):
        assert isinstance(self.if_, Apb5Interface)
        self.if_.paddr.value = transfer.address
        self.if_.pprot.value = transfer.protection.get_pprot()
        if self.if_.RME_SUPPORT.value:
            self.if_.pnse.value = transfer.protection.get_pnse()
        self.if_.pwrite.value = 0
        self.if_.pstrb.value = transfer.strobe
        if self.if_.WAKEUP_SUPPORT.value:
            self.if_.pwakeup.value = transfer.wakeup
        if self.if_.get_value("USER_REQ_WIDTH"):
            self.if_.pauser.value = transfer.auser
        self.if_.psel.value = 1
        await RisingEdge(self.if_.pclk)
        self.if_.penable.value = 1

    async def read_access_phase(self, transfer: Apb5Transfer):
        assert isinstance(self.if_, Apb5Interface)
        # Wait states by the completer
        while not self.if_.pready.value:
            await RisingEdge(self.if_.pclk)
        self.if_.psel.value = 0
        self.if_.penable.value = 0
        transfer.data = self.if_.get_value("prdata")
        transfer.response = self.if_.get_value("pslverr", Response)
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
        assert isinstance(self.if_, Apb5Interface)
        self.if_.prdata.value = 0
        self.if_.pready.value = 0
        self.if_.pslverr.value = 0
        if self.if_.get_value("USER_RESP_WIDTH"):
            self.if_.pbuser.value = 0
        if self.if_.get_value("USER_DATA_WIDTH"):
            self.if_.pruser.value = 0

    async def reset(self):
        assert isinstance(self.if_, Apb5Interface)
        self.reset_completer_signals()
        if self.if_.presetn.value:
            await FallingEdge(self.if_.presetn)
        await RisingEdge(self.if_.presetn)
        await RisingEdge(self.if_.pclk)

    async def respond(self, response: Apb5Transfer):
        assert isinstance(self.if_, Apb5Interface)
        await self.wait_cycles(response.response_delay)
        self.if_.prdata.value = response.data
        self.if_.pslverr.value = response.response
        self.if_.pready.value = 1
        await RisingEdge(self.if_.pclk)
        self.if_.pready.value = 0
