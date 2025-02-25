module regbank #(
    parameter ADDR_WIDTH = 8,
    parameter DATA_WIDTH = 32
) (
    input wire pclk,
    input wire presetn,
    input wire psel,
    input wire penable,
    input wire pwrite,
    input wire [ADDR_WIDTH-1:0] paddr,
    input wire [DATA_WIDTH-1:0] pwdata,
    output reg [DATA_WIDTH-1:0] prdata,
    output reg pslverr,
    output reg pready
);

  // Register addresses
  localparam READ_ONLY_ADDR = 8'h00;
  localparam READ_WRITE_ADDR = 8'h04;

  // Internal registers
  reg [DATA_WIDTH-1:0] read_write_reg;
  reg [DATA_WIDTH-1:0] read_only_reg;

  // Read-only register initialization
  initial begin
    read_only_reg = 32'hDEADBEEF;
  end

  // APB5 state machine
  reg state;
  localparam IDLE = 1'b0;
  localparam ACCESS = 1'b1;

  always @(posedge pclk or negedge presetn) begin
    if (~presetn) begin
      state <= IDLE;
      prdata <= '0;
      pslverr <= 1'b0;
      pready <= 1'b0;
    end
    else begin
      if (psel) begin
        if (penable) begin
          state <= IDLE;
          pready <= 1'b1;
          if (pwrite) begin
            // Write access
            case (paddr)
              READ_WRITE_ADDR:
                read_write_reg <= pwdata;
              default:
                pslverr <= 1'b1;
            endcase
          end
          else begin
            // Read access
            case (paddr)
              READ_ONLY_ADDR:
                prdata <= read_only_reg;

              READ_WRITE_ADDR:
                prdata <= read_write_reg;

              default:
                pslverr <= 1'b1;
            endcase
          end
        end
        else begin
          state <= ACCESS;
          pslverr <= 1'b0;
          prdata <= '0;
          pready <= '0;
        end
      end
      else begin
        state <= IDLE;
        pslverr <= 1'b0;
        prdata <= '0;
        pready <= '0;
      end
    end
  end

endmodule