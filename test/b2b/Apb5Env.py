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

    def connect_phase(self):
        # No special connections needed within the env in this basic example.
        # Connections between agents and interface are handled in agent's connect_phase
        pass

    def start_of_simulation(self):
        # Configure the agents here if needed, like setting which one is master and which one is slave
        # self.requester_agent.apb_if = self.apb_if
        # self.completer_agent.apb_if = self.apb_if
        pass
