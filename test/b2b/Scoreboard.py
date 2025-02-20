from copy import deepcopy
from pyuvm import uvm_subscriber


class Scoreboard(uvm_subscriber):

    def __init__(self, name="scoreboard", parent=None):
        super().__init__(name, parent)
        self.expected_export = self.uvm_AnalysisImp("expected_export", self, self.write_expected)
        self.actual_export = self.uvm_AnalysisImp("actual_export", self, self.write_actual)
        self.expected_queue = []
        self.actual_queue = []
        self.num_of_mismatches = 0
        self.num_of_matches = 0

    def build_phase(self):
        super().build_phase()
        self.is_in_order = self.cdb_get("is_in_order", self.get_full_name())
        # The corresponding expected items must already be in the scoreboard by the time an actual item arrives
        self.strict_prediction = True

    def write_expected(self, transaction):
        tr = deepcopy(transaction)
        self.expected_queue.append(tr)

    def write_actual(self, transaction):
        self.actual_queue.append(transaction)
        if self.strict_prediction:
            self.compare()

    def compare(self):
        if self.is_in_order:
            self._compare_in_order()
        else:
            self._compare_out_of_order()

    def _compare_out_of_order(self):
        raise NotImplementedError

    def _compare_in_order(self):
        expected = self.expected_queue.pop(0)
        actual = self.actual_queue.pop(0)
        if expected == actual:
            self.logger.debug(f"Match: {actual}")
            self.num_of_matches += 1
        else:
            self.logger.error(f"SCBD Mismatch!")
            self.logger.info(f"\nExpected: {expected}\nActual: {actual}")
            self.num_of_mismatches += 1

    def check_phase(self):
        assert not self.num_of_mismatches, "Mismatching items were found!"
        assert not self.expected_queue, "Expected items left at the end of simulation!"
        assert not self.actual_queue, "Actual items left at the end of simulation!"

    def report_phase(self):
        self.logger.info(f"Matched items: {self.num_of_matches}")
        self.logger.info(f"Mismatched items: {self.num_of_mismatches}")
