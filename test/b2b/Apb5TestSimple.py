import pyuvm

from apb5vip import *
from Apb5TestBase import Apb5TestBase


@pyuvm.test()
class Apb5TestSimple(Apb5TestBase):

    def __init__(self, name="apb5_test_simple", parent=None):
        super().__init__(name, parent)

    def end_of_elaboration_phase(self):
        super().end_of_elaboration_phase()
        self.apb5_requester_seq = Apb5Sequence("apb5_requester_seq")

    async def run_phase(self):
        await super().run_phase()
        self.raise_objection()

        requester_seqr = self.env.requester_agent.sequencer
        await self.apb5_requester_seq.start(requester_seqr)

        await self.wait_cycles(5)
        self.drop_objection()
