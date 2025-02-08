module b2b_tb#(
    parameter int ADDR_WIDTH = 8,
    parameter int DATA_WIDTH = 32,
    parameter bit RME_SUPPORT = 1,
    parameter bit WAKEUP_SUPPORT = 1,
    parameter int USER_REQ_WIDTH = 4,
    parameter int USER_DATA_WIDTH = 4,
    parameter int USER_RESP_WIDTH = 4
)();

    output logic PCLK;
    output logic PRESETN;
    inout logic PWAKEUP;
    inout logic PSEL;
    inout logic PENABLE;
    inout logic [ADDR_WIDTH-1:0] PADDR;
    inout logic PWRITE;
    inout logic [DATA_WIDTH-1:0] PWDATA;
    inout logic [DATA_WIDTH/8-1:0] PSTRB;
    inout logic [2:0] PPROT;
    inout logic PNSE;
    inout logic [DATA_WIDTH-1:0] PRDATA;
    inout logic PSLVERR;
    inout logic PREADY;
    inout logic [USER_REQ_WIDTH-1:0] PAUSER;
    inout logic [USER_DATA_WIDTH-1:0] PWUSER;
    inout logic [USER_DATA_WIDTH-1:0] PRUSER;
    inout logic [USER_RESP_WIDTH-1:0] PBUSER;


    assign PNSE = 'b0;

    initial begin
        PCLK = 0;
        PRESETN = 0;
        #20
        PRESETN = 1;
    end

    always begin
        #5 PCLK = ~PCLK;
    end

    initial begin
       $dumpfile("b2b_tb.vcd");
       $dumpvars(0,b2b_tb);
    end

endmodule