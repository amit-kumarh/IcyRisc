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
# blinky.c:7:   *LED_PTR = 255;
	li	a5,-1		# _1,
# blinky.c:7:   *LED_PTR = 255;
	li	a4,-1		# tmp146,
	sb	a4,0(a5)	# tmp146, *_1
.L5:
# blinky.c:9:     target = *MICROS_PTR + BLINK_TIME;
	li	a5,-12		# _2,
	lw	a5,0(a5)		# _3, *_2
# blinky.c:9:     target = *MICROS_PTR + BLINK_TIME;
	addi	a5,a5,10	#, _4, _3
# blinky.c:9:     target = *MICROS_PTR + BLINK_TIME;
	sw	a5,-20(s0)	# _4, target
# blinky.c:10:     while (*MICROS_PTR < target) {
	nop	
.L2:
# blinky.c:10:     while (*MICROS_PTR < target) {
	li	a5,-12		# _5,
	lw	a4,0(a5)		# _6, *_5
# blinky.c:10:     while (*MICROS_PTR < target) {
	lw	a5,-20(s0)		# target.0_7, target
	bltu	a4,a5,.L2	#, _6, target.0_7,
# blinky.c:12:     *LED_PTR = *LED_PTR == 0 ? 255 : 0;
	li	a5,-1		# _8,
	lbu	a5,0(a5)	# tmp148, *_8
	andi	a5,a5,0xff	# _9, tmp147
# blinky.c:12:     *LED_PTR = *LED_PTR == 0 ? 255 : 0;
	bne	a5,zero,.L3	#, _9,,
# blinky.c:12:     *LED_PTR = *LED_PTR == 0 ? 255 : 0;
	li	a5,255		# iftmp.1_11,
	j	.L4		#
.L3:
# blinky.c:12:     *LED_PTR = *LED_PTR == 0 ? 255 : 0;
	li	a5,0		# iftmp.1_11,
.L4:
# blinky.c:12:     *LED_PTR = *LED_PTR == 0 ? 255 : 0;
	li	a4,-1		# _10,
# blinky.c:12:     *LED_PTR = *LED_PTR == 0 ? 255 : 0;
	sb	a5,0(a4)	# iftmp.1_11, *_10
# blinky.c:9:     target = *MICROS_PTR + BLINK_TIME;
	j	.L5		#
	.size	main, .-main
	.ident	"GCC: (xPack GNU RISC-V Embedded GCC x86_64) 14.2.0"
	.section	.note.GNU-stack,"",@progbits
