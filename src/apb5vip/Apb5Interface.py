import cocotb

# TODO this file is a placeholder only
class Apb5Interface(object):
    async def drive(self, transaction):
        # Implement driving the transaction onto the actual hardware/simulator interface
        print(f"Driving: {transaction}")
        await cocotb.triggers.Timer(1, units="ns")  # Example delay
        pass

    async def capture(self, transaction):
        # Implement capturing a transaction from the actual hardware/simulator interface
        transaction.addr = 0x100  # Example
        transaction.data = 0xAA
        print("Capturing")
        await cocotb.triggers.Timer(1, units="ns")  # Example delay
        return transaction

    async def reset(self):
        # Example reset sequence
        await cocotb.triggers.Timer(10, units="ns")
        pass
