from pyuvm import uvm_subscriber
from cocotb_coverage.coverage import CoverPoint, CoverCross, coverage_section, coverage_db
from .Apb5Types import *
from .Apb5Transfer import Apb5Transfer


class Apb5CoverageCollector(uvm_subscriber):

    cp_address = CoverPoint(
        name="transfer.address",
        xf=lambda x: x.address,
        rel=lambda v, b: b[0] <= v < b[1],
        # TODO ranges based on ADDR_WIDTH parameter
        bins=[(0x0, 0x0), (0x1, 0xFE), (0xFF, 0xFF)],
        bins_labels=["min", "middle", "max"],
    )

    cp_direction = CoverPoint(
        name="transfer.direction",
        xf=lambda x: x.direction,
        bins=list(Direction),
        bins_labels=[d.name for d in Direction],
    )

    coverage = coverage_section(
        cp_address,
        cp_direction,
    )

    @coverage
    def sample(self, transfer):
        pass

    def __init__(self, name="coverage_collector", parent=None):
        super().__init__(name, parent)

    def write(self, transfer: Apb5Transfer):
        self.sample(transfer)

    def report_phase(self):
        coverage_db.export_to_yaml()
