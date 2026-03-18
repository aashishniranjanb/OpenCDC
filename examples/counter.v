// Two-clock-domain counter — CDC test design for OpenCDC
module dual_clock_counter (
    input  clk_fast,   // 100 MHz domain
    input  clk_slow,   // 25 MHz domain
    input  rst_n,
    output reg [3:0] count_fast,
    output reg [3:0] count_slow
);
    // Fast domain counter
    always @(posedge clk_fast or negedge rst_n) begin
        if (!rst_n) count_fast <= 4'b0;
        else        count_fast <= count_fast + 1;
    end

    // Slow domain reads fast counter — INTENTIONAL CDC VIOLATION
    always @(posedge clk_slow or negedge rst_n) begin
        if (!rst_n) count_slow <= 4'b0;
        else        count_slow <= count_fast; // <-- no synchronizer!
    end
endmodule
