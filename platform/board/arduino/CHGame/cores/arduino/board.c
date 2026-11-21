#include "board.h"

#ifdef __cplusplus
extern "C" {
#endif


#if defined(ARDUINO_CHGAME_REV1)
extern volatile uint32_t CFGHR_tmpB;    /* GPIOB CFGHR is write-only: its shadow */
#endif

WEAK void pre_init(void)
{
#if defined(ARDUINO_CHGAME_REV1)
  /* The backlight (PB9) dark from the first instruction of the sketch:
     driven low, not left a floating input, until the panel shows a defined
     picture (CHGfx's gfx_begin() lights it after its first black frame).
     R20's pull-down alone does not hold it off, and the panel's RAM holds
     noise after power-up, which showed for the moment between the reset and
     gfx_begin() (longer in a sketch that does more first). Level, then mode. */
  RCC->APB2PCENR |= RCC_APB2Periph_GPIOB;
  GPIOB->BCR = 1u << 9;
  CFGHR_tmpB = (CFGHR_tmpB & ~0xF0u) | 0x30u;   /* PB9: push-pull output */
  GPIOB->CFGHR = CFGHR_tmpB;
#endif
  hw_config_init();
}


#ifdef __cplusplus
}
#endif
