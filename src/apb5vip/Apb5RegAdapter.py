from pyuvm import uvm_reg_adapter, uvm_reg_bus_op, access_e, uvm_resp_t
from .Apb5Transfer import Apb5Transfer
from .Apb5Interface import Apb5Interface
from .Apb5Types import *


class Apb5RegAdapter(uvm_reg_adapter):

    def __init__(self,
                 vif: Apb5Interface,
                 name="apb5_reg_adapter"):
        super().__init__(name)
        self.byte_enable = False
        self.vif = vif

    def bus2reg(self,
                bus_item: Apb5Transfer,
                rw: uvm_reg_bus_op):
        rw.addr = bus_item.address
        rw.data = bus_item.data
        match bus_item.direction:
            case Direction.READ:
                rw.kind = access_e.UVM_READ
            case Direction.WRITE:
                rw.kind = access_e.UVM_WRITE
        match bus_item.response:
            case Response.OKAY:
                rw.status = uvm_resp_t.PASS_RESP
            case Response.ERROR:
                rw.status = uvm_resp_t.ERROR_RESP

    def reg2bus(self,
                rw: uvm_reg_bus_op) -> Apb5Transfer:
        bus_item = Apb5Transfer(vif=self.vif)
        # TODO make randomization optional
        bus_item.randomize_request()
        bus_item.address = rw.addr
        bus_item.data = rw.data
        match rw.kind:
            case access_e.UVM_READ:
                bus_item.direction = Direction.READ
            case access_e.UVM_WRITE:
                bus_item.direction = Direction.WRITE
        if rw.byte_en:
            raise NotImplementedError
        else:
            bus_item.strobe = 2**(bus_item.DATA_WIDTH//8)-1
        # TODO protection
        return bus_item
