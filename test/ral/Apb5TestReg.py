import pyuvm
from pyuvm import path_t, check_t, uvm_resp_t

from apb5vip import *
from Apb5TestBase import Apb5TestBase


@pyuvm.test()
class Apb5TestReg(Apb5TestBase):

    def __init__(self, name="apb5_test_simple", parent=None):
        super().__init__(name, parent)

    def end_of_elaboration_phase(self):
        super().end_of_elaboration_phase()
        self.ral = self.env.reg_block
        self.map = self.ral.def_map

    async def run_phase(self):
        await super().run_phase()
        self.raise_objection()

        status, rdata = await self.ral.ID.read(self.map, path_t.FRONTDOOR, check_t.CHECK)
        assert status == uvm_resp_t.PASS_RESP

        self.logger.info(f"0x{rdata:08x}")

        await self.wait_cycles(5)
        self.drop_objection()
