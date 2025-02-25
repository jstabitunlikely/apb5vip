from pyuvm import uvm_env
from apb5vip import *
from Apb5Regmodel import Apb5RegBlock


class Apb5Env(uvm_env):

    def __init__(self, name="apb5_env", parent=None):
        super().__init__(name, parent)

    def build_phase(self):
        # Requester agent (active) configuration
        self.cdb_set(label="is_active", value=True, inst_path="requester_agent*")
        self.cdb_set(label="is_requester", value=True, inst_path="requester_agent*")
        self.requester_agent = Apb5Agent("requester_agent", self)

        # Register model configuration
        self.reg_block = Apb5RegBlock("reg_block")
        vif = self.cdb_get("vif", "")
        assert isinstance(vif, Apb5Interface)
        self.reg_adapter = Apb5RegAdapter(name="reg_adapter", vif=vif)

    def connect_phase(self):
        self.reg_block.def_map.sequencer = self.requester_agent.sequencer
        self.reg_block.def_map.adapter = self.reg_adapter
