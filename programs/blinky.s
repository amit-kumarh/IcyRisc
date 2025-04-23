	.file	"blinky.c"
	.option nopic
	.attribute arch, "rv32i2p1"
	.attribute unaligned_access, 0
	.attribute stack_align, 16
# GNU C17 (xPack GNU RISC-V Embedded GCC x86_64) version 14.2.0 (riscv-none-elf)
#	compiled by GNU C version 13.2.0, GMP version 6.3.0, MPFR version 4.2.1, MPC version 1.3.1, isl version isl-0.26-GMP

# GGC heuristics: --param ggc-min-expand=100 --param ggc-min-heapsize=131072
# options passed: -mabi=ilp32 -misa-spec=20191213 -march=rv32i
	.text
	.align	2
	.globl	main
	.type	main, @function
main:
	addi	sp,sp,-32	#,,
	sw	ra,28(sp)	#,
	sw	s0,24(sp)	#,
	addi	s0,sp,32	#,,
# blinky.c:4:   int *led_addr = (int *)0xFFFFFFFF;
	li	a5,-1		# tmp140,
	sw	a5,-20(s0)	# tmp140, led_addr
# blinky.c:5:   int *millis_addr = (int *)0xFFFFFFF4;
	li	a5,-12		# tmp141,
	sw	a5,-24(s0)	# tmp141, millis_addr
# blinky.c:7:   *led_addr = 1;
	lw	a5,-20(s0)		# tmp142, led_addr
	li	a4,1		# tmp143,
	sw	a4,0(a5)	# tmp143, *led_addr_7
.L3:
# blinky.c:9:     target = *millis_addr + BLINK_TIME;
	lw	a5,-24(s0)		# tmp144, millis_addr
	lw	a5,0(a5)		# _1, *millis_addr_8
# blinky.c:9:     target = *millis_addr + BLINK_TIME;
	addi	a5,a5,10	#, target_11, _1
	sw	a5,-28(s0)	# target_11, target
# blinky.c:10:     while (*millis_addr < target) {
	nop	
.L2:
# blinky.c:10:     while (*millis_addr < target) {
	lw	a5,-24(s0)		# tmp146, millis_addr
	lw	a5,0(a5)		# _2, *millis_addr_8
# blinky.c:10:     while (*millis_addr < target) {
	lw	a4,-28(s0)		# tmp147, target
	bgt	a4,a5,.L2	#, tmp147, _2,
# blinky.c:12:     *led_addr = !(*led_addr);
	lw	a5,-20(s0)		# tmp148, led_addr
	lw	a5,0(a5)		# _3, *led_addr_7
# blinky.c:12:     *led_addr = !(*led_addr);
	seqz	a5,a5	# tmp150, _3
	andi	a5,a5,0xff	# _4, _4
	mv	a4,a5	# _5, _4
# blinky.c:12:     *led_addr = !(*led_addr);
	lw	a5,-20(s0)		# tmp151, led_addr
	sw	a4,0(a5)	# _5, *led_addr_7
# blinky.c:9:     target = *millis_addr + BLINK_TIME;
	j	.L3		#
	.size	main, .-main
	.ident	"GCC: (xPack GNU RISC-V Embedded GCC x86_64) 14.2.0"
	.section	.note.GNU-stack,"",@progbits
