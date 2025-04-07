filename = top
pcf_file = ../common/iceBlinkPico.pcf

build:
	yosys -p "synth_ice40 -top top -json $(filename).json" src/$(filename).sv
	nextpnr-ice40 --up5k --package sg48 --json $(filename).json --pcf $(pcf_file) --asc $(filename).asc
	icepack $(filename).asc $(filename).bin

prog: #for sram
	dfu-util --alt 0 -D $(filename).bin -R

clean:
	rm -rf $(filename).blif $(filename).asc $(filename).json $(filename).bin $(filename).vvp

sim:
	iverilog -g2012 -o $(filename).vvp $(filename)_tb.sv
	vvp $(filename).vvp
	gtkwave $(filename).vcd wavegen.gtkw

flash: build prog
