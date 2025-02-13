from pyuvm import uvm_sequence
from .Apb5Transfer import Apb5Transfer
from .Apb5Sequencer import Apb5Sequencer


class Apb5Sequence(uvm_sequence):

    def __init__(self, name="sequence"):
        super().__init__(name)

    async def body(self):
        assert isinstance(self.sequencer, Apb5Sequencer)
        # TODO use a virtual sequence for multiple transfers
        for i in range(1_000):
            transfer = Apb5Transfer(name=f"transfer{i}", vif=self.sequencer.vif)
            await self.start_item(transfer)
            transfer.randomize_request()
            await self.finish_item(transfer)
