/* SPDX-License-Identifier: GPL-3.0-or-later
 * CHSDtoSerial - the CHGame website's SD card helper.
 *
 * Upload it, plug the handheld in, and https://play.chgame.website reads
 * and writes the microSD card over the board's USB serial port: a browser
 * installs games and menus, backs the card up, and sends the board back to
 * the SD game menu, without the card ever leaving the slot. The protocol is
 * PROTOCOL.md (framed requests and answers with CRCs, journaled file
 * replacement, bounded reads; the browser is the other side). It is
 * CHSDtoUSB's cousin: the same card driver, but the PC talks to files
 * through this sketch instead of mounting the card as a drive, so there are
 * no mass-storage descriptors, no formatting, and the OS never sees the card.
 *
 * The screen is CHSDtoUSB's instrument panel (Agent.h, the "secret agent"
 * look the apps share) in the website's colours: what the website is doing
 * to the card, a graph of the traffic, the files by name, the card's state;
 * while no website has called, a scope sweeps for one, with the website's
 * QR code one key away. Display.h is the whole of the screen's doorway into
 * this file: its calls only watch, and nothing on the screen changes an
 * answer.
 *
 *   A              the website's QR code (while no website is talking);
 *                  any key puts it away
 *   B              cancel: the command in progress finishes, the stage is
 *                  dropped, the card synced, then transfers are refused
 *                  (STOPPED) until the website's next HELLO
 *   START (3 s)    back to the SD game menu, safely (an EXIT? box counts
 *                  down; letting go keeps it running)
 *   LEFT / RIGHT   the panel's page: EVENTS, STATS, CARD
 *   UP / DOWN      scroll the event log
 *
 * This file and transfer.c are the protocol, byte for byte what the website
 * was qualified against: change them only with PROTOCOL.md and the website.
 * The usual CHGame serial port is this sketch's protocol, so there is no
 * debug build for the board (the library's debug protocol would want the
 * same port); it was developed and driven on a PC in the separate SDtoSerial
 * project, and has run on the board as the website's helper.
 *
 * The files:
 *   CHSDtoSerial.ino  the frames, the request cache, the console's cancel
 *   transfer.*        the commands on the card: staging, journal, CRCs
 *   ff.c, ff.h, ffconf.h, diskio.h
 *                     FatFs R0.16 (FAT16/FAT32, short names; its own notice:
 *                     FatFs-LICENSE.txt)
 *   disk.cpp          FatFs's disk over Sd2Card, a sector at a time
 *   Sd2Card.*, SdInfo.h, Sd2PinMap.h
 *                     the SD card over SPI1 with DMA (from sdfatlib: GPL-3.0,
 *                     so this sketch is too)
 *   Memory.cpp        the stack's high-water mark (CAPS reports it)
 *   Display.*         the console: buttons, LED, beeps and the screen
 *   Monitor.*         what the website is doing, from the commands going past
 *   Ui.*              the screen; Qr.h and Shapes.h its tables (tools/)
 *   Agent.*           the secret agent chrome (shared with CHSDtoUSB, CHStlView)
 *   Fx.*, Sounds.*    Sizzle (the banner only) and the beeps
 *   config.h          the version
 */
#include <Arduino.h>
#include "config.h"
#include "transfer.h"
#include "Display.h"
#include <string.h>
static uint8_t rx[520],cached[520],reply[520];
static uint16_t used,cachedSize,replySize;
static uint32_t lastByte,lastId;
static uint8_t initError;
static bool userCancelled;
#ifndef CHWEB_HOST
extern "C" void transfer_stack_init();
#else
static void transfer_stack_init(){}
#endif
extern "C" { extern uint32_t chweb_error_sector; extern uint8_t chweb_error_code,chweb_error_operation; }
static uint16_t crc16(const uint8_t *p,uint16_t n){uint16_t c=0xffff;while(n--){c^=(uint16_t)*p++<<8;for(int i=0;i<8;i++)c=(c<<1)^((c&0x8000)?0x1021:0);}return c;}
static uint32_t get32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void emit(){Serial.write(reply,replySize);Serial.flush();}
static void dispatch(uint16_t n){
 uint32_t id=get32(rx+6);uint8_t cmd=rx[3];
 if(cachedSize&&id==lastId){
  if(cachedSize==n&&!memcmp(cached,rx,n)){if(cmd==1)userCancelled=false;emit();display_link(1,cmd);}
  else{uint8_t error[13]={'C','S',1,(uint8_t)(cmd|128),5,0,0,0,0,0,32,0,0};memcpy(error+6,rx+6,4);uint16_t c=crc16(error+2,9);error[11]=c;error[12]=c>>8;Serial.write(error,sizeof error);Serial.flush();display_link(2,cmd);}
  return;
 }
 uint8_t status=0;uint16_t out=0;
 if(cmd==16){if(n!=12)status=32;else{memcpy(reply+11,"SDtoSerial/1",12);out=12;}display_link(4,cmd);}
 else if(userCancelled&&cmd!=1&&cmd!=8&&cmd!=9&&cmd!=10)status=36;
 else if(cachedSize&&id<lastId&&cmd!=1)status=32;
 else { display_command(cmd,rx+10,n-12); status=initError?initError:transfer_command(cmd,rx+10,n-12,reply+11,&out); display_result(cmd,rx+10,n-12,status,reply+11,out); }
 if(status){out=6;reply[11]=chweb_error_operation;reply[12]=chweb_error_code;memcpy(reply+13,&chweb_error_sector,4);}
 if(cmd==1&&!status)userCancelled=false;
 reply[0]='C';reply[1]='S';reply[2]=1;reply[3]=cmd|128;reply[4]=(out+5)&255;reply[5]=(out+5)>>8;memcpy(reply+6,rx+6,4);reply[10]=status;
 replySize=out+13;uint16_t crc=crc16(reply+2,replySize-4);reply[replySize-2]=crc;reply[replySize-1]=crc>>8;
 memcpy(cached,rx,n);cachedSize=n;lastId=id;emit();
 if(cmd==10&&!status){display_leaving();NVIC_SystemReset();}
}
void setup(){pinMode(PIN_LCD_CS,OUTPUT);digitalWrite(PIN_LCD_CS,HIGH);pinMode(PIN_SD_CS,OUTPUT);digitalWrite(PIN_SD_CS,HIGH);Serial.begin();transfer_stack_init();display_begin();initError=transfer_init();display_card(initError);}
static void controls(){
 const uint8_t action=display_controls();if(!action)return;
 // This boundary is outside every filesystem operation and serial command.
 // COMMIT finishes before cancellation can discard a staging file.
 uint8_t scratch[16];uint16_t size=0;
 uint8_t error=transfer_command(8,0,0,scratch,&size);
 if(!error)error=transfer_command(9,0,0,scratch,&size);
 userCancelled=true;display_controls_done();display_cancelled(action,error);
 if(action&2){delay(50);NVIC_SystemReset();}
}
void loop(){
 controls();
 if(used&&millis()-lastByte>1000)used=0;
 while(Serial.available()){
  uint8_t c=(uint8_t)Serial.read();lastByte=millis();if(used==sizeof rx)used=0;rx[used++]=c;
  while(used>=6){uint16_t len=rx[4]|((uint16_t)rx[5]<<8);
   if(rx[0]!='C'||rx[1]!='S'||rx[2]!=1||len<4||len>512){memmove(rx,rx+1,--used);continue;}
   uint16_t total=len+8;if(used<total)break;
   if(crc16(rx+2,total-4)==(uint16_t)(rx[total-2]|((uint16_t)rx[total-1]<<8)))dispatch(total);else display_link(3,rx[3]);
   controls();
   memmove(rx,rx+total,used-total);used-=total;
  }
 }
}
