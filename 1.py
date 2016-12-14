#!/usr/bin/env python

from bs4 import BeautifulSoup
import socket, pprint

TCP_HOST="streaming1.naad-adna.pelmorex.com"
TCP_PORT=8080
BUFFER_SIZE=4098

TCP_IP = socket.gethostbyname( TCP_HOST )

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
data = ''
EOATEXT = "</alert>"

while True:
    buffer = s.recv(BUFFER_SIZE)
    data += buffer

    eoa = data.find(EOATEXT)
    if (eoa != -1):
        xml = data[0:eoa + len(EOATEXT)]
        data = data[eoa + len(EOATEXT):]
        alert = BeautifulSoup(xml, "xml")
        print('Alert received:\n')
        print alert.prettify()
        print alert.sender.string

print('Connection closed')
