#!/usr/bin/env python

from bs4 import BeautifulSoup
import socket, pprint

class pelmorex():
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.TCP_HOST="streaming1.naad-adna.pelmorex.com"
        self.TCP_IP = socket.gethostbyname( self.TCP_HOST )
        self.TCP_PORT=8080
        self.BUFFER_SIZE=4098
        self.data = ''
        self.EOATEXT = "</alert>"

    def _reconnect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

    def connect(self):
        print("connecting")
        self.s.connect((self.TCP_IP, self.TCP_PORT))


    def start(self):
        while 1:
            self.read()

    def read(self):
        try:
            buffer = self.s.recv(self.BUFFER_SIZE)
        except socket.error:
            print("Socket error")
            self._reconnect()
            return 

        self.data += buffer

        eoa = self.data.find(self.EOATEXT)
        if (eoa != -1):
            xml = self.data[0:eoa + len(self.EOATEXT)]
            data = self.data[eoa + len(self.EOATEXT):]
            alert = BeautifulSoup(xml, "lxml")
            if alert.sender.string != "NAADS-Heartbeat":
                print('Alert received:\n')
                print(alert.prettify())
            print(alert.sender.string)

if __name__ == "__main__":
    p = pelmorex()
    p.connect()
    p.start()
