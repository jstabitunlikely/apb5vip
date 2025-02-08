from pyuvm import uvm_agent, ConfigDB
from .Apb5Driver import Apb5Driver
from .Apb5Monitor import Apb5Monitor
from .Apb5Sequencer import Apb5Sequencer


class Apb5Agent(uvm_agent):

    def __init__(self, name="agent", parent=None):
        super().__init__(name, parent)

    def build_phase(self):
        super().build_phase()
        is_requester = ConfigDB().get(None, self.get_full_name(), "is_requester")
        self.is_requester = bool(is_requester)
        if self.is_active:
            self.driver = Apb5Driver("driver", self, self.is_requester)
            self.sequencer = Apb5Sequencer("sequencer", self)
        self.monitor = Apb5Monitor("monitor", self)

    def connect_phase(self):
        if self.is_active:
            self.driver.seq_item_port.connect(self.sequencer.seq_item_export)
            if not self.is_requester:
                self.monitor.request_ap.connect(self.sequencer.request_fifo.analysis_export)
