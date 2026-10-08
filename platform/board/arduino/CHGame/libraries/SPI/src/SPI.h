/*
 * Copyright (c) 2010 by Cristian Maglie <c.maglie@arduino.cc>
 * Copyright (c) 2014 by Paul Stoffregen <paul@pjrc.com> (Transaction API)
 * SPI Master library for arduino.
 *
 * This file is free software; you can redistribute it and/or modify
 * it under the terms of either the GNU General Public License version 2
 * or the GNU Lesser General Public License version 2.1, both as
 * published by the Free Software Foundation.
 * 
 * Modified 30 jurn 2023 by TempersLee to surpport wch's MCU
 */

/**
 * @file
 * @brief Arduino's SPI library (SPIClass, SPISettings), ported to WCH's
 * chips: SPI master on the CH32X035's SPI1.
 */

/**
 * @defgroup core_spi SPI
 * @ingroup lib_core
 * @brief The Arduino SPI API: SPI master on SPI1, the CH32X035's one SPI.
 *
 * @code
 * #include <SPI.h>
 *
 * SPI.begin();
 * SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0));
 * digitalWrite(myCs, LOW);
 * uint8_t answer = SPI.transfer(0x9F);
 * digitalWrite(myCs, HIGH);
 * SPI.endTransaction();
 * @endcode
 *
 * The global @ref SPI is SPI1 on the board's PA5 (SCK), PA6 (MISO) and
 * PA7 (MOSI), the only pins SPI1 has on this chip. Transfers are polled
 * byte by byte (no DMA, no interrupts), and each call gives up after
 * @ref SPI_TRANSFER_TIMEOUT ms. The clock is 48 MHz divided by 2, 4 ...
 * 256: a requested clock gets the fastest of those that does not exceed
 * it (24 MHz down to 187.5 kHz), so the default 4 MHz request runs at
 * 3 MHz.
 *
 * Settings are remembered per chip-select pin, for up to
 * @ref NB_SPI_SETTINGS pins. A transfer for a pin that has none (never given
 * to begin() or beginTransaction(), or forgotten by endTransaction()) does
 * nothing and returns 0.
 *
 * @note On the CHGame board SPI1 is shared by the LCD (CS `PIN_LCD_CS`,
 * PA4, which is also the default `SS`) and the SD card (CS `PIN_SD_CS`,
 * PB11), and CHGfx drives it directly by DMA. Use this class only for a
 * device of your own on SPI1, only between `gfx_wait()` and the next flush,
 * and keep the panel's and the card's CS high. For the card, use
 * @ref lib_chsd "CHSd".
 *
 * @warning begin(), beginTransaction() and a transfer for another CS pin
 * reset SPI1 and program it afresh (clock, mode, bit order), and end()
 * switches SPI1's clock off. CHGfx sets SPI1 up only in `gfx_begin()` and
 * `gfx_setSpiDiv()`, so hand it back before the next flush with
 * `gfx_setSpiDiv(gfx_spiDiv())`, which programs all of SPI1 for the panel
 * again (and switches its clock back on).
 * @{
 */

#ifndef _SPI_H_INCLUDED
#define _SPI_H_INCLUDED

#include "Arduino.h"
#include <stdio.h>
extern "C" {
#include "utility/spi_com.h"
}


/**
 * @brief Defined to 1: this SPI has beginTransaction(), endTransaction(),
 * usingInterrupt() and SPISettings(clock, bitOrder, dataMode).
 */
#define SPI_HAS_TRANSACTION 1

/**
 * @name Clock dividers for setClockDivider() (deprecated)
 * Compatibility with sketches designed for AVR at 16 MHz cannot be ensured,
 * as the SPI clock depends on the system clock: here the divider applies to
 * 48 MHz, and the result is then rounded down to 48 MHz / 2^n. New code
 * passes the clock in Hz to SPISettings with SPI.beginTransaction() instead.
 * @{
 */
#define SPI_CLOCK_DIV2   2      /**< 48 MHz / 2 = 24 MHz */
#define SPI_CLOCK_DIV4   4      /**< 48 MHz / 4 = 12 MHz */
#define SPI_CLOCK_DIV8   8      /**< 48 MHz / 8 = 6 MHz */
#define SPI_CLOCK_DIV16  16     /**< 48 MHz / 16 = 3 MHz */
#define SPI_CLOCK_DIV32  32     /**< 48 MHz / 32 = 1.5 MHz */
#define SPI_CLOCK_DIV64  64     /**< 48 MHz / 64 = 750 kHz */
#define SPI_CLOCK_DIV128 128    /**< 48 MHz / 128 = 375 kHz */
/** @} */

/**
 * @name SPI modes, for SPISettings and setDataMode()
 * @{
 */
#define SPI_MODE0 0x00          /**< clock idles low, data sampled on the rising edge (CPOL 0, CPHA 0) */
#define SPI_MODE1 0x01          /**< clock idles low, data sampled on the falling edge (CPOL 0, CPHA 1) */
#define SPI_MODE2 0x02          /**< clock idles high, data sampled on the falling edge (CPOL 1, CPHA 0) */
#define SPI_MODE3 0x03          /**< clock idles high, data sampled on the rising edge (CPOL 1, CPHA 1) */
/** @} */

/**
 * @name Receive or not, for SPISettings' noRecv
 * @{
 */
#define SPI_TRANSMITRECEIVE 0x0 /**< send and receive (the default) */
#define SPI_TRANSMITONLY 0x1    /**< send only: what comes back is not read, and transfer() returns 0 */
/** @} */

/** @brief What a transfer does with a CS pin the class drives, once it is done. */
enum SPITransferMode {
  SPI_CONTINUE, /**< Transfer not finished: CS pin kept active (low) */
  SPI_LAST      /**< Transfer ended: CS pin released (high) */
};

/**
 * @brief The "CS pin" that means the sketch drives its chip select itself,
 * outside the SPI class (the default for every method).
 */
#define CS_PIN_CONTROLLED_BY_USER  NUM_DIGITAL_PINS

/** @brief Indicates there is no configuration selected (internal). */
#define NO_CONFIG   ((int16_t)(-1))

/**
 * @brief How long one transfer call may take before it gives up, in ms
 * (default 1000). SPI.cpp uses it, so a different value must be defined
 * for the whole build (`build.extra_flags`), not just in the sketch.
 */
#ifndef SPI_TRANSFER_TIMEOUT
  #define SPI_TRANSFER_TIMEOUT 1000
#endif

/**
 * @brief The number of CS pins whose settings an SPIClass remembers, 1 to
 * 254 (default 4). Can be redefined in variant.h.
 */
#ifndef NB_SPI_SETTINGS
  #define NB_SPI_SETTINGS 4
#endif

/**
 * @brief A device's SPI settings: its maximum clock, bit order and mode,
 * for SPIClass::beginTransaction().
 *
 * @code
 * SPI.beginTransaction(SPISettings(8000000, MSBFIRST, SPI_MODE0));  // runs at 6 MHz
 * @endcode
 */
class SPISettings {
  public:
    /**
     * @brief Settings for a device.
     * @param clock     the device's maximum clock in Hz; the bus runs at the
     *                  fastest 48 MHz / 2^n (n = 1..8) that does not exceed
     *                  it, and at 187.5 kHz below that.
     * @param bitOrder  `MSBFIRST` or `LSBFIRST`.
     * @param dataMode  `SPI_MODE0` ... `SPI_MODE3`; any other value means
     *                  `SPI_MODE0`.
     * @param noRecv    `SPI_TRANSMITRECEIVE` (the default) or
     *                  `SPI_TRANSMITONLY`: send only, and do not read what
     *                  comes back.
     */
    constexpr SPISettings(uint32_t clock, BitOrder bitOrder, uint8_t dataMode, bool noRecv = SPI_TRANSMITRECEIVE)
      : pinCS(-1),
        clk(clock),
        bOrder(bitOrder),
        dMode((spi_mode_e)(
                (SPI_MODE0 == dataMode) ? SPI_MODE_0 :
                (SPI_MODE1 == dataMode) ? SPI_MODE_1 :
                (SPI_MODE2 == dataMode) ? SPI_MODE_2 :
                (SPI_MODE3 == dataMode) ? SPI_MODE_3 :
                SPI_MODE0
              )),
        noReceive(noRecv)
    { }
    /**
     * @brief The default settings: 4 MHz requested (3 MHz on the wire),
     * MSB first, `SPI_MODE0`, send and receive.
     */
    constexpr SPISettings()
      : pinCS(-1),
        clk(SPI_SPEED_CLOCK_DEFAULT),
        bOrder(MSBFIRST),
        dMode(SPI_MODE_0),
        noReceive(SPI_TRANSMITRECEIVE)
    { }
  private:
    int16_t pinCS;      //CS pin associated to the configuration
    uint32_t clk;       //specifies the spi bus maximum clock speed
    BitOrder bOrder;    //bit order (MSBFirst or LSBFirst)
    spi_mode_e dMode;   //one of the data mode
    //Mode          Clock Polarity (CPOL)   Clock Phase (CPHA)
    //SPI_MODE0             0                     0
    //SPI_MODE1             0                     1
    //SPI_MODE2             1                     0
    //SPI_MODE3             1                     1
    friend class SPIClass;
    bool noReceive;
};

/**
 * @brief An SPI master: the Arduino SPI API on one of the chip's SPI
 * peripherals (the global @ref SPI on this board).
 *
 * Every method takes an optional CS pin first. Without it (or with
 * @ref CS_PIN_CONTROLLED_BY_USER) the sketch drives its device's chip
 * select itself; with it, the class drives that pin low for the transfer
 * and high after it, and keeps settings for it apart from other pins'.
 */
class SPIClass {
  public:
    /**
     * @brief An SPI on the variant's default pins: `MOSI`, `MISO` and `SCK`
     * (PA7, PA6 and PA5 on this board), with no hardware chip select.
     */
    SPIClass();
    /**
     * @brief An SPI on the given pins, which must all belong to the same SPI
     * peripheral (on the CH32X035 only SPI1's PA7, PA6, PA5 and PA4 do).
     * @param mosi  the MOSI pin (`PA7`).
     * @param miso  the MISO pin (`PA6`).
     * @param sclk  the clock pin (`PA5`).
     * @param ssel  a hardware chip select the peripheral drives itself
     *              (`PA4`, the panel's CS on this board), or
     *              `PNUM_NOT_DEFINED` (the default) for none. With one, do
     *              not pass CS pins to the other methods.
     */
    SPIClass(uint32_t mosi, uint32_t miso, uint32_t sclk, uint32_t ssel = PNUM_NOT_DEFINED);

    /**
     * @name Pins (call before begin())
     * On the CH32X035 SPI1 has one pin for each role, so these only matter
     * for an SPIClass made with no pins at all.
     * @{
     */

    // setMISO/MOSI/SCLK/SSEL have to be called before begin()
    /** @brief Sets the MISO pin. @param miso the pin's Arduino number (`PA6`). */
    void setMISO(uint32_t miso)
    {
      _spi.pin_miso = digitalPinToPinName(miso);
    };
    /** @brief Sets the MOSI pin. @param mosi the pin's Arduino number (`PA7`). */
    void setMOSI(uint32_t mosi)
    {
      _spi.pin_mosi = digitalPinToPinName(mosi);
    };
    /** @brief Sets the clock pin. @param sclk the pin's Arduino number (`PA5`). */
    void setSCLK(uint32_t sclk)
    {
      _spi.pin_sclk = digitalPinToPinName(sclk);
    };
    /**
     * @brief Sets a hardware chip select, driven by the peripheral itself.
     * @param ssel the pin's Arduino number (`PA4`, the panel's CS on this
     *             board).
     */
    void setSSEL(uint32_t ssel)
    {
      _spi.pin_ssel = digitalPinToPinName(ssel);
    };

    /** @brief Sets the MISO pin. @param miso the pin's name (`PA_6`). */
    void setMISO(PinName miso)
    {
      _spi.pin_miso = (miso);
    };
    /** @brief Sets the MOSI pin. @param mosi the pin's name (`PA_7`). */
    void setMOSI(PinName mosi)
    {
      _spi.pin_mosi = (mosi);
    };
    /** @brief Sets the clock pin. @param sclk the pin's name (`PA_5`). */
    void setSCLK(PinName sclk)
    {
      _spi.pin_sclk = (sclk);
    };
    /** @brief Sets a hardware chip select. @param ssel the pin's name (`PA_4`). */
    void setSSEL(PinName ssel)
    {
      _spi.pin_ssel = (ssel);
    };
    /** @} */

    /**
     * @brief Starts the SPI with the pin's settings (the defaults the first
     * time: 3 MHz, MSB first, `SPI_MODE0`).
     *
     * Resets SPI1 and programs it afresh, and sets the SPI pins up.
     * @param _pin  a CS pin for the class to drive (made an output and set
     *              high here), or @ref CS_PIN_CONTROLLED_BY_USER (the
     *              default). Nothing happens if @ref NB_SPI_SETTINGS other
     *              pins already have settings.
     */
    virtual void begin(uint8_t _pin = CS_PIN_CONTROLLED_BY_USER);
    /**
     * @brief Stops the SPI: resets SPI1, switches its clock off and forgets
     * every pin's settings.
     */
    void end(void);

    /* This function should be used to configure the SPI instance in case you
     * don't use default parameters.
     * You can attach another CS pin to the SPI instance and each CS pin can be
     * attach with specific SPI settings.
     */
    /**
     * @brief Stores a device's settings for a CS pin and programs SPI1 with
     * them.
     *
     * Resets SPI1 and programs it afresh. Unlike on AVR, nothing is
     * locked and interrupts are left alone.
     * @param pin       a CS pin for the class to drive (made an output and
     *                  set high here), or @ref CS_PIN_CONTROLLED_BY_USER.
     *                  Nothing happens if @ref NB_SPI_SETTINGS other pins
     *                  already have settings.
     * @param settings  the device's clock, bit order and mode.
     */
    virtual void beginTransaction(uint8_t pin, SPISettings settings);
    /**
     * @brief Programs SPI1 with a device's settings, for a device whose CS
     * the sketch drives itself.
     * @param settings  the device's clock, bit order and mode.
     */
    void beginTransaction(SPISettings settings)
    {
      beginTransaction(CS_PIN_CONTROLLED_BY_USER, settings);
    }

    /**
     * @brief Forgets the pin's settings: transfers for it do nothing until
     * the next begin() or beginTransaction() for it. SPI1 is left as it is.
     * @param pin  the CS pin given to beginTransaction().
     */
    void endTransaction(uint8_t pin);
    /**
     * @brief Forgets the settings of the sketch-driven CS: transfer() does
     * nothing until the next begin() or beginTransaction().
     */
    void endTransaction(void)
    {
      endTransaction(CS_PIN_CONTROLLED_BY_USER);
    }

    /**
     * @name Transfers
     * Each one needs begin() or beginTransaction() for its pin first. With
     * a CS pin other than the last transfer's, SPI1 is reset and programmed
     * with that pin's settings first. The class drives the pin low for the
     * transfer and, with `SPI_LAST`, high after it.
     * @{
     */

    /* Transfer functions: must be called after initialization of the SPI
     * instance with begin() or beginTransaction().
     * You can specify the CS pin to use.
     */
    /**
     * @brief Sends one byte and returns the byte received meanwhile.
     * @param pin    the device's CS pin.
     * @param _data  the byte to send.
     * @param _mode  `SPI_LAST` (the default) releases CS afterwards,
     *               `SPI_CONTINUE` keeps it low for the next transfer.
     * @return the byte received; 0 if the pin has no settings or the
     *         settings are `SPI_TRANSMITONLY`.
     */
    virtual byte transfer(uint8_t pin, uint8_t _data, SPITransferMode _mode = SPI_LAST);
    /**
     * @brief Sends 16 bits as two bytes and returns the 16 bits received.
     *
     * With `MSBFIRST` the high byte goes first, with `LSBFIRST` the low
     * byte, so the bits go out in the chosen order.
     * @param pin    the device's CS pin.
     * @param _data  the 16 bits to send.
     * @param _mode  `SPI_LAST` (the default) or `SPI_CONTINUE`.
     * @return the 16 bits received; 0 if the pin has no settings or the
     *         settings are `SPI_TRANSMITONLY`.
     */
    virtual uint16_t transfer16(uint8_t pin, uint16_t _data, SPITransferMode _mode = SPI_LAST);
    /**
     * @brief Sends a buffer, replacing its bytes with the bytes received.
     * @param pin     the device's CS pin.
     * @param _buf    the bytes to send, overwritten with those received
     *                (left as sent with `SPI_TRANSMITONLY`).
     * @param _count  how many bytes (up to 65,535); 0 does nothing.
     * @param _mode   `SPI_LAST` (the default) or `SPI_CONTINUE`.
     */
    virtual void transfer(uint8_t pin, void *_buf, size_t _count, SPITransferMode _mode = SPI_LAST);
    /**
     * @brief Sends one buffer and receives into another.
     * @param _pin     the device's CS pin.
     * @param _bufout  the bytes to send.
     * @param _bufin   receives the bytes received (untouched with
     *                 `SPI_TRANSMITONLY`); may be `_bufout`.
     * @param _count   how many bytes (up to 65,535); 0 does nothing.
     * @param _mode    `SPI_LAST` (the default) or `SPI_CONTINUE`.
     */
    virtual void transfer(byte _pin, void *_bufout, void *_bufin, size_t _count, SPITransferMode _mode = SPI_LAST);

    // Transfer functions when user controls himself the CS pin.
    /**
     * @brief Sends one byte and returns the byte received meanwhile (CS
     * driven by the sketch).
     * @param _data  the byte to send.
     * @param _mode  ignored without a CS pin.
     * @return the byte received; 0 before begin() or with
     *         `SPI_TRANSMITONLY`.
     */
    byte transfer(uint8_t _data, SPITransferMode _mode = SPI_LAST)
    {
      return transfer(CS_PIN_CONTROLLED_BY_USER, _data, _mode);
    }

    /**
     * @brief Sends 16 bits and returns the 16 bits received (CS driven by
     * the sketch).
     * @param _data  the 16 bits to send, in the chosen bit order.
     * @param _mode  ignored without a CS pin.
     * @return the 16 bits received; 0 before begin() or with
     *         `SPI_TRANSMITONLY`.
     */
    uint16_t transfer16(uint16_t _data, SPITransferMode _mode = SPI_LAST)
    {
      return transfer16(CS_PIN_CONTROLLED_BY_USER, _data, _mode);
    }

    /**
     * @brief Sends a buffer, replacing its bytes with the bytes received (CS
     * driven by the sketch).
     * @param _buf    the bytes to send, overwritten with those received.
     * @param _count  how many bytes (up to 65,535).
     * @param _mode   ignored without a CS pin.
     */
    void transfer(void *_buf, size_t _count, SPITransferMode _mode = SPI_LAST)
    {
      transfer(CS_PIN_CONTROLLED_BY_USER, _buf, _count, _mode);
    }

    /**
     * @brief Sends one buffer and receives into another (CS driven by the
     * sketch).
     * @param _bufout  the bytes to send.
     * @param _bufin   receives the bytes received.
     * @param _count   how many bytes (up to 65,535).
     * @param _mode    ignored without a CS pin.
     */
    void transfer(void *_bufout, void *_bufin, size_t _count, SPITransferMode _mode = SPI_LAST)
    {
      transfer(CS_PIN_CONTROLLED_BY_USER, _bufout, _bufin, _count, _mode);
    }
    /** @} */

    /**
     * @name Deprecated settings
     * Kept for compatibility: use SPISettings with beginTransaction()
     * instead. Each changes one of the pin's settings and then resets and
     * programs SPI1 with them; for a pin with no settings it does nothing.
     * @{
     */

    /* These methods are deprecated and kept for compatibility.
     * Use SPISettings with SPI.beginTransaction() to configure SPI parameters.
     */
    /**
     * @brief Sets the bit order for a CS pin.
     * @param _pin    the CS pin.
     * @par Parameters
     * - `_order`: `MSBFIRST` or `LSBFIRST`.
     */
    void setBitOrder(uint8_t _pin, BitOrder);
    /** @brief Sets the bit order. @param _order `MSBFIRST` or `LSBFIRST`. */
    void setBitOrder(BitOrder _order)
    {
      setBitOrder(CS_PIN_CONTROLLED_BY_USER, _order);
    }

    /**
     * @brief Sets the mode for a CS pin.
     * @param _pin   the CS pin.
     * @par Parameters
     * - `_mode`: `SPI_MODE0` ... `SPI_MODE3`; any other value is ignored.
     */
    void setDataMode(uint8_t _pin, uint8_t);
    /** @brief Sets the mode. @param _mode `SPI_MODE0` ... `SPI_MODE3`. */
    void setDataMode(uint8_t _mode)
    {
      setDataMode(CS_PIN_CONTROLLED_BY_USER, _mode);
    }

    /**
     * @brief Sets the clock for a CS pin as a divider of 48 MHz.
     * @param _pin  the CS pin.
     * @par Parameters
     * - `_div`: `SPI_CLOCK_DIV2` ... `SPI_CLOCK_DIV128` (any 1-255 works;
     *   the result is rounded down to 48 MHz / 2^n); 0 means the
     *   default clock (3 MHz).
     */
    void setClockDivider(uint8_t _pin, uint8_t);
    /**
     * @brief Sets the clock as a divider of 48 MHz.
     * @param _div  `SPI_CLOCK_DIV2` ... `SPI_CLOCK_DIV128`; 0 means the
     *              default clock (3 MHz).
     */
    void setClockDivider(uint8_t _div)
    {
      setClockDivider(CS_PIN_CONTROLLED_BY_USER, _div);
    }
    /** @} */

    // Not implemented functions. Kept for backward compatibility.
    /**
     * @brief Does nothing (kept for compatibility): transfers are never
     * guarded against interrupts.
     * @param interruptNumber  ignored.
     */
    void usingInterrupt(uint8_t interruptNumber);
    /** @brief Does nothing (kept for compatibility). */
    void attachInterrupt(void);
    /** @brief Does nothing (kept for compatibility). */
    void detachInterrupt(void);

    // Could be used to mix Arduino API and STM32Cube HAL API (ex: DMA). Use at your own risk.
    /**
     * @brief The WCH peripheral library's view of this SPI: its instance
     * and init structure, for mixing in WCH's own SPI functions. Use at
     * your own risk.
     * @return the handle, valid for the object's lifetime.
     */
    SPI_HandleTypeDef *getHandle(void)
    {
      return &(_spi.handle);
    }

  protected:
    // spi instance
    spi_t         _spi;   /**< the instance's pins, peripheral and WCH init structure */

  private:
    /* Contains various spiSettings for the same spi instance. Each spi spiSettings
    is associated to a CS pin. */
    SPISettings   spiSettings[NB_SPI_SETTINGS];

    // Use to know which configuration is selected.
    int16_t       _CSPinConfig;

    typedef enum {
      GET_IDX = 0,
      ADD_NEW_PIN = 1
    } pin_option_t;

    uint8_t pinIdx(uint8_t _pin, pin_option_t option)
    {
      uint8_t i;

      if ((_pin > NUM_DIGITAL_PINS) && (!digitalPinIsValid(_pin))) {
        return NB_SPI_SETTINGS;
      }

      for (i = 0; i < NB_SPI_SETTINGS; i++) {
        if (_pin == spiSettings[i].pinCS) {
          return i;
        }
      }

      if (option == ADD_NEW_PIN) {
        for (i = 0; i < NB_SPI_SETTINGS; i++) {
          if (spiSettings[i].pinCS == -1) {
            spiSettings[i].pinCS = _pin;
            return i;
          }
        }
      }
      return i;
    }

    void RemovePin(uint8_t _pin)
    {
      if ((_pin > NUM_DIGITAL_PINS) && (!digitalPinIsValid(_pin))) {
        return;
      }

      for (uint8_t i = 0; i < NB_SPI_SETTINGS; i++) {
        if (spiSettings[i].pinCS == _pin) {
          spiSettings[i].pinCS = -1;
          spiSettings[i].clk = SPI_SPEED_CLOCK_DEFAULT;
          spiSettings[i].bOrder = MSBFIRST;
          spiSettings[i].dMode = SPI_MODE_0;
        }
      }
    }

    void RemoveAllPin(void)
    {
      for (uint8_t i = 0; i < NB_SPI_SETTINGS; i++) {
        spiSettings[i].pinCS = -1;
        spiSettings[i].clk = SPI_SPEED_CLOCK_DEFAULT;
        spiSettings[i].bOrder = MSBFIRST;
        spiSettings[i].dMode = SPI_MODE_0;
      }
    }
};

/**
 * @brief The SPI: SPI1 on PA5 (SCK), PA6 (MISO) and PA7 (MOSI), the bus the
 * board's panel and SD card are on.
 */
extern SPIClass SPI;

#if defined(SUBGHZSPI_BASE)
class SUBGHZSPIClass : public SPIClass {
  public:
    SUBGHZSPIClass(): SPIClass{NC, NC, NC, NC}
    {
      _spi.spi = SUBGHZSPI;
    }

    void begin(uint8_t _pin = CS_PIN_CONTROLLED_BY_USER);
    void beginTransaction(uint8_t pin, SPISettings settings);
    byte transfer(uint8_t pin, uint8_t _data, SPITransferMode _mode = SPI_LAST);
    uint16_t transfer16(uint8_t pin, uint16_t _data, SPITransferMode _mode = SPI_LAST);
    void transfer(uint8_t pin, void *_buf, size_t _count, SPITransferMode _mode = SPI_LAST);
    void transfer(byte _pin, void *_bufout, void *_bufin, size_t _count, SPITransferMode _mode = SPI_LAST);
    void enableDebugPins(uint32_t mosi = DEBUG_SUBGHZSPI_MOSI, uint32_t miso = DEBUG_SUBGHZSPI_MISO, uint32_t sclk = DEBUG_SUBGHZSPI_SCLK, uint32_t ssel = DEBUG_SUBGHZSPI_SS);

    using SPIClass::beginTransaction;
    using SPIClass::transfer;
    using SPIClass::transfer16;
};

#endif

/** @} */

#endif /* _SPI_H_INCLUDED */
