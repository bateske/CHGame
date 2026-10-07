/* SPDX-License-Identifier: GPL-3.0-or-later */
#include <Arduino.h>
#include <stdint.h>
extern "C" uint8_t _susrstack, _eusrstack;
extern "C" void transfer_stack_init(){
 uintptr_t sp;noInterrupts();asm volatile("mv %0, sp":"=r"(sp));
 uintptr_t top=sp>128?sp-128:0;for(volatile uint8_t *p=&_susrstack;(uintptr_t)p<top&&p<&_eusrstack;p++)*p=0xa5;
 interrupts();
}
extern "C" uint16_t transfer_stack_free(){volatile uint8_t *p=&_susrstack;while(p<&_eusrstack&&*p==0xa5)p++;return (uint16_t)(p-&_susrstack);}
extern "C" uint16_t transfer_stack_size(){return (uint16_t)(&_eusrstack-&_susrstack);}
