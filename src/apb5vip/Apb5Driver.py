from pyuvm import uvm_driver
from .Apb5Types import *
from .Apb5Bfm import Apb5RequesterBfm, Apb5CompleterBfm


class Apb5Driver(uvm_driver):

    def __init__(self, name="driver", agent=None, is_requester=True):
        super().__init__(name, agent)
        self.is_requester = is_requester

    def build_phase(self):
        if self.is_requester:
            self.bfm = Apb5RequesterBfm(name="requester_bfm", parent=self)
        else:
            self.bfm = Apb5CompleterBfm(name="completer_bfm", parent=self)

    async def run_phase(self):
        await self.bfm.reset()
        while True:
            item = await self.seq_item_port.get_next_item()
            if isinstance(self.bfm, Apb5RequesterBfm):
                await self.bfm.drive(item)
            else:
                await self.bfm.respond(item)
            self.seq_item_port.item_done(item)
