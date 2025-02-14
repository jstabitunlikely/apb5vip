from math import ceil, floor, log2
from pyuvm import uvm_subscriber, ConfigDB
from cocotb_coverage.coverage import CoverPoint, CoverCross, coverage_section, coverage_db
from .Apb5Types import *
from .Apb5Transfer import Apb5Transfer, Apb5Interface


class Apb5TransferCoverage:

    def __init__(self, vif: Apb5Interface):
        self.vif = vif
        self.define_transfer_coverage()

    def define_transfer_coverage(self):

        # Address
        bins_address_autobins = 16
        bins_address_max = 2**self.vif.ADDR_WIDTH
        bins_address_step = ceil(bins_address_max / bins_address_autobins)
        # TODO: the middle ranges are a bit rough around the edges, because they include the min and max vales as
        # well. Additionally, if ADDR_WIDTH is not dividable by autobins, values grater than maximum are also included in
        # the last bin.
        bins_address = \
            [(0x0, 0x0)] + \
            [(i * bins_address_step, (i + 1) * bins_address_step) for i in range(bins_address_autobins)] + \
            [(bins_address_max-1, bins_address_max-1)]

        self.cp_address = CoverPoint(
            name="transfer.address",
            xf=lambda x: x.address,
            rel=lambda v, b: b[0] <= v < b[1],
            bins=bins_address,
            bins_labels=[f"0x{a[0]:x}-0x{a[1]:x}" for a in bins_address],
        )

        # Security
        if self.vif.RME_SUPPORT:
            bins_security = list(Security)
        else:
            bins_security = [Security.NONSEC, Security.SEC]

        self.cp_security = CoverPoint(
            name="transfer.security",
            xf=lambda x: x.protection.security,
            bins=bins_security,
            bins_labels=[s.name for s in bins_security]
        )

        # Privilege
        self.cp_privilege = CoverPoint(
            name="transfer.privilege",
            xf=lambda x: x.protection.privilege,
            bins=list(Privilege),
            bins_labels=[p.name for p in Privilege]
        )

        # Transaction
        self.cp_transaction = CoverPoint(
            name="transfer.transaction",
            xf=lambda x: x.protection.transaction,
            bins=list(Transaction),
            bins_labels=[t.name for t in Transaction]
        )

        # Direction
        self.cp_direction = CoverPoint(
            name="transfer.direction",
            xf=lambda x: x.direction,
            bins=list(Direction),
            bins_labels=[d.name for d in Direction],
        )

        # Data
        # Power-of-two coverage pattern, where each bit needs to be the leftmost '1'
        bins_data = list(range(self.vif.DATA_WIDTH+1))
        self.cp_data = CoverPoint(
            name="transfer.data",
            xf=lambda x: x.data,
            bins=bins_data,
            bins_labels=[f"leftmost_i{d}" if d else 0 for d in bins_data],
            rel=lambda v, b: b == int(floor(log2(v))) + 1 if v else b == v
        )

        # Strobe
        bins_strobe_max = 2**(self.vif.DATA_WIDTH // 8)
        self.cp_strobe = CoverPoint(
            name="transfer.strobe",
            # Note: sampling condition is included in the transformation
            xf=lambda x: x.strobe if x.direction == Direction.WRITE else -1,
            bins=list(range(bins_strobe_max)),
        )

        # Cross: Address x Direction
        self.cross_address_x_direction = CoverCross(
            "transfer.address_x_direction",
            items=["transfer.address", "transfer.direction"],
        )

        # Cross: Protection
        self.cross_security_x_privilege_x_transaction = CoverCross(
            "transfer.security_x_privilege_x_transaction",
            items=["transfer.security", "transfer.privilege", "transfer.transaction"]
        )

        # Cross: Direction x Protection
        self.cross_direction_x_protection = CoverCross(
            name="transfer.direction_x_protection",
            items=["transfer.direction", "transfer.security_x_privilege_x_transaction"]
        )

        # Cross: Direction x Data
        self.cross_direction_x_data = CoverCross(
            name="transfer.direction_x_data",
            items=["transfer.direction", "transfer.data"]
        )

        self.transfer_coverage = coverage_section(
            self.cp_address,
            self.cp_security,
            self.cp_privilege,
            self.cp_transaction,
            self.cp_direction,
            self.cp_strobe,
            self.cp_data,
            self.cross_address_x_direction,
            self.cross_security_x_privilege_x_transaction,
            self.cross_direction_x_protection,
            self.cross_direction_x_data
        )

class Apb5CoverageCollector(uvm_subscriber):

    def __init__(self, name="coverage_collector", parent=None):
        super().__init__(name, parent)

    def build_phase(self):
        vif = ConfigDB().get(None, self.get_full_name(), "vif")
        assert isinstance(vif, Apb5Interface)
        self.transfer_coverage = Apb5TransferCoverage(vif)

    def write(self, transfer: Apb5Transfer):
        # Note: to allow using instance variables in CoverPoint definitions
        @self.transfer_coverage.transfer_coverage
        def sample(transfer):
            pass
        sample(transfer)

    def report_phase(self):
        coverage_db.export_to_yaml()
