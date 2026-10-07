/* SPDX-License-Identifier: GPL-3.0-or-later
 * CDC-only CHSDtoUSB browser build. Bounded, one-file transactions.
 * The journal protects file replacement, not the FAT volume against power loss.
 */
#include "transfer.h"
#include "ff.h"
#include "diskio.h"
#include <string.h>
#define STAGE "_CHWEB/NEW.TMP"
#define OLD "_CHWEB/OLD.BAK"
#define JOURNAL "_CHWEB/TXN.DAT"
#define BAD 32
#define BUSY 33
#define CHECKSUM 34
#define RECOVERY 35
__attribute__((weak)) void transfer_ui_poll(void){}
__attribute__((weak)) uint16_t transfer_stack_free(void){return 0;}
__attribute__((weak)) uint16_t transfer_stack_size(void){return 0;}
static FATFS fs;
static FIL staged,inspector;
static uint8_t inspect_active;
static char inspect_path[121];
static uint8_t check_buffer[512];
static uint8_t active,recovered,ready;
static uint32_t expected_size,expected_crc,offset;
static char target[121];
static uint8_t block[512];
static uint32_t get32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void put32(uint8_t *p,uint32_t v){for(int i=0;i<4;i++){p[i]=v;v>>=8;}}
static const uint32_t crc_nibble[16]={0,0x1db71064,0x3b6e20c8,0x26d930ac,0x76dc4190,0x6b6b51f4,0x4db26158,0x5005713c,0xedb88320,0xf00f9344,0xd6d6a3e8,0xcb61b38c,0x9b64c2b0,0x86d3d2d4,0xa00ae278,0xbdbdf21c};
uint32_t transfer_crc(uint32_t c,const uint8_t *p,size_t n){while(n--){c^=*p++;c=(c>>4)^crc_nibble[c&15];c=(c>>4)^crc_nibble[c&15];}return c;}
static int exists(const char *p){FILINFO f;return f_stat(p,&f)==FR_OK;}
static uint8_t syncdisk(void){return disk_ioctl(0,CTRL_SYNC,0)==RES_OK?0:FR_DISK_ERR;}
static uint8_t remove_if_present(const char *p){FRESULT r=f_unlink(p);return r==FR_NO_FILE?0:r;}
static uint8_t inspect(const char *p,uint32_t *size,uint32_t *crc,uint8_t *title){
 FIL f;UINT n;FRESULT r=f_open(&f,p,FA_READ);if(r)return r;*size=f_size(&f);uint32_t c=0xffffffffu;
 if(title)memset(title,0,32);
 do{r=f_read(&f,block,sizeof block,&n);if(r)break;
  if(title&&f_tell(&f)==512&&n==512&&get32(block)==0x31474843u&&get32(block+508)==(transfer_crc(0xffffffffu,block,508)^0xffffffffu))memcpy(title,block+32,32);
  c=transfer_crc(c,block,n);transfer_ui_poll();
 }while(n);FRESULT close=f_close(&f);*crc=c^0xffffffffu;return r?r:close;
}
static int matches(const char *p,uint32_t size,uint32_t crc){uint32_t s,c;return !inspect(p,&s,&c,0)&&s==size&&c==crc;}
static int validpath(const uint8_t *p,uint16_t n){
 if(n<2||n>121||p[n-1]||!memcmp(p,"_CHWEB",n>6?6:n))return 0;
 unsigned base=0,ext=0,dot=0;for(int i=0;i<n-1;i++){char c=p[i];if(c=='/'){if(!base||(dot&&!ext))return 0;base=ext=dot=0;}
 else if(c=='.'){if(dot||!base)return 0;dot=1;}
 else{if(!c||!((c>='A'&&c<='Z')||(c>='0'&&c<='9')||strchr("!#$%&'()-@^_`{}~",c)))return 0;if(dot){if(++ext>3)return 0;}else if(++base>8)return 0;}}
 return base&&(!dot||ext);
}
static uint8_t cleanup(void){uint8_t r;if((r=remove_if_present(OLD)))return r;if((r=remove_if_present(STAGE)))return r;if((r=remove_if_present(JOURNAL)))return r;return syncdisk();}
static uint8_t recover(void){
 if(!exists(JOURNAL)){if(exists(OLD))return RECOVERY;return remove_if_present(STAGE);}
 uint8_t record[140];FIL f;UINT n;FRESULT r=f_open(&f,JOURNAL,FA_READ);if(r)return r;r=f_read(&f,record,sizeof record,&n);f_close(&f);
 if(r||n!=sizeof record||get32(record)!=0x31575843||record[133]||record[134]||record[135]||get32(record+136)!=(transfer_crc(0xffffffffu,record,136)^0xffffffffu))return RECOVERY;
 if(!validpath(record+12,(uint16_t)(strnlen((char*)record+12,121)+1)))return RECOVERY;
 uint32_t size=get32(record+4),crc=get32(record+8);const char *dest=(char*)record+12;
 if(matches(dest,size,crc)){recovered=1;return cleanup();}
 if(matches(STAGE,size,crc)){
  if(exists(dest)){if(exists(OLD))return RECOVERY;if((r=f_rename(dest,OLD)))return r;}
  if((r=f_rename(STAGE,dest)))return r;if(!matches(dest,size,crc))return CHECKSUM;recovered=1;return cleanup();
 }
 if(exists(OLD)&&!exists(dest)){if((r=f_rename(OLD,dest)))return r;recovered=1;return cleanup();}
 return RECOVERY;
}
uint8_t transfer_init(void){
 active=ready=recovered=inspect_active=0;FRESULT r=f_mount(&fs,"",1);if(r)return r;if(fs.fs_type!=FS_FAT16&&fs.fs_type!=FS_FAT32)return FR_NO_FILESYSTEM;
 r=f_mkdir("_CHWEB");if(r&&r!=FR_EXIST)return r;r=recover();if(!r)ready=1;return r;
}
uint8_t transfer_command(uint8_t cmd,const uint8_t *data,uint16_t len,uint8_t *out,uint16_t *size){
 *size=0;if(!ready)return RECOVERY;FRESULT r;FILINFO info;
 if(cmd!=11&&cmd!=12&&cmd!=15&&inspect_active){f_close(&inspector);inspect_active=0;}
 if(cmd==1){if(len)return BAD;DWORD free;FATFS *volume;r=f_getfree("",&free,&volume);if(r)return r;out[0]=1;out[1]=recovered;put32(out+2,(fs.n_fatent-2)*fs.csize);put32(out+6,free*fs.csize);out[10]=0;out[11]=2;out[12]=120;out[13]=0;*size=14;return 0;}
 if(cmd==2){if(!validpath(data,len))return BAD;if((r=f_stat((char*)data,&info)))return r;uint32_t s=0,c=0;out[8]=(info.fattrib&AM_DIR)!=0;memset(out+9,0,32);s=info.fsize;if(!out[8]){FIL f;UINT n;if((r=f_open(&f,(char*)data,FA_READ)))return r;r=f_read(&f,block,512,&n);f_close(&f);if(r)return r;if(n==512&&get32(block)==0x31474843u&&get32(block+508)==(transfer_crc(0xffffffffu,block,508)^0xffffffffu))memcpy(out+9,block+32,32);}put32(out,s);put32(out+4,c);*size=41;return 0;}
 if(cmd==3){if(len<5||!((len==5&&data[4]==0)||validpath(data+4,len-4)))return BAD;DIR dir;if((r=f_opendir(&dir,(char*)data+4)))return r;uint32_t index=get32(data);if(index>4095){f_closedir(&dir);return BAD;}for(uint32_t i=0;i<=index;i++){r=f_readdir(&dir,&info);if(r||!info.fname[0])break;}f_closedir(&dir);if(r)return r;if(!info.fname[0])return 0;put32(out,info.fsize);out[4]=(info.fattrib&AM_DIR)!=0;*size=5+strlen(info.fname);memcpy(out+5,info.fname,*size-5);return 0;}
 if(cmd==11){if(len<10||!validpath(data+8,len-8))return BAD;UINT n;uint32_t pos=get32(data),c=get32(data+4);const char *path=(char*)data+8;
  if(inspect_active&&(strcmp(path,inspect_path)||f_tell(&inspector)!=pos)){f_close(&inspector);inspect_active=0;}
  if(!inspect_active){if((r=f_open(&inspector,path,FA_READ)))return r;strcpy(inspect_path,path);inspect_active=1;if(pos>f_size(&inspector)){f_close(&inspector);inspect_active=0;return BAD;}if((r=f_lseek(&inspector,pos))){f_close(&inspector);inspect_active=0;return r;}}
  r=FR_OK;for(int i=0;i<32&&!r;i++){r=f_read(&inspector,check_buffer,sizeof check_buffer,&n);if(r)break;c=transfer_crc(c,check_buffer,n);transfer_ui_poll();if(n<sizeof check_buffer)break;}
  put32(out,f_tell(&inspector));put32(out+4,c);out[8]=f_eof(&inspector);*size=9;if(r||out[8]){FRESULT close=f_close(&inspector);inspect_active=0;if(!r)r=close;}return r;}
 // CAPS: protocol extension version, read feature bit and bounded data bytes.
 if(cmd==13){if(len)return BAD;out[0]=1;out[1]=15;out[2]=0xe0;out[3]=1;uint16_t spare=transfer_stack_free(),reserved=transfer_stack_size();out[4]=spare;out[5]=spare>>8;out[6]=reserved;out[7]=reserved>>8;*size=8;return 0;}
 // REMOVE is idempotent, non-recursive and restricted to the game collection.
 if(cmd==14){if(active||exists(JOURNAL))return BUSY;if(!validpath(data,len)||len<8||memcmp(data,"GAMES/",6))return BAD;r=f_unlink((const char*)data);if(r==FR_NO_FILE||r==FR_NO_PATH)r=FR_OK;return r?r:syncdisk();}
 // Host supplies aggregate transfer progress; this command never accesses SD.
 if(cmd==15){if(len!=13||data[12]>2||get32(data)>get32(data+4))return BAD;return 0;}
 // READ: offset u32, count u16, NUL-terminated 8.3 path. CRC32 covers data.
 if(cmd==12){if(active)return BUSY;if(len<8||!validpath(data+6,len-6))return BAD;
  uint32_t pos=get32(data);UINT wanted=data[4]|((uint16_t)data[5]<<8),n=0;
  if(!wanted||wanted>480)return BAD;const char *path=(char*)data+6;
  if(inspect_active&&(strcmp(path,inspect_path)||f_tell(&inspector)!=pos)){f_close(&inspector);inspect_active=0;}
  if(!inspect_active){if((r=f_open(&inspector,path,FA_READ)))return r;strcpy(inspect_path,path);inspect_active=1;
   if(pos>f_size(&inspector)){f_close(&inspector);inspect_active=0;return BAD;}
   if((r=f_lseek(&inspector,pos))){f_close(&inspector);inspect_active=0;return r;}}
  r=f_read(&inspector,out+9,wanted,&n);put32(out,pos);put32(out+4,transfer_crc(0xffffffffu,out+9,n)^0xffffffffu);out[8]=f_eof(&inspector);*size=9+n;
  if(r||out[8]){FRESULT close=f_close(&inspector);inspect_active=0;if(!r)r=close;}return r;
 }
 if(cmd==4){if(active)return BUSY;if(!validpath(data,len))return BAD;r=f_mkdir((char*)data);if(r==FR_EXIST){if((r=f_stat((char*)data,&info)))return r;return info.fattrib&AM_DIR?0:FR_EXIST;}return r;}
 if(cmd==5){if(active||exists(JOURNAL))return BUSY;if(len<10||!validpath(data+8,len-8))return BAD;
  expected_size=get32(data);expected_crc=get32(data+4);strcpy(target,(char*)data+8);offset=0;
  if((r=f_stat(target,&info))==FR_OK&&(info.fattrib&(AM_DIR|AM_RDO)))return FR_DENIED;if(r!=FR_OK&&r!=FR_NO_FILE&&r!=FR_NO_PATH)return r;
  DWORD free;FATFS *volume;if((r=f_getfree("",&free,&volume)))return r;if((uint64_t)free*fs.csize*512<(uint64_t)expected_size+2048)return FR_DENIED;
  r=f_open(&staged,STAGE,FA_WRITE|FA_CREATE_ALWAYS);if(!r)active=1;return r;
 }
 if(cmd==6){if(!active||len<5||get32(data)!=offset||len-4>expected_size-offset)return BAD;UINT n;r=f_write(&staged,data+4,len-4,&n);offset+=n;if(r)return r;return n==len-4?0:FR_DENIED;}
 if(cmd==7){if(len||!active||offset!=expected_size)return BAD;r=f_sync(&staged);FRESULT close=f_close(&staged);active=0;if(r||close)return r?r:close;if(!matches(STAGE,expected_size,expected_crc))return CHECKSUM;
  uint8_t record[140]={0};put32(record,0x31575843);put32(record+4,expected_size);put32(record+8,expected_crc);strcpy((char*)record+12,target);put32(record+136,transfer_crc(0xffffffffu,record,136)^0xffffffffu);
  FIL journal;UINT n;if((r=f_open(&journal,JOURNAL,FA_WRITE|FA_CREATE_ALWAYS)))return r;r=f_write(&journal,record,sizeof record,&n);if(!r&&n!=sizeof record)r=FR_DENIED;if(!r)r=f_sync(&journal);close=f_close(&journal);if(r||close)return r?r:close;
  // From here, any failure requires recovery before another command may write.
  ready=0;r=recover();if(!r)ready=1;return r;
 }
 if(cmd==8){if(len)return BAD;if(active){r=f_close(&staged);active=0;if(r)return r;}if(exists(JOURNAL))return RECOVERY;return remove_if_present(STAGE);}
 if(cmd==9||cmd==10){if(len||active)return BUSY;return syncdisk();}
 return BAD;
}
