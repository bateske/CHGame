/**
 *******************************************************************************
 * Copyright (c) 2021 Nanjing Qinheng Microelectronics Co., Ltd.
 * All rights reserved.
 *
 * This software component is licensed by WCH under BSD 3-Clause license,
 * the "License"; You may not use this file except in compliance with the
 * License. You may obtain a copy of the License at:
 *                        opensource.org/licenses/BSD-3-Clause
 *
 *******************************************************************************
 */

#include "Arduino.h"
#include "PeripheralPins.h"

/* =====
 * Notes:
 * - The pins mentioned Px_y_ALTz are alternative possibilities which use other
 *   HW peripheral instances. You can use them the same way as any other "normal"
 *   pin (i.e. analogWrite(PA7_ALT1, 128);).
 *
 * - Commented lines are alternative possibilities which are not used per default.
 *   If you change them, you will have to know what you do
 * =====
 */

//*** ADC ***
#ifdef ADC_MODULE_ENABLED
WEAK const PinMap PinMap_ADC[] = {
  {PA_0,      ADC1, CH_PIN_DATA_EXT(CH_MODE_INPUT, CH_CNF_INPUT_ANALOG, 0, AFIO_NONE, 0)}, // ADC1_IN0
  {PA_1,      ADC1, CH_PIN_DATA_EXT(CH_MODE_INPUT, CH_CNF_INPUT_ANALOG, 0, AFIO_NONE, 1)}, // ADC1_IN1
  {PA_2,      ADC1, CH_PIN_DATA_EXT(CH_MODE_INPUT, CH_CNF_INPUT_ANALOG, 0, AFIO_NONE, 2)}, // ADC1_IN2
  {PA_3,      ADC1, CH_PIN_DATA_EXT(CH_MODE_INPUT, CH_CNF_INPUT_ANALOG, 0, AFIO_NONE, 3)}, // ADC1_IN3
  {PA_4,      ADC1, CH_PIN_DATA_EXT(CH_MODE_INPUT, CH_CNF_INPUT_ANALOG, 0, AFIO_NONE, 4)}, // ADC1_IN4
  {PA_5,      ADC1, CH_PIN_DATA_EXT(CH_MODE_INPUT, CH_CNF_INPUT_ANALOG, 0, AFIO_NONE, 5)}, // ADC1_IN5
  {PA_6,      ADC1, CH_PIN_DATA_EXT(CH_MODE_INPUT, CH_CNF_INPUT_ANALOG, 0, AFIO_NONE, 6)}, // ADC1_IN6
  {PA_7,      ADC1, CH_PIN_DATA_EXT(CH_MODE_INPUT, CH_CNF_INPUT_ANALOG, 0, AFIO_NONE, 7)}, // ADC1_IN7
  {PB_0,      ADC1, CH_PIN_DATA_EXT(CH_MODE_INPUT, CH_CNF_INPUT_ANALOG, 0, AFIO_NONE, 8)}, // ADC1_IN8
  {PB_1,      ADC1, CH_PIN_DATA_EXT(CH_MODE_INPUT, CH_CNF_INPUT_ANALOG, 0, AFIO_NONE, 9)}, // ADC1_IN9
  {PC_0,      ADC1, CH_PIN_DATA_EXT(CH_MODE_INPUT, CH_CNF_INPUT_ANALOG, 0, AFIO_NONE, 10)}, // ADC1_IN8
  {PC_3,      ADC1, CH_PIN_DATA_EXT(CH_MODE_INPUT, CH_CNF_INPUT_ANALOG, 0, AFIO_NONE, 13)}, // ADC1_IN9
  {NC,        NP,   0}
};
#endif

//*** No DAC ***



//*** I2C ***
/* CHGAME Rev1: I2C1 remap 3 only (SDA PC18, SCL PC19, CN2). The other
 * remaps put it on USB D+/D- (PC16/PC17). */
#ifdef I2C_MODULE_ENABLED
WEAK const PinMap PinMap_I2C_SDA[] = {
  {PC_18, I2C1, CH_PIN_DATA(CH_MODE_OUTPUT_50MHz, CH_CNF_OUTPUT_AFOD, NOPULL, AFIO_PartialRemap3_I2C1_ENABLE)}, // CN2 SDA
  {NC,   NP,   0}
};
#endif

#ifdef I2C_MODULE_ENABLED
WEAK const PinMap PinMap_I2C_SCL[] = {
  {PC_19, I2C1, CH_PIN_DATA(CH_MODE_OUTPUT_50MHz, CH_CNF_OUTPUT_AFOD, NOPULL, AFIO_PartialRemap3_I2C1_ENABLE)}, // CN2 SCL
  {NC,   NP,   0}
};
#endif

//*** TIM ***
/* CHGAME Rev1: only the three channels the board wires up, all at remap 000
 * (RM, AFIO_PCFR1: TIM1_RM[17:15] 000 = CH1 PB9, CH2 PB10; TIM2_RM[20:18]
 * 000 = CH2 PA1). Every other channel of TIM1/TIM2/TIM3 lands on a button,
 * the display or the card, USB, PA0, CN2/CN3 or a CC pin, and TIM1's
 * complementary outputs (PB6-PB8 at remap 000) and break input (PB5 = DOWN)
 * must never be enabled, so there are no N rows and no other remaps.
 *
 * TIM1's rows force remap 000: AFIO_Remap_TIM1_DISABLE clears exactly
 * PCFR1[17:15]. TIM2's row is AFIO_NONE on purpose: the SDK's
 * GPIO_PinRemapConfig(GPIO_FullRemap_TIM2, DISABLE) behind
 * AFIO_Remap_TIM2_DISABLE clears PCFR1[18:16] instead of [20:18] (it would
 * change TIM1_RM[2:1] and leave TIM2_RM[2:1]). TIM2_RM is 000 from reset,
 * nothing in the core changes it, and the CHGame library's audio clears it
 * with a masked write. */
#ifdef TIM_MODULE_ENABLED
WEAK const PinMap PinMap_TIM[] = {
  {PB_9,       TIM1, CH_PIN_DATA_EXT(CH_MODE_OUTPUT_50MHz, CH_CNF_OUTPUT_AFPP, NOPULL, AFIO_Remap_TIM1_DISABLE, 1)}, // TIM1_CH1: backlight
  {PB_10,      TIM1, CH_PIN_DATA_EXT(CH_MODE_OUTPUT_50MHz, CH_CNF_OUTPUT_AFPP, NOPULL, AFIO_Remap_TIM1_DISABLE, 2)}, // TIM1_CH2: LED
  {PA_1,       TIM2, CH_PIN_DATA_EXT(CH_MODE_OUTPUT_50MHz, CH_CNF_OUTPUT_AFPP, NOPULL, AFIO_NONE, 2)},               // TIM2_CH2: buzzer
  {NC,         NP,   0}
};
#endif

//*** UART ***
/* CHGAME Rev1: USART2 at remap 000 on CN3 only. USART1 (PB10/PB11) is the
 * LED and A, USART3 (PB3/PB4) SD CS and LCD DC, USART4 (PB0/PB1) UP and DOWN,
 * and USART2's own RTS/CTS (PA1/PA0) are the buzzer and VBUS sense: no
 * hardware flow control. */
#ifdef UART_MODULE_ENABLED
WEAK const PinMap PinMap_UART_TX[] = {
  {PA_2,  USART2, CH_PIN_DATA(CH_MODE_OUTPUT_50MHz, CH_CNF_OUTPUT_AFPP, 0, AFIO_NONE)},   // CN3 TX
  {NC,   NP,     0}
};
#endif

#ifdef UART_MODULE_ENABLED
WEAK const PinMap PinMap_UART_RX[] = {
  {PA_3,  USART2, CH_PIN_DATA(CH_MODE_INPUT, CH_CNF_INPUT_PUPD, PULLUP, AFIO_NONE)},     // CN3 RX
  {NC,    NP,     0}
};
#endif

#ifdef UART_MODULE_ENABLED
WEAK const PinMap PinMap_UART_RTS[] = {
  {NC,    NP,     0}
};
#endif

#ifdef UART_MODULE_ENABLED
WEAK const PinMap PinMap_UART_CTS[] = {
  {NC,    NP,     0}
};
#endif


//*** SPI ***
#ifdef SPI_MODULE_ENABLED
WEAK const PinMap PinMap_SPI_MOSI[] = {
  {PA_7, SPI1, CH_PIN_DATA(CH_MODE_OUTPUT_50MHz, CH_CNF_OUTPUT_AFPP, 0, AFIO_NONE)},
  {NC,   NP,   0}
};
#endif

#ifdef SPI_MODULE_ENABLED
WEAK const PinMap PinMap_SPI_MISO[] = {
  {PA_6, SPI1, CH_PIN_DATA(CH_MODE_INPUT, CH_CNF_INPUT_FLOAT, 0, AFIO_NONE)},
  {NC,   NP,   0}
};
#endif

#ifdef SPI_MODULE_ENABLED
WEAK const PinMap PinMap_SPI_SCLK[] = {
  {PA_5, SPI1, CH_PIN_DATA(CH_MODE_OUTPUT_50MHz, CH_CNF_OUTPUT_AFPP, 0, AFIO_NONE)},
  {NC,   NP,   0}
};
#endif

#ifdef SPI_MODULE_ENABLED
WEAK const PinMap PinMap_SPI_SSEL[] = {
  {PA_4,  SPI1, CH_PIN_DATA(CH_MODE_OUTPUT_50MHz, CH_CNF_OUTPUT_AFPP, 0, AFIO_NONE)},
  {NC,    NP,   0}
};
#endif

//*** NO CAN ***
#ifdef CAN_MODULE_ENABLED

#endif

#ifdef CAN_MODULE_ENABLED 

#endif

//*** No ETHERNET ***



//*** USB ***
#ifdef USB_MODULE_ENABLED
WEAK const PinMap PinMap_USB[] = {
  {PC_16, USB, CH_PIN_DATA(CH_MODE_INPUT, GPIO_NOPULL, AFIO_NONE)}, // USB_DM
  {PC_17, USB, CH_PIN_DATA(CH_MODE_INPUT, GPIO_NOPULL, AFIO_NONE)}, // USB_DP
  {NC,    NP,  0}
};
#endif

//*** No SD ***


