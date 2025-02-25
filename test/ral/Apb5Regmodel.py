from pyuvm import uvm_reg, uvm_reg_field, predict_t, uvm_reg_block, uvm_reg_map


class Id(uvm_reg):

    def __init__(self, name="Id", reg_width=32):
        super().__init__(name, reg_width)
        self.ID0 = uvm_reg_field('ID0')
        self.ID1 = uvm_reg_field('ID1')

    def build(self):
        self.ID0.configure(self, 16, 0, 'RO', False, 0)
        self.ID1.configure(self, 16, 16, 'RO', False, 0)
        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class Data(uvm_reg):

    def __init__(self, name="Data", reg_width=32):
        super().__init__(name, reg_width)
        self.DATA0 = uvm_reg_field('DATA0')
        self.DATA1 = uvm_reg_field('DATA1')

    def build(self):
        self.DATA0.configure(self, 8, 0, 'RW', False, 0)
        self.DATA1.configure(self, 8, 16, 'RW', False, 0)
        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class Apb5RegBlock(uvm_reg_block):

    def __init__(self, name="Apb5RegBlock"):
        super().__init__(name)
        self.def_map = uvm_reg_map('map')
        self.def_map.configure(self, 0)

        self.ID = Id('Id')
        self.ID.configure(self, "0x0", "", False, False)
        self.def_map.add_reg(self.ID, "0x0", "RO")

        self.DATA = Data('Data')
        self.DATA.configure(self, "0x0", "", False, False)
        self.def_map.add_reg(self.DATA, "0x4", "RW")
