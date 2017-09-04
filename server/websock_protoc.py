#!/usr/bin/env python
#coding:utf-8

import base64
import hashlib
import struct
import sys,os

class WebSocket():
    @staticmethod
    def handshake(conn):
        key = None 
        data = conn.recv(8192)
	#print "client request:\n",data
        if not len(data):
            return False
        for line in data.split('\r\n\r\n')[0].split('\r\n')[1:]:
            k, v = line.split(': ')
            if k == 'Sec-WebSocket-Key':
                key = base64.b64encode(hashlib.sha1(v + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest())
        if not key:
            conn.close()
            return False
        response = 'HTTP/1.1 101 Switching Protocols\r\n'\
                   'Upgrade: websocket\r\n'\
                   'Connection: Upgrade\r\n'\
                   'Sec-WebSocket-Accept:' + key + '\r\n\r\n'
        conn.send(response)
        return True

    @staticmethod
    def recv(conn, size=8192):
        data = conn.recv(size)
        if not len(data):
            return False
        length = ord(data[1]) & 127
        if length == 126:
            mask = data[4:8]
            raw = data[8:]
        elif length == 127:
            mask = data[10:14]
            raw = data[14:]
        else:
            mask = data[2:6]
            raw = data[6:]
        ret = ''
        for cnt, d in enumerate(raw):
            ret += chr(ord(d) ^ ord(mask[cnt%4]))
        return ret
                      
    @staticmethod
    def send(conn, data):
        head = '\x81'
        if len(data) < 126:
            head += struct.pack('B', len(data))
        elif len(data) <= 0xFFFF:
            head += struct.pack('!BH', 126, len(data))
        else:
            head += struct.pack('!BQ', 127, len(data))
        conn.send(head+data)
