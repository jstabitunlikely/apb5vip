from pyuvm import uvm_sequence

from .Apb5Transfer import Apb5Transfer


class Apb5Sequence(uvm_sequence):

    def __init__(self, name="sequence"):
        super().__init__(name)

    async def body(self):
        # TODO use a virtual sequence for multiple transfers
        for i in range(5):
            transfer = Apb5Transfer(name=f"transfer[{i}]")
            await self.start_item(transfer)
            transfer.randomize_request()
            await self.finish_item(transfer)
            response = await self.get_response()
