//register file

module Register #(

)(
    input logic clk,
    input logic [4:0] rs1,
    input logic [4:0] rs2,
    input logic [4:0] wd_reg,
    input logic [31:0] rdv,
    input logic wren,
    output logic [31:0] rs1v,
    output logic [31:0] rs2v
)
//define register block
logic [31:0] register_file [32];
register_file [0] = 32'b0;


//write data to wrtie data address when write enable is high (never overwrite r0 is hard 0)
always_ff @(posedge clk)begin
   if(wren) begin
    if(|wd_reg) begin
      register_file [wd_reg] <= rdv;  
   end
   end
end

//read data from the frist read data register

always_ff @(posedge clk)begin
    rs1v <= register_file [rs1]
    rs2v <= register_file [rs2]
end


endmodule