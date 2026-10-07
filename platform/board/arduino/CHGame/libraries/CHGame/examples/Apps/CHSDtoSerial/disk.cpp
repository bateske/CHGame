/* SPDX-License-Identifier: GPL-3.0-or-later */
#include <Arduino.h>
#include "Sd2Card.h"
extern "C" {
#include "ff.h"
#include "diskio.h"
}
static Sd2Card card;
static DSTATUS state=STA_NOINIT;
extern "C" { uint32_t chweb_error_sector=0; uint8_t chweb_error_code=0,chweb_error_operation=0; }
extern "C" DSTATUS disk_initialize(BYTE drive){if(drive)return STA_NOINIT;state=card.init(SPI_FULL_SPEED,PIN_SD_CS)&&card.crcOn()?0:STA_NOINIT;return state;}
extern "C" DSTATUS disk_status(BYTE drive){return drive?STA_NOINIT:state;}
extern "C" DRESULT disk_read(BYTE drive,BYTE *buf,LBA_t sector,UINT count){
 if(drive||state)return RES_NOTRDY;
 bool opened=false;for(UINT i=0;i<count;i++){bool ok=false;for(int retry=0;retry<4&&!ok;retry++){if(!opened)opened=card.readStart(sector+i);ok=opened&&card.readBlockChecked(buf+512*i);if(!ok){card.readStop();opened=false;}}if(!ok){chweb_error_sector=sector+i;chweb_error_code=card.errorCode();chweb_error_operation=1;return RES_ERROR;}}return card.readStop()?RES_OK:RES_ERROR;
}
extern "C" DRESULT disk_write(BYTE drive,const BYTE *buf,LBA_t sector,UINT count){
 if(drive||state)return RES_NOTRDY;
 // FatFs commonly updates one metadata sector. CMD24 includes busy/status
 // verification and avoids a pre-erase/multi-block transaction for one sector.
 for(UINT i=0;i<count;i++){bool ok=false;for(int retry=0;retry<4&&!ok;retry++)ok=card.writeBlock(sector+i,buf+512*i,true);if(!ok){chweb_error_sector=sector+i;chweb_error_code=card.errorCode();chweb_error_operation=2;return RES_ERROR;}}return RES_OK;
}
extern "C" DRESULT disk_ioctl(BYTE drive,BYTE cmd,void *buf){if(drive||state)return RES_NOTRDY;switch(cmd){case CTRL_SYNC:return RES_OK;case GET_SECTOR_COUNT:*(LBA_t*)buf=card.cardSize();return RES_OK;case GET_BLOCK_SIZE:*(DWORD*)buf=1;return RES_OK;case GET_SECTOR_SIZE:*(WORD*)buf=512;return RES_OK;default:return RES_PARERR;}}
