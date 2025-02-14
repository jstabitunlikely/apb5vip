import random
from pyuvm import uvm_sequence_item, ConfigDB

from .Apb5Types import *
from .Apb5Interface import Apb5Interface


class Apb5Transfer(uvm_sequence_item):

    def __init__(self, name="transfer", vif=None):
        super().__init__(name)

        self.vif = vif
        assert isinstance(self.vif, Apb5Interface)

        # Bus properties

        # Address width
        self.ADDR_WIDTH = self.vif.ADDR_WIDTH
        # Data width
        self.DATA_WIDTH = self.vif.DATA_WIDTH
        # User request width
        self.USER_REQ_WIDTH = self.vif.USER_REQ_WIDTH
        # User data width
        self.USER_DATA_WIDTH = self.vif.USER_DATA_WIDTH
        # User response width
        self.USER_RESP_WIDTH = self.vif.USER_RESP_WIDTH
        # RME support
        self.RME_SUPPORT = self.vif.RME_SUPPORT
        # Wakeup support
        self.WAKEUP_SUPPORT = self.vif.WAKEUP_SUPPORT

        # Physical bus signals

        # Requester: Address
        self.address = 0
        # Requester: Protection (abstract)
        self.protection = ProtectionExt()
        # Requester: Direction
        self.direction = Direction.READ
        # Requester/Completer: Write/read data
        self.data = 0
        # Requester: Write strobe
        self.strobe = 0
        # Requester: Wake up mode
        self.wakeup_mode = WakeupMode.WITH_SEL
        # Requester: User signals
        self.auser = 0
        self.wuser = 0
        # Completer: Transfer error
        self.response = Response.OKAY
        # Completer: User signals
        self.ruser = 0
        self.buser = 0

        # Timing control for (re)active agents

        # Request delay
        self.request_delay = 0
        # Response delay (wait states)
        self.response_delay = 0

        # Internal stuff

        # Number of digits needed for hex representation
        if self.ADDR_WIDTH % 4:
            self._awx = self.ADDR_WIDTH // 4 + 1
        else:
            self._awx = self.ADDR_WIDTH // 4

        if self.DATA_WIDTH % 4:
            self._dwx = self.DATA_WIDTH // 4 + 1
        else:
            self._dwx = self.DATA_WIDTH // 4

    def randomize_request(self):
        # TODO use a constrained random library e.g. PyVSC
        self.address = random.randint(0, 2**self.ADDR_WIDTH-1)
        self.protection.privilege = random.choice(list(Privilege))
        self.protection.transaction = random.choice(list(Transaction))
        if self.RME_SUPPORT:
            security_domain = list(Security)
        else:
            security_domain = [Security.NONSEC, Security.SEC]
        self.protection.security = random.choice(security_domain)
        self.direction = random.choice(list(Direction))
        if self.direction == Direction.WRITE:
            self.strobe = random.randint(0, 2**(self.DATA_WIDTH//8)-1)
            self.data = random.randint(0, 2**self.DATA_WIDTH-1)
            if self.USER_DATA_WIDTH:
                self.wuser = random.randint(0, 2**self.USER_DATA_WIDTH-1)
        else:
            self.strobe = 2**(self.DATA_WIDTH//8)-1
        if self.WAKEUP_SUPPORT:
            self.wakeup_mode = random.choice(list(WakeupMode))
        if self.USER_REQ_WIDTH:
            self.auser = random.randint(0, 2**self.USER_REQ_WIDTH-1)
        self.request_delay = random.randint(0, 3)

    def randomize_response(self):
        match self.direction:
            case Direction.READ:
                self.data = random.randint(0, 2**self.DATA_WIDTH-1)
                if self.USER_DATA_WIDTH:
                    self.ruser = random.randint(0, 2**self.USER_DATA_WIDTH-1)
        self.response = random.choice(list(Response))
        if self.USER_RESP_WIDTH:
            self.buser = random.randint(0, 2**self.USER_RESP_WIDTH-1)
        self.response_delay = random.randint(0, 3)

    def __eq__(self, value):
        if not isinstance(value, Apb5Transfer):
            return False

        return (
            self.address == value.address and
            self.protection == value.protection and
            self.direction == value.direction and
            self.data == value.data and
            self.strobe == value.strobe and
            self.wakeup_mode == value.wakeup_mode and
            self.auser == value.auser and
            self.wuser == value.wuser and
            self.response == value.response and
            self.ruser == value.ruser and
            self.buser == value.buser and
            self.request_delay == value.request_delay and
            self.response_delay == value.response_delay
        )

    def __hash__(self):
        return hash((
            self.address,
            self.protection,
            self.direction,
            self.data,
            self.strobe,
            self.wakeup_mode,
            self.auser,
            self.wuser,
            self.response,
            self.ruser,
            self.buser,
            self.request_delay,
            self.response_delay
        ))

    def str_multiline(self):
        return '\n'.join([
            f"APB5 Transaction: {self.get_name()}",
            f"  Address: 0x{self.address:0{self._awx}x}",
            f"  Protection: {self.protection}",
            f"  Direction: {self.direction.name}",
            f"  Data: 0x{self.data:0{self._dwx}x}",
            f"  Strobe: {self.strobe:01x}",
            f"  Wakeup: {self.wakeup_mode}",
            f"  AUser: 0x{self.auser:08x}",
            f"  WUser: 0x{self.wuser:08x}",
            f"  Response: {self.response.name}",
            f"  RUser: 0x{self.ruser:08x}",
            f"  BUser: 0x{self.buser:08x}",
            f"  Request Delay: {self.request_delay}",
            f"  Response Delay: {self.response_delay}",
        ])

    def str_oneline(self):
        return ', '.join([
            f"Addr=0x{self.address:0{self._awx}x}",
            f"{self.direction.name:<5}",
            f"Data=0x{self.data:0{self._dwx}x}",
            f"{self.protection}",
            # TODO other important fields
        ])

    def __str__(self):
        return self.str_oneline()

    def __repr__(self):
        return self.str_oneline()
