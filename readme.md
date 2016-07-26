# KeySniffer device discovery tools and advisories

For information on the KeySniffer vulnerabilities, please visit [keysniffer.net](https://www.keysniffer.net).

## Requirements

- SDCC (minimum version 3.1.0)
- GNU Binutils
- Python
- PyUSB
- platformio

Install dependencies on Ubuntu:

```
sudo apt-get install sdcc binutils python python-pip
sudo pip install -U pip
sudo pip install -U -I pyusb
sudo pip install -U platformio
```

## Supported Hardware

The following hardware has been tested and is known to work.

- CrazyRadio PA USB dongle
- SparkFun nRF24LU1+ breakout board
- Logitech Unifying dongle (model C-U0007, Nordic Semiconductor based)

## Initialize the submodule

```
git submodule init
git submodule update
```

## Build the firmware

```
cd nrf-research-firmware
make
```

## Flash over USB

nRF24LU1+ chips come with a factory programmed bootloader occupying the topmost 2KB of flash memory. The CrazyRadio firmware and RFStorm research firmware support USB commands to enter the Nordic bootloader.

Dongles and breakout boards can be programmed over USB if they are running one of the following firmwares:

- Nordic Semiconductor Bootloader
- CrazyRadio Firmware
- RFStorm Research Firmware

To flash the firmware over USB:

```
cd nrf-research-firmware
sudo make install
```

## Flash a Logitech Unifying dongle

*The most common Unifying dongles are based on the nRF24LU1+, but some use chips from Texas Instruments.
This firmware is only supported on the nRF24LU1+ variants, which have a model number of C-U0007. The flashing
script will automatically detect which type of dongle is plugged in, and will only attempt to flash the nRF24LU1+ variants.*

To flash the firmware over USB onto a Logitech Unifying dongle:

```
cd nrf-research-firmware
sudo make logitech_install
```

## Flash a Logitech Unifying dongle back to the original firmware

Download and extract the Logitech firmware image, which will be named `RQR_012_005_00028.hex` or similar. Then, run the following command to flash the Logitech firmware onto the dongle:

```
cd nrf-research-firmware
sudo ./prog/usb-flasher/logitech-usb-restore.py [path-to-firmware.hex]
```

## Flash over SPI using a Teensy

If your dongle or breakout board is bricked, you can alternatively program it over SPI using a Teensy.

This has only been tested with a Teensy 3.1/3.2, but is likely to work with other Arduino variants as well.

### Build and Upload the Teensy Flasher

```
cd nrf-research-firmware/prog
platformio run --project-dir teensy-flasher --target upload
```

### Connect the Teensy to the nRF24LU1+

| Teensy | CrazyRadio PA | Sparkfun nRF24LU1+ Breakout |
| ------ | ---------- | -------- |
| GND | 9 | GND |
| 8 | 3 | RESET |
| 9 | 2 | PROG |
| 10 | 10 | P0.3 |
| 11 | 6 | P0.1 |
| 12 | 8 | P0.2 |
| 13 | 4 | P0.0 |
| 3.3V | 5 | VIN |

### Flash the nRF24LU1+

```
cd nrf-research-firmware
sudo make spi_install
```

# Python Scripts

## device discovery - MOSART Semiconductor based devices

Identify nearby MOSART Semiconductor based wireless keyboard dongles

```
usage: ./tools/mosart-device-discovery.py

```

## device discovery - GE 98614 wireless keyboard

```
usage: ./tools/ge-device-discovery.py

```
