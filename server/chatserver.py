#!/usr/bin/env python
#coding:utf-8


import sys,os

from deamon import daemonize
import json
import logging
from websock_protoc import WebSocket
import sock_utils
import threading
import socket






class websocket_thread(threading.Thread):
    def __init__(self, connection):
        super(websocket_thread, self).__init__()
        self.connection = connection

    def run(self):
        while 1:
            data = WebSocket.recv(self.connection)
            finally_data = json.loads(data)
            if not finally_data.has_key("sock_type"):
            	WebSocket.send(self.connection, json.dumps({"code":0,"msg":"没有请求方法"}))
            	self.connection.close()
            sock_type = finally_data["sock_type"]
            username = finally_data["name"]
            chat_type = finally_data["chat_type"]
            if chat_type == "single":
                talk_name = finally_data["talk_name"]
                req = sock_utils.Req_Method(self.connection,username,chat_type,talk_name)
            elif chat_type == "group":
                req = sock_utils.Req_Method(self.connection,username,chat_type)
            sock_result = getattr(req,sock_type)
            sock_result(finally_data)



def main():
    pid = os.getpid()
    with open(process_pid,"w") as f:
        f.write("%d"%pid)
    while True:
        connection, address = sock.accept()
        try:
            if WebSocket.handshake(connection):
                thread = websocket_thread(connection)
                thread.start()
        except socket.timeout:
            logging.warning('websocket connection timeout')
                    
if __name__ == '__main__':
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))   
    process_pid = "%s/%s.pid"%(BASE_DIR,sys.argv[0].strip(".py"))
    process_log = "%s/%s.log"%(BASE_DIR,sys.argv[0].strip(".py"))      
    logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='a') 
    if len(sys.argv) != 2:
            logging.error("参数数目输入错误,ps:python %s start|stop|restart"%sys.argv[0])
    elif sys.argv[1] != "start" and sys.argv[1] != "stop" and sys.argv[1] != "restart":
            logging.error("参数输入错误,ps:start|stop|restart")
    elif sys.argv[1] == "start":
            logging.warning("the process is start")
            daemonize('/dev/null',process_log,process_log)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('0.0.0.0', 7002))
            sock.listen(5)                  
            main()
    elif sys.argv[1] == "stop":
            with open(process_pid,"r") as f:
                    pid = f.read()
            os.kill(int(pid),9)
            logging.warning("the process is stop")


