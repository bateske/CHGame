/*
  EEPROM - Enables reading and writing to non-volatile storage in the processor.
  
  Uses the Option bytes area in Flash to emulate EEPROM.
  On the CH32V003 there are 2+24 bytes available. 
  The first two bytes are Option bytes data0 and data1.
  All bytes are copied to a 26-byte long byte array in RAM.
  After changing a value the commit() method is used to write flash.

  Ported by Maxint R&D to CH32, based on multiple sources.
  Tested on CH32V003 using Arduino IDE 2.3.2 and OpenWCH core 1.0.4. 
  Includes code from Option Data example of CH32V003fun by CNLOHR.
  Arduino original copyright (c) 2006 David A. Mellis.  All right reserved.
  ESP8266 version copyright (c) 2014 Ivan Grokhotkov. All rights reserved.
  
  This library is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 2.1 of the License, or (at your option) any later version.

  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public
  License along with this library; if not, write to the Free Software
  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/

/**
 * @file
 * @brief Arduino's EEPROM API, emulated in 26 bytes of the chip's option-byte
 * area (written for the CH32V003).
 */

/**
 * @defgroup core_eeprom EEPROM
 * @ingroup lib_core
 * @brief The Arduino EEPROM API over the option-byte area, for the
 * CH32V003. **On the CHGame board (CH32X035) it does not save:** commit()
 * writes nothing and returns `false`.
 *
 * @note **Saving on the CHGame board?** Use the CHGame library's
 * @ref chgame_save "save::" functions: a CRC-checked record of up to 244
 * bytes in the top two pages of the application flash, shared by every game
 * (each tells its records apart by its own magic), which survives power
 * cuts and re-uploads.
 *
 * What the library does on the chip it was written for, the CH32V003:
 *
 * - **26 bytes**, copied into a buffer on the heap by begin(). Bytes 0 and 1
 *   are the user option bytes `Data0` and `Data1`; bytes 2-25 are kept as
 *   half-words (each value with its inverse) at 0x1FFFF810-0x1FFFF83F,
 *   after the 16 bytes of the option-byte block (`OB_BASE`, 0x1FFFF800).
 * - read(), write(), get(), put(), erase() and `[]` work on that buffer.
 *   Nothing reaches flash until commit() (or end()).
 * - commit() erases the whole option-byte area, writes back the read
 *   protection (`RDPR`), user (`USER`) and write protection (`WRPR0-3`) words
 *   it copied just before, then `Data0`, `Data1` and every byte that is not
 *   0xFF. It does not check what it wrote.
 *
 * **On the CH32X035** that commit() is switched off, and a sketch that
 * includes this header gets a compiler message saying so. The chip's
 * option-byte block is the 16 bytes alone, and WCH's CH32X035 library
 * programs it only as one fast-programmed page, never a half-word at a
 * time as above. A write that did not take after the erase would leave the
 * chip read-protected (removing that with the factory ISP erases the whole
 * flash, bootloader included) or with its user options changed (on this
 * board they keep PB7, SELECT, from being the reset pin). So on this chip
 * begin() reads `Data0` and `Data1` and sets bytes 2-25 to 0xFF, everything
 * works on the RAM copy as usual, and commit() returns `false` without
 * writing. Nothing survives a reset.
 * @{
 */
#ifndef EEPROM_h
#define EEPROM_h
#include <Arduino.h>

// A message, not a #warning: the board's default "Compiler warnings: None"
// (-w) would hide a warning, and this one matters.
#if defined(CH32X035) && !defined(EEPROM_NO_WARNING)
#pragma message "EEPROM does not save on the CH32X035 (the CHGame board): commit() writes nothing and returns false. Save with the CHGame library's save:: (CHGame.h). Define EEPROM_NO_WARNING to silence this."
#endif

/** @cond */
// Required definitions copied from /system/CH32V00x/SRC/Peripheral/src/ch32v00x_flash.c
/* Flash Control Register bits */
//#define CR_PG_Set                  ((uint32_t)0x00000001)
//#define CR_PG_Reset                ((uint32_t)0xFFFFFFFE)
//#define CR_PER_Set                 ((uint32_t)0x00000002)
//#define CR_PER_Reset               ((uint32_t)0xFFFFFFFD)
//#define CR_MER_Set                 ((uint32_t)0x00000004)
//#define CR_MER_Reset               ((uint32_t)0xFFFFFFFB)
#define CR_OPTPG_Set               ((uint32_t)0x00000010)
#define CR_OPTPG_Reset             ((uint32_t)0xFFFFFFEF)
#define CR_OPTER_Set               ((uint32_t)0x00000020)
#define CR_OPTER_Reset             ((uint32_t)0xFFFFFFDF)
#define CR_STRT_Set                ((uint32_t)0x00000040)
#define CR_LOCK_Set                ((uint32_t)0x00000080)
//#define CR_PAGE_PG                 ((uint32_t)0x00010000)
//#define CR_PAGE_ER                 ((uint32_t)0x00020000)
//#define CR_BUF_LOAD                ((uint32_t)0x00040000)
//#define CR_BUF_RST                 ((uint32_t)0x00080000)

/* FLASH Keys */
//#define RDP_Key                    ((uint16_t)0x00A5)
#define FLASH_KEY1                 ((uint32_t)0x45670123)
#define FLASH_KEY2                 ((uint32_t)0xCDEF89AB)
/** @endcond */


/**
 * @brief 26 bytes of emulated EEPROM in the option-byte area, worked on in a
 * RAM copy and written by commit() (see @ref core_eeprom).
 */
class EEPROMClass {
  public:
    /**
     * @brief Makes the object; nothing is read until begin().
     */
    EEPROMClass(void);
    /**
     * @brief Calls end(), which commits any change.
     */
    ~EEPROMClass(void);

    /**
     * @brief Copies the 26 bytes from the option-byte area into RAM (26 bytes on
     * the heap, allocated the first time). Call it before anything else.
     *
     * On the CH32X035 only bytes 0 and 1 (`Data0`, `Data1`) are read; bytes
     * 2-25 start as 0xFF.
     */
    void begin(void);

    /**
     * @brief The 26-byte RAM copy, to change in place; marks it changed, so the
     * next commit() writes it.
     * @return the copy, or `nullptr` before begin().
     */
    uint8_t * getDataPtr();
    /**
     * @brief The 26-byte RAM copy, read-only.
     * @return the copy, or `nullptr` before begin().
     */
    uint8_t const * getConstDataPtr() const;
    /**
     * @brief Reads the option bytes `Data0` and `Data1` straight from the chip
     * (no begin() needed).
     * @return `Data0`'s half-word in the high 16 bits and `Data1`'s in the low
     *         16; in each, the low byte is the value and the high byte its
     *         inverse.
     */
    uint32_t ReadOptionBytes(void);   // return data0 and data1 option bytes including their inversed values

    /**
     * @brief Reads a byte of the RAM copy.
     * @param idx  0 to 25.
     * @return the byte; 0 if `idx` is out of range or before begin().
     */
    uint8_t read( int const idx );
    /**
     * @brief Changes a byte of the RAM copy; commit() writes it.
     * @param idx  0 to 25; anything else is ignored, as is a call before begin().
     * @param val  the new value.
     */
    void write( int const idx, uint8_t const val);     // requires commit() to make data stick
    /**
     * @brief Sets the 26 bytes of the RAM copy to 0xFF; commit() writes them.
     */
    void erase(void);     // requires commit() to make data stick

    /**
     * @brief Writes the RAM copy to the option-byte area, if anything changed
     * since begin() or the last commit().
     *
     * Erases the whole area and rewrites it (see @ref core_eeprom). On the
     * CH32X035 it writes nothing.
     * @return `true` if nothing had changed, or (CH32V003) once written: what
     *         was written is not checked. `false` on the CH32X035 whenever
     *         there was something to write.
     */
    bool commit(void);
    /**
     * @brief Commits, then forgets the RAM copy (its 26 bytes are not freed);
     * begin() starts again.
     * @return what commit() returned.
     */
    bool end(void);

    /**
     * @brief Copies `sizeof(T)` bytes of the RAM copy into `t`.
     * @tparam T        any plain type or struct.
     * @param address  the first byte, 0 to 26 - `sizeof(T)`.
     * @param t        receives the bytes; left as it was if they would not fit.
     * @return `t`.
     */
    template<typename T> 
    T &get(int const address, T &t) {
      if (address < 0 || address + sizeof(T) > _size)
        return t;
      memcpy((uint8_t*) &t, _data + address, sizeof(T));
      return t;
    }

    /**
     * @brief Copies `t` into the RAM copy, if it differs; commit() writes it.
     * @tparam T        any plain type or struct.
     * @param address  the first byte, 0 to 26 - `sizeof(T)`; nothing is stored
     *                 if `t` would not fit.
     * @param t        the value.
     * @return `t`.
     */
    template<typename T> 
    const T &put(int const address, const T &t) {
      if (address < 0 || address + sizeof(T) > _size)
        return t;
      if (memcmp(_data + address, (const uint8_t*)&t, sizeof(T)) != 0) {
        _dirty = true;
        memcpy(_data + address, (const uint8_t*)&t, sizeof(T));
      }
      return t;
    }

    /**
     * @brief The emulated EEPROM's size.
     * @return 26 after begin(), 0 before.
     */
    size_t length() {return _size;}

    /**
     * @brief A byte of the RAM copy, to read or change; marks the copy changed.
     * No range check: call begin() first and keep to 0-25.
     * @param address  0 to 25.
     * @return the byte.
     */
    uint8_t& operator[](int const address) {return getDataPtr()[address];}
    /**
     * @brief A byte of the RAM copy, read-only. No range check.
     * @param address  0 to 25.
     * @return the byte.
     */
    uint8_t const & operator[](int const address) const {return getConstDataPtr()[address];}

  protected:
    /** @brief The RAM copy (26 bytes after begin()). */
    uint8_t* _data = nullptr;
    /** @brief Whether the copy changed since begin() or the last commit(). */
    bool _dirty = false;
    /** @brief The copy's size: 26 after begin(), else 0. */
    size_t _size = 0;
};

#if !defined(NO_GLOBAL_INSTANCES) && !defined(NO_GLOBAL_EEPROM)
/**
 * @brief The emulated EEPROM. Call `EEPROM.begin()` first.
 */
extern EEPROMClass EEPROM;
#endif


/** @} */

#endif		// #ifndef EEPROM_h