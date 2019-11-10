from socket import *
import threading
buffer_size = 2048

# ======================================================
# Created by Evan Smith on 11/8
#
#
# The high level idea of this client is that it is a dummy client.
# The client has no logic about the information sent to the server
# And the response logic is also handled by the server. The client
# uses two threads, one for sending and one for receiving.
# ======================================================


# ======================================================
# Main driving function for Chat client. Thread creation
# and initialization is the first task performed. The chat
# client is constantly listening aware of it's connection
# status to the server to handle errors appropriately.
# ======================================================
def main():
    initiate_connection_and_threads()
    try:
        while True:
            if not connected:
                print("Error: No longer connected. Safe to close program.")
                break
    except (KeyboardInterrupt, SystemExit):
        print("Error: Exception on main thread")


# A single thread is used for sending messages.
def sending_thread(sock, ip_addr):
    try:
        while 1:
            msg = input()
            sock.send(msg.encode())
    except:
        global connected
        connected = False
        print("Error: Exception on send thread")
        exit(1)


# A single thread is used for receiving messages.
def receiving_thread(sock, ip_addr):
    global connected
    try:
        while 1:
            msg = sock.recv(buffer_size)
            if len(msg) < 248:
                # special command indicating client should terminate
                if "FORCE_EXIT" in msg.decode():
                    connected = False
                    print("Error: Connection terminated by server")
                    exit(1)
                else:
                    print(msg.decode())
            else:
                print("Error: message too long")
    except:
        connected = False
        print("Error: Exception on receiving thread")
        exit(1)


# Thread initiation and creation.
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