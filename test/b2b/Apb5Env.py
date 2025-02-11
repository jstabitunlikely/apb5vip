from pyuvm import uvm_env, ConfigDB
from apb5vip import *


class Apb5Env(uvm_env):

    def __init__(self, name="apb5_env", parent=None):
        super().__init__(name, parent)

    def build_phase(self):
        ConfigDB().set(self, "*requester_agent*", "is_active", True)
        ConfigDB().set(self, "*requester_agent*", "is_requester", True)
        self.requester_agent = Apb5Agent("requester_agent", self)

        ConfigDB().set(self, "*completer_agent*", "is_active", True)
        ConfigDB().set(self, "*completer_agent*", "is_requester", False)
        self.completer_agent = Apb5Agent("completer_agent", self)
