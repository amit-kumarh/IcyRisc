`timescale 10ns / 10ps

module top_tb;
  logic clk = 0;
  logic SW, RGB_R, RGB_G, RGB_B, LED;

  top u0 (
      .clk(clk),
      .SW(SW),
      .RGB_R(RGB_R),
      .RGB_G(RGB_G),
      .RGB_B(RGB_B),
      .LED(LED)
  );

  always begin
    #4 clk = ~clk;
  end

  initial begin
    $dumpfile("build/top.vcd");
    $dumpvars(0, top_tb);
    SW = 0;
    #8 SW = 1;
    #30000 $finish;
  end

endmodule
