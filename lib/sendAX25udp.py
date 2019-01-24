#!/usr/bin/env python3

import struct
import crcmod
import sys
from bitstring import BitArray

class X25:
    def __init__(self):
        self.x25_crc_func = crcmod.predefined.mkCrcFun('x-25')
        self.flag = struct.pack("<B", 0x7e)

    def _encode_address(self, address, ssid=0, last=False):
        if ssid > 15:
            raise 
        result = ""
        for letter in address.ljust(6):
            result += chr(ord(letter.upper()) << 1)
        rssid = ssid << 1
        if last:
            rssid = rssid | 0b01100001
        else: 
            rssid = rssid | 0b01100000
        result += chr(rssid)
        return result.encode('Latin-1')

    def getAddress(self, address, ssid=0, last=False):
        return self._encode_address(address, ssid, last)

    def calc_crc(self, packet):
        # Calculate the CRC
        c = self.x25_crc_func(packet)
        crc = BitArray(hex(c))
        crc.byteswap()
        return (crc).bytes

    # Relays is an array of relays
    def packet(self, src, src_ssid = 0, dst = "CQ", dst_ssid = 0, relays = [], message = ""):
        # Start Building the packet
        packet = struct.pack("<7s", self.getAddress(dst, dst_ssid))
        if len(relays) == 0:
            packet += struct.pack("<7s", self.getAddress(src, src_ssid, True))
        else:
            packet += struct.pack("<7s", self.getAddress(src, src_ssid))
            for relay in relays[:-1]:
                packet += struct.pack("<7s", self.getAddress(relay[0], relay[1]))
            packet += struct.pack("<7s", self.getAddress(relays[-1][0], relays[-1][1], True))
        packet += struct.pack("<BB{}s".format(len(message)), 0x3F, 0xF0, bytes(message, "ASCII"))
        return packet

    def frames(self, packet):
        crc = self.calc_crc(packet)
        return packet + crc


x = X25()
packet = x.packet("w2fs", 4, "cq", 0, relays = [['RELAY', 0]], message="Test")
packet = x.packet("ve3yca", 4, "cq", 0, relays = [], message="Test")
sys.stdout.buffer.write(x.frames(packet))
