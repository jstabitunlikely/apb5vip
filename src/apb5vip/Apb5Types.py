import enum


@enum.unique
class Direction(enum.IntEnum):
    READ = 0
    WRITE = 1


@enum.unique
class Response(enum.IntEnum):
    OKAY = 0
    ERROR = 1

@enum.unique
class WakeupMode(enum.IntEnum):
    NEVER = 0
    WITH_SEL = 1
    WITH_ENABLE = 2
    # TODO other modes


@enum.unique
class Privilege(enum.IntEnum):
    NORM = 0
    PRIV = 1


@enum.unique
class Security(enum.IntEnum):
    SEC = 0
    NONSEC = 1
    ROOT = 2
    REALM = 3


@enum.unique
class Transaction(enum.IntEnum):
    DATA = 0
    INST = 1


class ProtectionExt:
    def __init__(self):
        self.security = Security.SEC
        self.privilege = Privilege.NORM
        self.transaction = Transaction.DATA

    def get_pprot(self):
        return (self.transaction << 2) | ((self.security & 1) << 1) | self.privilege

    def get_pnse(self):
        return self.security >> 1

    def __str__(self):
        return f"{self.privilege.name}_{self.security.name}_{self.transaction.name}"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash((
            self.security,
            self.privilege,
            self.transaction
        ))

    def __eq__(self, value: object):
        if not isinstance(value, ProtectionExt):
            return False

        return (
            self.security == value.security and
            self.privilege == value.privilege and
            self.transaction == value.transaction
        )
