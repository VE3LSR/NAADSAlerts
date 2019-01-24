#!/usr/bin/env python3

import struct
import crcmod
import sys
from bitstring import BitStream


class X25:
    def __init__(self):
        self.x25_crc_func = crcmod.predefined.mkCrcFun('x-25')        

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

    def hexify(self, string):
        return " ".join(hex((x))[2:] for x in string)

    def getAddress(self, address, ssid=0, last=False):
        return self._encode_address(address, ssid, last)

    # Relays is an array of relays
    def packet(self, src, src_ssid = 0, dst = "CQ", dst_ssid = 0, relays = [], message = ""):
        flag = struct.pack("<B", 0x7e)
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
        # Bit Stuffing - If there is 5 high bits, add a low bit right after
        #TODO
        # Calculate the CRC
        c = self.x25_crc_func(packet)
        crc = BitStream(hex(c))
        crc.reverse()
        return (flag + packet + (crc^'0xFFFF').bytes + flag)

x = X25()

#sys.stdout.buffer.write (x.packet("w2fs", 4, "cq", 0, relays = [['RELAY', 0]], message="Test"))
#sys.stdout.buffer.write (x.packet("ve3yca", 4, "cq", 0, relays = [], message="Test"))

print (x.hexify(x.packet("w2fs", 4, "cq", 0, relays = [['RELAY', 0]], message="Test")))
