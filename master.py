import socket
import threading

def handle_client(sock, addr):
	global system_state

	try:
		confirmar = False
		raw = sock.recv(1024)
		if not raw:
			return

		dados = raw.decode('utf-8')
		if dados.split(' ')[0] == 'QUERO_PUBLICAR':
			system_state[dados.split(' ')[1]] = addr[0] + ':' + dados.split(' ')[2]
			sock.send('OK_REGISTRADO'.encode())
		if dados.split(' ')[0] == 'QUEM_PUBLICA' :
			topico = dados.split(' ')[1]
			if topico in system_state:
				sock.send(system_state[topico].encode())
			else:
				sock.send('ERRO:NAO_ENCONTRADO'.encode())
	finally:
		sock.close()

if __name__ == '__main__':
	system_state = {}

	ros_master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ros_master.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	ros_master.bind(('127.0.0.1', 8000))
	ros_master.listen(5)

	try:
		while True:
			sock, addr = ros_master.accept()
			thread = threading.Thread(target = handle_client, args = (sock, addr))
			thread.start()

	finally:
		ros_master.close()
