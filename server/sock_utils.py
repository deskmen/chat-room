#coding:utf-8

from websock_protoc import WebSocket
import time
import json
import logging
import sys
reload(sys)
sys.setdefaultencoding("utf-8")



sock_list = {}
single_chat_list = [] 

class Req_Method(object):
	def __init__(self,sock,username,chat_type,talk_name=None):
		self.sock = sock
		self.sock_list = sock_list
		self.single_chat_list = single_chat_list
		if chat_type == "group":
			if not sock_list.has_key(username):
				self.sock_list[username] = self.sock
		elif chat_type == "single":
			self.name_to_talk_list = map(lambda x:(x["name"],x["talk_name"]),self.single_chat_list)
			if (username,talk_name) not in self.name_to_talk_list:
				self.single_chat_list.append({"name_sock":self.sock,"msg_list":[],"name":username,"talk_name":talk_name})
		self.return_data = {"code":1}
	def test(self,*args,**kwargs):
		finally_data = args[0]
		msg = finally_data["chat_content"]
		name = finally_data["name"]
		if msg == "logout":
			self.sock_list.pop(name)
		self.return_data["chat_type"] = "group" 
		self.return_data["data"] = msg 
		self.return_data["name"] = name 
		self.return_data["chat_users"] = self.sock_list.keys() 
		for n,s in self.sock_list.items():
			try:
				WebSocket.send(s, json.dumps(self.return_data))
			except:
				s.close()
				self.sock_list.pop(n)
	def lost(self,*args,**kwargs):
		finally_data = args[0]
		name = finally_data["name"]
		logging.waring(finally_data)
		if self.sock_list.has_key(name):
			self.sock_list[name].close()
			self.sock_list.pop(name)
	def single_chat(self,*args,**kwargs):
		finally_data = args[0]
                msg = finally_data["chat_content"]
                name = finally_data["name"]
                talk_name = finally_data["talk_name"]
		logging.warning(self.single_chat_list)
		name_to_talk_list = map(lambda x:(str(x["name"]),str(x["talk_name"])),self.single_chat_list)
		if (name,talk_name) in name_to_talk_list:
			single_talk_index = name_to_talk_list.index((name,talk_name))
			talk_info = self.single_chat_list[single_talk_index]
		if msg == "logout":
			self.single_chat_list.pop(single_talk_index)	
			self.sock.close()
			return
		self.single_chat_list[single_talk_index]["msg_list"].append(msg)
		return_talk = {"chat_type":"single","name":name,"msg":msg,"talk_name":talk_name}
		if sock_list.has_key(talk_name):
			talk_name_group_sock = sock_list[talk_name]
			WebSocket.send(talk_name_group_sock, json.dumps(return_talk))
		if (talk_name,name) in name_to_talk_list:
			talk_name_to_name = name_to_talk_list.index((talk_name,name))
			talk_sock = self.single_chat_list[talk_name_to_name]["name_sock"]
			WebSocket.send(talk_sock, json.dumps(return_talk))
		logging.warning(self.single_chat_list)
		WebSocket.send(talk_info["name_sock"], json.dumps(return_talk))
