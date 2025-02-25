module ral_tb#(
    parameter int ADDR_WIDTH = 16,
    parameter int DATA_WIDTH = 32,
    parameter bit RME_SUPPORT = 0,
    parameter bit WAKEUP_SUPPORT = 0,
    parameter int USER_REQ_WIDTH = 0,
    parameter int USER_DATA_WIDTH = 0,
    parameter int USER_RESP_WIDTH = 0
)();

    output logic PCLK;
    output logic PRESETN;
    input logic PSEL;
    input logic PENABLE;
    input logic [ADDR_WIDTH-1:0] PADDR;
    input logic PWRITE;
    input logic [DATA_WIDTH-1:0] PWDATA;
    input logic [DATA_WIDTH/8-1:0] PSTRB;
    input logic [2:0] PPROT;
    output logic [DATA_WIDTH-1:0] PRDATA;
    output logic PSLVERR;
    output logic PREADY;

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
       $dumpfile("ral_tb.vcd");
       $dumpvars(0,ral_tb);
    end

    regbank#(
        .DATA_WIDTH(DATA_WIDTH)
    ) u_regbank(
        .pclk(PCLK),
        .presetn(PRESETN),
        .psel(PSEL),
        .penable(PENABLE),
        .pwrite(PWRITE),
        .paddr(PADDR[7:0]),
        .pwdata(PWDATA),
        .prdata(PRDATA),
        .pslverr(PSLVERR),
        .pready(PREADY)
    );

endmodule