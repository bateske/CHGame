/*
  TwoWire.h - TWI/I2C library for Arduino & Wiring
  Copyright (c) 2006 Nicholas Zambetti.  All right reserved.

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

  Modified 2012 by Todd Krein (todd@krein.org) to implement repeated starts
  
  Modified 6 june 2023 by Temperslee to support wch's risc-v chips
*/

/**
 * @file
 * @brief Arduino's Wire library (TwoWire), ported to WCH's chips: I2C master
 * and slave on the CH32X035's I2C1.
 */

/**
 * @defgroup core_wire Wire (I2C)
 * @ingroup lib_core
 * @brief The Arduino Wire API: I2C master (and slave) on I2C1.
 *
 * @code
 * #include <Wire.h>
 *
 * Wire.begin();                       // master, 100 kHz
 * Wire.beginTransmission(0x3C);
 * Wire.write(0x00);
 * Wire.write(0xAF);
 * uint8_t err = Wire.endTransmission();   // 0: done
 * if (Wire.requestFrom(0x3C, 1) == 1) {
 *     int b = Wire.read();
 * }
 * @endcode
 *
 * On the CHGame board (rev0) the global @ref Wire uses SDA = PC18
 * (`PIN_WIRE_SDA`) and SCL = PC19 (`PIN_WIRE_SCL`), which come out on the
 * expansion header H1: SDA on H1.2, SCL on H1.1. The board has no pull-up
 * resistors on them, so the device or the wiring must provide them. (They
 * are also the chip's two-wire debug pins, DIO and DCK.) The stock
 * CH32X035 defaults, PC17 and PC16, are the board's USB D+ and D-: never
 * pass them to begin(sda, scl) or setSDA() / setSCL().
 *
 * Transfers are polled (slave mode uses the I2C interrupt) and each step
 * gives up after about 3 ms (`I2C_TIMEOUT_TICK`). The transmit and receive
 * buffers live on the heap: they start at @ref BUFFER_LENGTH bytes, grow as
 * needed, and a transmission holds at most @ref WIRE_MAX_TX_BUFF_LENGTH bytes.
 * @{
 */
#ifndef TwoWire_h
#define TwoWire_h

#include <functional>

#include "Stream.h"
#include "Arduino.h"

extern "C" {
#include "utility/twi.h"
}

// Minimal buffer length. Buffers length will be increased when needed,
// but TX buffer is limited to a maximum to avoid too much stack consumption
// Note: Buffer length and max buffer length are limited by uin16_t type
/**
 * @brief The smallest size of the receive and transmit buffers, in bytes
 * (they grow on the heap when a transfer needs more).
 */
#define BUFFER_LENGTH 32
/**
 * @brief The most bytes one transmission (beginTransmission() ...
 * endTransmission()) can hold; write() returns 0 past it. Default 1024.
 */
#if !defined(WIRE_MAX_TX_BUFF_LENGTH)
  #define WIRE_MAX_TX_BUFF_LENGTH       1024U
#endif

// WIRE_HAS_END means Wire has end()
/**
 * @brief Defined to 1: this Wire has end().
 */
#define WIRE_HAS_END 1

/**
 * @brief An I2C bus: the Arduino Wire API on one of the chip's I2C
 * peripherals (the global @ref Wire on this board).
 *
 * As a master: beginTransmission(), write() and endTransmission() to send;
 * requestFrom(), then available() and read() to receive. As a slave:
 * begin(address), with onReceive() and onRequest(). It is a `Stream`, so
 * `print()` works inside a transmission too.
 */
class TwoWire : public Stream {
  public:
    /**
     * @brief What onReceive() takes: called with the number of bytes received.
     */
    typedef std::function<void(int)> cb_function_receive_t;
    /**
     * @brief What onRequest() takes: called when the master asks for data.
     */
    typedef std::function<void(void)> cb_function_request_t;

  private:
    uint8_t *rxBuffer;           //Dynamic application and release 
    uint16_t rxBufferAllocated;   
    uint16_t rxBufferIndex;
    uint16_t rxBufferLength;

    uint8_t txAddress;
    uint8_t *txBuffer;           //Dynamic application and release
    uint16_t txBufferAllocated;
    uint16_t txDataSize;

    uint8_t transmitting;

    uint8_t ownAddress;
    i2c_t _i2c;

    std::function<void(int)> user_onReceive;
    std::function<void(void)> user_onRequest;

    static void onRequestService(i2c_t *);
    static void onReceiveService(i2c_t *);

    void allocateRxBuffer(size_t length);
    size_t allocateTxBuffer(size_t length);

    void resetRxBuffer(void);
    void resetTxBuffer(void);
    void recoverBus(void);

  public:
    /**
     * @brief An I2C bus on the variant's `SDA` and `SCL` (PC18 and PC19 on
     * this board).
     */
    TwoWire();
    /**
     * @brief An I2C bus on the given pins.
     * @param sda  the SDA pin (Arduino pin number).
     * @param scl  the SCL pin (Arduino pin number).
     */
    TwoWire(uint32_t sda, uint32_t scl);
    // setSCL/SDA have to be called before begin()
    /**
     * @brief Sets the SCL pin; call before begin().
     * @param scl  the pin's Arduino number (`PC19` on this board).
     */
    void setSCL(uint32_t scl)
    {
      _i2c.scl = digitalPinToPinName(scl);
    };
    /**
     * @brief Sets the SDA pin; call before begin().
     * @param sda  the pin's Arduino number (`PC18` on this board).
     */
    void setSDA(uint32_t sda)
    {
      _i2c.sda = digitalPinToPinName(sda);
    };
    /**
     * @brief Sets the SCL pin; call before begin().
     * @param scl  the pin's name (`PC_19`).
     */
    void setSCL(PinName scl)
    {
      _i2c.scl = scl;
    };
    /**
     * @brief Sets the SDA pin; call before begin().
     * @param sda  the pin's name (`PC_18`).
     */
    void setSDA(PinName sda)
    {
      _i2c.sda = sda;
    };
    /**
     * @brief Joins the bus as the master, at 100 kHz.
     *
     * Sets the pins up and resets I2C1. If a device holds SDA low (stuck after
     * a reset), clocks SCL 20 times first to free it. Call it once, or end()
     * first: it forgets (and leaks) the buffers it had.
     * @param generalCall  stored, but not used by this port.
     */
    void begin(bool generalCall = false);
    /**
     * @brief Joins the bus as the master on the given pins, at 100 kHz.
     * @par Parameters
     * - `sda`: the SDA pin (Arduino pin number).
     * - `scl`: the SCL pin (Arduino pin number).
     */
    void begin(uint32_t, uint32_t);
    /**
     * @brief Joins the bus as a slave at a 7-bit address (1 means the master,
     * as begin() does).
     *
     * The I2C interrupt then answers the master: see onReceive() and
     * onRequest(). A slave receives at most 32 bytes per message
     * (`I2C_TXRX_BUFFER_SIZE`).
     * @par Parameters
     * - `address`: the slave's 7-bit address.
     * @param generalCall    stored, but not used by this port.
     * @param NoStretchMode  stored, but not used by this port.
     */
    void begin(uint8_t, bool generalCall = false, bool NoStretchMode = false);
    /**
     * @brief Joins the bus as a slave at a 7-bit address (the `int` form).
     * @par Parameters
     * - `address`: the slave's 7-bit address.
     * @param generalCall    stored, but not used by this port.
     * @param NoStretchMode  stored, but not used by this port.
     */
    void begin(int, bool generalCall = false, bool NoStretchMode = false);
    /**
     * @brief Leaves the bus: turns the I2C interrupts off, resets I2C1 and
     * frees the buffers.
     */
    void end();
    /**
     * @brief Sets the bus clock; call after begin().
     * @par Parameters
     * - `frequency`: in Hz: up to 100000 gives 100 kHz, up to 400000 gives
     *   400 kHz, up to 1000000 gives 1 MHz. Higher values are not
     *   valid.
     */
    void setClock(uint32_t);
    /**
     * @brief Starts collecting bytes for a slave; nothing goes on the bus until
     * endTransmission().
     * @par Parameters
     * - `address`: the slave's 7-bit address.
     */
    void beginTransmission(uint8_t);
    /**
     * @brief Starts collecting bytes for a slave (the `int` form).
     * @par Parameters
     * - `address`: the slave's 7-bit address.
     */
    void beginTransmission(int);
    /**
     * @brief Sends the bytes collected since beginTransmission(), then a STOP.
     *
     * Blocks until done. With no bytes it only addresses the slave, which is
     * how an I2C scanner finds devices.
     * @return As Arduino's: 0 sent; 2 no slave acknowledged the address;
     *         3 the slave did not acknowledge a data byte; 4 another error
     *         (bus busy, timeout). A NACK ends the write with a STOP at once.
     */
    uint8_t endTransmission(void);
    /**
     * @brief Sends the bytes collected since beginTransmission(), with or
     * without a STOP.
     * @par Parameters
     * - `sendStop`: `true`: end with a STOP; `false`: keep the bus, for a
     *   repeated start by the requestFrom() that follows.
     * @return 0 sent; 2 address not acknowledged; 3 data not acknowledged;
     *         4 another error (see endTransmission()).
     */
    uint8_t endTransmission(uint8_t);
    /**
     * @brief Reads bytes from a slave into the receive buffer, for available()
     * and read().
     *
     * Blocks until done; the read always ends with a STOP.
     * @par Parameters
     * - `address`: the slave's 7-bit address.
     * - `quantity`: how many bytes, 1 to 255.
     * @return `quantity` if they all arrived, 0 if the read failed.
     * @note The whole read must finish within about 3 ms (`I2C_TIMEOUT_TICK`):
     *       at 100 kHz that is about 30 bytes, at 400 kHz about 120. Raise the
     *       clock with setClock(), or read in smaller pieces, for more.
     */
    uint8_t requestFrom(uint8_t, uint8_t);
    /**
     * @brief Reads bytes from a slave (Arduino's form with `sendStop`).
     * @par Parameters
     * - `address`: the slave's 7-bit address.
     * - `quantity`: how many bytes, 1 to 255.
     * - `sendStop`: ignored: this port always ends a read with a STOP.
     * @return `quantity` if they all arrived, 0 if the read failed.
     */
    uint8_t requestFrom(uint8_t, uint8_t, uint8_t);
    /**
     * @brief Reads bytes from a slave (Arduino's form with `sendStop`).
     * @par Parameters
     * - `address`: the slave's 7-bit address.
     * - `quantity`: how many bytes, 1 to 255.
     * - `sendStop`: ignored: this port always ends a read with a STOP.
     * @return `quantity` if they all arrived, 0 if the read failed.
     */
    uint8_t requestFrom(uint8_t, size_t, bool);
    /**
     * @brief Writes a register address to a slave, then reads bytes from it
     * with a repeated start.
     * @par Parameters
     * - `address`: the slave's 7-bit address.
     * - `quantity`: how many bytes, 1 to 255.
     * - `iaddress`: the register (internal) address, sent first.
     * - `isize`: how many bytes of `iaddress` to send, most significant
     *   first: 0 (none, a plain read) to 3.
     * - `sendStop`: ignored: this port always ends a read with a STOP.
     * @return `quantity` if they all arrived, 0 if the read failed.
     */
    uint8_t requestFrom(uint8_t, uint8_t, uint32_t, uint8_t, uint8_t);
    /**
     * @brief Reads bytes from a slave (the `int` form).
     * @par Parameters
     * - `address`: the slave's 7-bit address.
     * - `quantity`: how many bytes, 1 to 255.
     * @return `quantity` if they all arrived, 0 if the read failed.
     */
    uint8_t requestFrom(int, int);
    /**
     * @brief Reads bytes from a slave (the `int` form with `sendStop`).
     * @par Parameters
     * - `address`: the slave's 7-bit address.
     * - `quantity`: how many bytes, 1 to 255.
     * - `sendStop`: ignored: this port always ends a read with a STOP.
     * @return `quantity` if they all arrived, 0 if the read failed.
     */
    uint8_t requestFrom(int, int, int);
    /**
     * @brief Adds a byte to the transmission, or, in a slave's onRequest()
     * callback, sends it to the master.
     * @par Parameters
     * - `data`: the byte.
     * @return 1, or 0 if the transmission would pass
     *         @ref WIRE_MAX_TX_BUFF_LENGTH bytes (or a slave's byte was not
     *         taken).
     */
    virtual size_t write(uint8_t);
    /**
     * @brief Adds bytes to the transmission, or, in a slave's onRequest()
     * callback, sends them to the master.
     * @par Parameters
     * - `data`: the bytes.
     * - `quantity`: how many.
     * @return `quantity`, or 0 if the transmission would pass
     *         @ref WIRE_MAX_TX_BUFF_LENGTH bytes (none are added then).
     */
    virtual size_t write(const uint8_t *, size_t);
    /**
     * @brief How many received bytes are left to read (after requestFrom(),
     * or in an onReceive() callback).
     * @return the number of bytes.
     */
    virtual int available(void);
    /**
     * @brief Takes the next received byte.
     * @return the byte (0-255), or -1 if there is none.
     */
    virtual int read(void);
    /**
     * @brief The next received byte, left in the buffer.
     * @return the byte (0-255), or -1 if there is none.
     */
    virtual int peek(void);
    /**
     * @brief Throws away the received bytes and the transmission's bytes.
     * (Unlike `Serial.flush()`, it does not wait for anything.)
     */
    virtual void flush(void);

    /**
     * @brief Sets what a slave does when the master has sent it a message.
     * @param callback  called from the I2C interrupt after the master's STOP,
     *                  with the number of bytes received (1-32); it reads them
     *                  with read().
     */
    void onReceive(cb_function_receive_t callback);
    /**
     * @brief Sets what a slave does when the master asks it for data.
     * @param callback  called from the I2C interrupt; it answers with write().
     */
    void onRequest(cb_function_request_t callback);

    /**
     * @brief Writes the low byte of `n` (see write(uint8_t)).
     * @param n  the value; only its low 8 bits are sent.
     * @return 1, or 0 if it did not fit.
     */
    inline size_t write(unsigned long n)
    {
      return write((uint8_t)n);
    }
    /**
     * @brief Writes the low byte of `n` (see write(uint8_t)).
     * @param n  the value; only its low 8 bits are sent.
     * @return 1, or 0 if it did not fit.
     */
    inline size_t write(long n)
    {
      return write((uint8_t)n);
    }
    /**
     * @brief Writes the low byte of `n` (see write(uint8_t)).
     * @param n  the value; only its low 8 bits are sent.
     * @return 1, or 0 if it did not fit.
     */
    inline size_t write(unsigned int n)
    {
      return write((uint8_t)n);
    }
    /**
     * @brief Writes the low byte of `n` (see write(uint8_t)).
     * @param n  the value; only its low 8 bits are sent.
     * @return 1, or 0 if it did not fit.
     */
    inline size_t write(int n)
    {
      return write((uint8_t)n);
    }
    using Print::write;

    /**
     * @brief The WCH peripheral library's view of this bus: its instance and
     * init structure, for mixing in WCH's own I2C functions. Use at your own
     * risk.
     * @return the handle, valid for the object's lifetime.
     */
    I2C_HandleTypeDef *getHandle(void)
    {
      return &(_i2c.handle);
    }
};



/**
 * @brief The I2C bus: I2C1 on PC18 (SDA, header H1.2) and PC19 (SCL, H1.1).
 */
extern TwoWire Wire;

/** @} */

#endif
