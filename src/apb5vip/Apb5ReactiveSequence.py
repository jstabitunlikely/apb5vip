from pyuvm import uvm_sequence
from .Apb5Sequencer import Apb5Sequencer

class Apb5ReactiveSequence(uvm_sequence):

    async def body(self):
        assert isinstance(self.sequencer, Apb5Sequencer)
        while True:
            request = await self.sequencer.request_fifo.get()
            await self.start_item(request)
            request.randomize_response()
            await self.finish_item(request)
