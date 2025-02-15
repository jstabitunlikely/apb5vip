from pyuvm import uvm_sequencer, uvm_tlm_analysis_fifo


class Apb5Sequencer(uvm_sequencer):

    def __init__(self, name="sequencer", parent=None):
        super().__init__(name, parent)
        self.request_fifo = uvm_tlm_analysis_fifo("request_fifo", self)

    def connect_phase(self):
        self.vif = self.cdb_get("vif", self.get_full_name())
