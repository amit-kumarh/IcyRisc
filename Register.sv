//register file

module Register #(

)(
    input logic clk,
    input logic [0:31] rs1,
    input logic [0:31] rs2,
    input logic rd_reg,
    input logic rdv,
    input logic wren,
    output logic [0:31] rs1v,
    output logic [0:31] rs2v
)


always_ff @(posedge clk)begin
    

end


endmodule