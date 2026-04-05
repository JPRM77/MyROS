import socket
import threading

def subscribing (client, callback):
	try:
		while True:
			raw = client.recv(1024)
			if not raw:
				break

			dados = raw.decode('utf-8')
			callback(dados)
	finally:
		client.close()


class Node:
	def __init__ (self, name):
		self.node_name = name
		self.ip_master = ('127.0.0.1',8000)

		# Node server configuration:
		self.node_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.node_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		self.node_server.bind(('127.0.0.1', 0))
		self.node_ip = self.node_server.getsockname()
		self.node_server.listen(20)
		# Node characteristics
		self.topic_confirmation = {}
		self.subscribers_list  = {}

	def register_topic (self, topic_name):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.connect(self.ip_master)
		sock.send('QUERO_PUBLICAR {} {}'.format(topic_name, self.node_ip[1]).encode('utf-8'))
		dados = sock.recv(1024).decode('utf-8')
		if dados == 'OK_REGISTRADO':
			self.topic_confirmation[topic_name] = True
		else:
			self.topic_confirmation[topic_name] = False
		sock.close()

	def lookup_topic (self, topic_name):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.connect(self.ip_master)
		sock.send('QUEM_PUBLICA {}'.format(topic_name).encode('utf-8'))
		dados = sock.recv(1024).decode('utf-8')
		sock.close()
		return dados


	def accept_subscribers (self, topic_name):
		self.subscribers_list[topic_name] = []
		while True:
			sock, addr = self.node_server.accept()
			self.subscribers_list[topic_name].append(sock)


	def publisher (self, topic_name):
		thread = threading.Thread(target = self.accept_subscribers, args = (topic_name, ))
		thread.start()

	def publish(self, topic_name, msg):
		for i in self.subscribers_list[topic_name]:
			try:
				i.send(msg.encode('utf-8'))
			except:
				self.subscribers_list[topic_name].remove(i)


	def Subscriber (self, topic_name, callback):
		ip_pub = self.lookup_topic(topic_name)
		sub = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sub.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sub.connect((ip_pub.split(':')[0], int(ip_pub.split(':')[1])))
		thread = threading.Thread(target = subscribing, args = (sub, callback))
		thread.start()


	def close_node (self):
		self.node_server.close()
