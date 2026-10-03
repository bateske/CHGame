/* SysTick_Handler is in the vector table but can never run: the bootloader
 * uses SysTick as a free-running counter with its interrupt disabled.
 * ch32x035_misc.c supplies weak stubs for every other IRQ handler except NMI
 * and HardFault, which are here. */
void SysTick_Handler(void) __attribute__((interrupt("WCH-Interrupt-fast")));
void SysTick_Handler(void) { }

/* A fault in the bootloader stops it where it is; power off and on (B held
 * for USB mode) starts again. The bench reporter that blinked mcause and mepc
 * on the LED went for flash (SIZES.md); git has it, as src/fault.c. */
void NMI_Handler(void)       __attribute__((interrupt("WCH-Interrupt-fast")));
void HardFault_Handler(void) __attribute__((interrupt("WCH-Interrupt-fast")));
void NMI_Handler(void)       { for (;;) { } }
void HardFault_Handler(void) { for (;;) { } }
