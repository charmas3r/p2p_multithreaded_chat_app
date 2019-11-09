from socket import *
import threading
buffer_size = 2048
connected = False
client_name = ""

# Created by Evan Smith on 11/8
#
#
# The high level idea of this client is that it is a dummy client.
# The client has no logic about the information sent to the server
# And the response logic is also handled by the server. The client
# uses two threads, one for sending and one for receiving.


def main():
    initiate_connection_and_threads()
    try:
        while True:
            if not connected:
                print("Error: No longer connected. Safe to close program.")
                break
    except (KeyboardInterrupt, SystemExit):
        print("Error: Exception on main thread")


def sending_thread(sock, ip_addr):
    try:
        while 1:
            if len(client_name) < 1:
                msg = input()
            else:
                msg = input(client_name + ": ")
            sock.send(msg.encode())
    except:
        global connected
        connected = False
        print("Error: Exception on send thread")
        exit(1)


def receiving_thread(sock, ip_addr):
    global connected
    global client_name
    try:
        while 1:
            msg = sock.recv(buffer_size)
            if len(msg) < 248:
                if "FORCE_EXIT" in msg.decode():
                    connected = False
                    print("Error: Connection terminated by server")
                    exit(1)
                elif "NOT_CHAT" in msg.decode():
                    client_name = ""
                elif "IN_CHAT" in msg.decode():
                    str_list = msg.decode().split(':')
                    client_name = str_list[1]
                else:
                    print(msg.decode())
            else:
                print("Error: message too long")
    except:
        connected = False
        print("Error: Exception on receiving thread")
        exit(1)


def initiate_connection_and_threads():
    server_name = '127.0.0.1'
    server_port = 12000
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_name, server_port))
    send_thread = threading.Thread(target=sending_thread, args=(client_socket, server_name))
    send_thread.start()
    recv_thread = threading.Thread(target=receiving_thread, args=(client_socket, server_name))
    recv_thread.start()
    global connected
    connected = True


if __name__ == "__main__":
    main()

