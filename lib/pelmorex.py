#!/usr/bin/env python3

from bs4 import BeautifulSoup
from shapely.geometry import Point, Polygon
from datetime import datetime, timedelta
import socket, pprint


class pelmorex():
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.TCP_HOST="streaming2.naad-adna.pelmorex.com"
        self.TCP_IP = socket.gethostbyname( self.TCP_HOST )
        self.TCP_PORT=8080
        self.BUFFER_SIZE=4098
        self.data = None
        self.EOATEXT = b"</alert>"
        self.lastheartbeat = datetime.now()

    def _reconnect(self):
        print("Reconnecting")
        self.s.close()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

    def connect(self):
        print("connecting")
        self.s.connect((self.TCP_IP, self.TCP_PORT))
        self.s.settimeout(10)
        self.lastheartbeat = datetime.now()

    def start(self):
        while 1:
            if self.lastheartbeat + timedelta(minutes=2) < datetime.now():
                self._reconnect()
            result = self.read()
            if result != False:
                result = self.parse(result)
                if result.sender.string != "NAADS-Heartbeat":
                    print('Alert received:\n')
                    self.save(result)
                    print(result.prettify())
                else:
                    self.lastheartbeat = datetime.now()
                print(result.sender.string)

    # Checks to see if a point is in the alert poly
    # alert: The alert data
    # points: A tuple or a list of tuples consisting of points
    #
    # Returns the first point position within the poly or false

    def filter_in_geo(self, alert, points):
        for infos in alert.findAll('info'):
            for areas in infos.findAll('area'):
                if areas.find("polygon"):
                    p = [tuple(map(float,s.split(','))) for s in areas.polygon.string.split(' ')]
                    poly = Polygon(p)
                    counter = 0
                    if all(isinstance(item, tuple) for item in points):
                        for point in points:
                            counter += 1
                            p1 = Point(point[0], point[1])
                            if p1.within(poly):
                                return counter
                    else:
                        p1 = Point(points[0], points[1])
                        if p1.within(poly):
                            return 1
        return False

    def parse(self, data):
        alert = BeautifulSoup(data, "xml")
        return alert

    def save(self, data, directory="savedata"):
        with open("%s/%s.xml" % (directory, data.identifier.string), "w") as file:
            file.write(str(data))

    def read(self):
        try:
            buffer = self.s.recv(self.BUFFER_SIZE)
        except socket.timeout:
            return False
        except socket.error:
            print("Socket error")
            self._reconnect()
            return False

        if self.data == None: 
            self.data = buffer
        else:
            self.data += buffer

        eoa = self.data.find(self.EOATEXT)
        if (eoa != -1):
            xml = self.data[0:eoa + len(self.EOATEXT)]
            self.data = self.data[eoa + len(self.EOATEXT):]
            return xml
        return False

if __name__ == "__main__":
    p = pelmorex()
    p.connect()
    p.start()

#    testdata = open("../samples/6example_CAPCP_with_free_drawn_polygon.xml","r").read()
#    testdata = open("Ontario-Fixed.xml","r").read()
#    result = p.parse(testdata)
#    print(p.filter_in_geo(result, (44.389355, -79.690331)))
#    print(result.sender.string)

