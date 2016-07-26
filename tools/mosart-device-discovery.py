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
common.init_args('./mosart-device-discovery.py')
common.parser.add_argument('-d', '--dwell', type=float, help='Dwell time per channel, in milliseconds', default='200')
common.parse_and_init()

# Put the radio in promiscuous mode
common.radio.enter_promiscuous_mode_generic("\xAA\xAA\xAA", common.RF_RATE_1M)

# Set the channels to {2..84..2}
common.channels = range(2, 84, 2)

# Convert dwell time from milliseconds to seconds
dwell_time = common.args.dwell / 1000

# Set the initial channel
common.radio.set_channel(common.channels[0])

# Potentially valid address counts
addresses = {}

# Sweep through the channels and decode ESB packets in pseudo-promiscuous mode
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
  if value[0] == 0xFF: continue

  # De-whiten the payload
  for x in range(len(value)): value[x] ^= 0x5A

  # Look for the 11:22 sequence
  for x in range(len(value)-6):
    if value[x+4] == 0x11 and value[x+5] == 0x22:

      address = chr(value[x]) + chr(value[x+1]) + chr(value[x+2]) + chr(value[x+3])
      if not address in addresses: addresses[address] = 0
      addresses[address] += 1
      if addresses[address] > 10:

        # Log the address and quit
        logging.info('\033[92m\033[1mMOSART dongle found on channel {0} with address {1}\033[0m'.format(
                  common.channels[channel_index],
                  ':'.join('{:02X}'.format(ord(b)) for b in address)))

        quit()

  # Log the packet
  logging.debug('{0: >2}  {1: >2}  {2}'.format(
            common.channels[channel_index],
            len(value),
            ':'.join('{:02X}'.format(b) for b in value)))

