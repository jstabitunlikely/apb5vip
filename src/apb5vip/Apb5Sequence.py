from pyuvm import uvm_sequence
from cocotb_coverage import crv
from .Apb5Transfer import Apb5Transfer
from .Apb5Sequencer import Apb5Sequencer


class Apb5Sequence(uvm_sequence, crv.Randomized):

    def __init__(self, name="sequence"):
        super().__init__(name)
        crv.Randomized.__init__(self)
        self.num_of_transfers = 1
        self.add_rand("num_of_transfers", domain=list(range(2_000)))

    async def body(self):
        assert isinstance(self.sequencer, Apb5Sequencer)
        for i in range(self.num_of_transfers):
            transfer = Apb5Transfer(name=f"transfer{i}", vif=self.sequencer.vif)
            await self.start_item(transfer)
            transfer.randomize_request()
            await self.finish_item(transfer)
