#!/usr/bin/env python2

'''
  Copyright (C) 2016 Bastille Networks

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import time, logging, sys
sys.path.append('../nrf-research-firmware/tools')
from lib import common

# Parse command line arguments and initialize the radio
common.init_args('./ge-device-discovery.py')
common.parser.add_argument('-d', '--dwell', type=float, help='Dwell time per channel, in milliseconds', default='200')
common.parse_and_init()

# Put the radio in promiscuous mode
common.radio.enter_promiscuous_mode_generic("\x33\x33\x33\x30", common.RF_RATE_1M, 32)

# Set the channels to {18..63..3}
common.channels = range(18, 63+1, 3)

# Convert dwell time from milliseconds to seconds
dwell_time = common.args.dwell / 1000

# Set the initial channel
common.radio.set_channel(common.channels[0])

# Potentially valid address counts
addresses = {}

# Update a CRC-CCITT with one byte of data
def crc_update(crc, data):
  crc ^= (data << 8)
  for x in range(8):
    if (crc & 0x8000) == 0x8000: crc = ((crc << 1) ^ 0x1021) & 0xFFFF
    else: crc <<= 1
  crc &= 0xFFFF
  return crc

# Sweep through the channels and decode packets in pseudo-promiscuous mode
last_tune = time.time()
channel_index = 0
while True:

  # Increment the channel
  if len(common.channels) > 1 and time.time() - last_tune > dwell_time:
    channel_index = (channel_index + 1) % (len(common.channels))
    common.radio.set_channel(common.channels[channel_index])
    last_tune = time.time()

  # Receive payloads
  value = common.radio.receive_payload()
  if len(value) < 32: continue

  # Decode
  bits = ''.join(bin(c)[2:].zfill(8) for c in value)[::2]
  decoded = []
  for x in range(len(bits)/8):
    decoded.append(int(bits[x*8:(x+1)*8], 2))
  decoded = decoded[1:]

  print ':'.join('{:02X}'.format(b) for b in decoded)

  # Validate the CRC
  crc = 0x1D0F
  for x in range(9):
    crc = crc_update(crc, decoded[4+x])
  crc_given = decoded[13] << 8 | decoded[14]
  if crc == crc_given:

    # Log the address and quit
    logging.info('\033[92m\033[1mGE 98614 dongle found on channel {0} with address {1}\033[0m'.format(
              common.channels[channel_index],
              ':'.join('{:02X}'.format(b) for b in decoded[0:4])))

    quit()

