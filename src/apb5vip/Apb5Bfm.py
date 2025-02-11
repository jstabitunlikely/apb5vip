import cocotb
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles

from pyuvm import uvm_component
from .Apb5Types import *
from .Apb5Utils import get_int
from .Apb5Transfer import Apb5Transfer


class Apb5Bfm(uvm_component):

    def __init__(self, name="bfm", parent=None):
        super().__init__(name, parent)
        # TODO use an interface object
        self.if_ = cocotb.top

    async def wait_cycles(self, cycles):
        assert self.if_ is not None
        await ClockCycles(self.if_.PCLK, cycles)

    async def reset(self):
        ...

    async def run_phase(self):
        await self.reset()


class Apb5RequesterBfm(Apb5Bfm):

    def reset_requester_signals(self):
        assert self.if_ is not None
        self.if_.PADDR.value = 0
        self.if_.PPROT.value = 0
        if self.if_.RME_SUPPORT.value:
            self.if_.PNSE.value = 0
        self.if_.PWRITE.value = 0
        self.if_.PWDATA.value = 0
        self.if_.PSTRB.value = 0
        if self.if_.WAKEUP_SUPPORT.value:
            self.if_.PWAKEUP.value = 0
        if get_int(self.if_.USER_REQ_WIDTH):
            self.if_.PAUSER.value = 0
        if get_int(self.if_.USER_DATA_WIDTH):
            self.if_.PWUSER.value = 0
        self.if_.PSEL.value = 0
        self.if_.PENABLE.value = 0

    async def reset(self):
        assert self.if_ is not None
        self.reset_requester_signals()
        if self.if_.PRESETN.value:
            await FallingEdge(self.if_.PRESETN)
        await RisingEdge(self.if_.PRESETN)
        await RisingEdge(self.if_.PCLK)

    async def write_setup_phase(self, transfer: Apb5Transfer):
        assert self.if_ is not None
        self.if_.PADDR.value = transfer.address
        self.if_.PPROT.value = transfer.protection.get_pprot()
        if self.if_.RME_SUPPORT.value:
            self.if_.PNSE.value = transfer.protection.get_pnse()
        self.if_.PWRITE.value = 1
        self.if_.PWDATA.value = transfer.data
        self.if_.PSTRB.value = transfer.strobe
        if self.if_.WAKEUP_SUPPORT.value:
            self.if_.PWAKEUP.value = transfer.wakeup
        if get_int(self.if_.USER_REQ_WIDTH):
            self.if_.PAUSER.value = transfer.auser
        if get_int(self.if_.USER_DATA_WIDTH):
            self.if_.PWUSER.value = transfer.wuser
        self.if_.PSEL.value = 1
        await RisingEdge(self.if_.PCLK)
        self.if_.PENABLE.value = 1

    async def write_access_phase(self):
        assert self.if_ is not None
        # Wait states by the completer
        while not self.if_.PREADY.value:
            await RisingEdge(self.if_.PCLK)
        self.if_.PSEL.value = 0
        self.if_.PENABLE.value = 0
        # TODO drive unqualified signal values: zero, one, 'x', random or hold

    async def write(self, transfer: Apb5Transfer):
        await self.write_setup_phase(transfer)
        await self.write_access_phase()

    async def read_setup_phase(self, transfer: Apb5Transfer):
        assert self.if_ is not None
        self.if_.PADDR.value = transfer.address
        self.if_.PPROT.value = transfer.protection.get_pprot()
        if self.if_.RME_SUPPORT.value:
            self.if_.PNSE.value = transfer.protection.get_pnse()
        self.if_.PWRITE.value = 0
        self.if_.PSTRB.value = transfer.strobe
        if self.if_.WAKEUP_SUPPORT.value:
            self.if_.PWAKEUP.value = transfer.wakeup
        if get_int(self.if_.USER_REQ_WIDTH):
            self.if_.PAUSER.value = transfer.auser
        self.if_.PSEL.value = 1
        await RisingEdge(self.if_.PCLK)
        self.if_.PENABLE.value = 1

    async def read_access_phase(self, transfer: Apb5Transfer):
        assert self.if_ is not None
        # Wait states by the completer
        while not self.if_.PREADY.value:
            await RisingEdge(self.if_.PCLK)
        self.if_.PSEL.value = 0
        self.if_.PENABLE.value = 0
        transfer.data = get_int(self.if_.PRDATA)
        transfer.response = Response(self.if_.PSLVERR.value)
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
        assert self.if_ is not None
        self.if_.PRDATA.value = 0
        self.if_.PREADY.value = 0
        self.if_.PSLVERR.value = 0
        if get_int(self.if_.USER_RESP_WIDTH):
            self.if_.PBUSER.value = 0
        if get_int(self.if_.USER_DATA_WIDTH):
            self.if_.PRUSER.value = 0

    async def reset(self):
        assert self.if_ is not None
        self.reset_completer_signals()
        if self.if_.PRESETN.value:
            await FallingEdge(self.if_.PRESETN)
        await RisingEdge(self.if_.PRESETN)
        await RisingEdge(self.if_.PCLK)

    async def respond(self, response: Apb5Transfer):
        assert self.if_ is not None
        await self.wait_cycles(response.response_delay)
        self.if_.PRDATA.value = response.data
        self.if_.PSLVERR.value = response.response
        self.if_.PREADY.value = 1
        await RisingEdge(self.if_.PCLK)
        self.if_.PREADY.value = 0
