from typing import Any, Callable


class Apb5Interface():

    def __init__(self,
                 clock,
                 resetn) -> None:

        # Properties
        self.ADDR_WIDTH: Any = None
        self.DATA_WIDTH: Any = None
        self.RME_SUPPORT: Any = None
        self.WAKEUP_SUPPORT: Any = None
        self.USER_REQ_WIDTH: Any = None
        self.USER_DATA_WIDTH: Any = None
        self.USER_RESP_WIDTH: Any = None

        # Signals
        self.pclk = clock
        self.presetn = resetn
        self.pwakeup: Any = None
        self.psel: Any = None
        self.penable: Any = None
        self.paddr: Any = None
        self.pwrite: Any = None
        self.pwdata: Any = None
        self.pstrb: Any = None
        self.pprot: Any = None
        self.pnse: Any = None
        self.prdata: Any = None
        self.pslverr: Any = None
        self.pready: Any = None
        self.pauser: Any = None
        self.pwuser: Any = None
        self.pruser: Any = None
        self.pbuser: Any = None

    def get_value(self,
                  signal: str,
                  type_: Callable = int) -> Any:
        return type_(self.__getattribute__(signal).value)


class Apb5RequesterInterface(Apb5Interface):

    pass


class Apb5CompleterInterface(Apb5Interface):

    pass
