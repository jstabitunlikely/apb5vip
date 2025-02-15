from pyuvm import uvm_env
from apb5vip import *


class Apb5Env(uvm_env):

    def __init__(self, name="apb5_env", parent=None):
        super().__init__(name, parent)

    def build_phase(self):
        self.cdb_set(label="is_active", value=True, inst_path="requester_agent*")
        self.cdb_set(label="is_requester", value=True, inst_path="requester_agent*")
        self.requester_agent = Apb5Agent("requester_agent", self)

        self.cdb_set(label="is_active", value=True, inst_path="completer_agent*")
        self.cdb_set(label="is_requester", value=False, inst_path="completer_agent*")
        self.completer_agent = Apb5Agent("completer_agent", self)

        self.cdb_set(label="is_active", value=False, inst_path="completer_agent_cov*")
        self.cdb_set(label="is_requester", value=False, inst_path="completer_agent_cov*")
        self.cdb_set(label="has_coverage", value=True, inst_path="completer_agent_cov*")
        self.completer_agent_cov = Apb5Agent("completer_agent_cov", self)
