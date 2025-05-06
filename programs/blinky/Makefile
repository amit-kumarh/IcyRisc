proj_name = blinky

build:
	riscv-none-elf-gcc -S -fverbose-asm -march=rv32i -nostdlib $(proj_name).c
	riscv-none-elf-gcc -march=rv32i -nostdlib $(proj_name).c -T linker.ld -Xlinker -Map=output.map -o blinky.elf
	riscv-none-elf-gcc -march=rv32i -nostdlib $(proj_name).c -T linker.ld -o blinky.elf
	../elf2hex/bin/riscv-none-elf-elf2hex --bit-width 32 --input $(proj_name).elf --output blinky.txt
	python ../pad_0s.py $(proj_name).txt
	python ../split_memhfile.py $(proj_name).txt

