from pyuvm import uvm_subscriber
from cocotb_coverage.coverage import CoverPoint, CoverCross, coverage_section, coverage_db
from .Apb5Types import *
from .Apb5Transfer import Apb5Transfer


class Apb5TransferCoverage:

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

    cp_strobe = CoverPoint(
        name="transfer.strobe",
        xf=lambda x: x.strobe,
        # TODO how to implement sampling conditions with cocotb-coverage?
        bins=list(range(0x10)),
    )

    cross_address_x_direction = CoverCross(
        "transfer.address_x_direction",
        items=["transfer.address", "transfer.direction"],
    )

    coverage = coverage_section(
        cp_address,
        cp_direction,
        cp_strobe,
        cross_address_x_direction,
    )

    @coverage
    def sample(self, transfer):
        pass


class Apb5CoverageCollector(uvm_subscriber):

    def __init__(self, name="coverage_collector", parent=None):
        super().__init__(name, parent)
        self.transfer_coverage = Apb5TransferCoverage()

    def write(self, transfer: Apb5Transfer):
        self.transfer_coverage.sample(transfer)

    def report_phase(self):
        coverage_db.export_to_yaml()
