filename = ./src/top
buildname = ./build/top
pcf_file = ../common/iceBlinkPico.pcf

build:
	yosys -p "synth_ice40 -top top -json $(filename).json" src/$(filename).sv
	nextpnr-ice40 --up5k --package sg48 --json $(filename).json --pcf $(pcf_file) --asc $(filename).asc
	icepack $(filename).asc $(filename).bin

prog: #for sram
	dfu-util --alt 0 -D $(filename).bin -R

clean:
	rm -rf $(buildname).blif $(buildname).asc $(buildname).json $(buildname).bin $(buildname).vvp

sim:
	iverilog -g2012 -o $(buildname).vvp -c top.f $(filename)_tb.sv
	vvp $(buildname).vvp
	gtkwave $(buildname).vcd build/wavegen.gtkw

flash: build prog
