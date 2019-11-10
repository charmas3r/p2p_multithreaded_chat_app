import socket
import threading
import enum

SHOW_USER_LIST = '1'
PRIVATE_CHATTING = '2'
GROUP_CHATTING = '3'
EXIT = '4'
QUIT = 'Quit'
FORCE_EXIT = "FORCE_EXIT"
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 12000
BUFFER_SIZE = 2048
THREAD_LIMIT = 100

active_clients = {}
database = {}

# ======================================================
# Created by Evan Smith on 11/9
#
#
# The high level idea of this server is that it contains
# all the logic for chat server. All messages are sent
# from server and client blindly displays them. This means
# that this server class contains all parsing and options
# about how messages are shown. The server also keeps
# track of all the users currently on the chat server
# and a database of connections and user objects.
#
# The server uses a state machine to route messages. A basic
# example is this. If a user in "Idle" mode he/she can login
# and see the menu. This means that any message that comes in
# while the user is in this state will be routed accordingly.
# This enables more sophisticated logic to be implemented by the
# server, and helps keep the client code clean of any logic. Finally
# it also helps show correct "availability" of these users.
# ======================================================


# Enum class represents states the user can be in during the chat app.
# Messages are routed based on this state.
class UserState(enum.Enum):
    Idle = 1
    Requesting = 2
    Requested = 3
    Chatting = 4
    GroupChatting = 5

    def __str__(self):
        return '%s' % self.value


# User class which represents has some basic attributes
class User:
    def __init__(self, username, availability, connection, address, login_status, state):
        self.username = username
        self.availability = availability
        self.connection = connection
        self.address = address
        self.login_status = login_status
        self.state = state


# This function receives the messages. Messages are received in an endless loop
# and then sent to the message router for logic parsing. Upon connection, a
# user object is created for each connecting thread and a welcome message sent
def handle_client(connection, address):
    print("%s:%s has connected" % address)
    database[connection] = User("this", "available", connection, address, False, UserState.Idle)
    send_welcome(connection)
    try:
        while True:
            message = connection.recv(BUFFER_SIZE)
            message_router(message, connection)
    except:
        pass
    finally:
        connection.close()


# This is the main routing mechanism for the application. First, a user object
# is created based on the connection and based on the state of that user
# object, the message is routed appropriately.
def message_router(message, connection):
    # since thread is alive a user object will always will return current user
    user = database[connection]
    if user.state is UserState.Requesting:
        user_requesting_state_func(user, message, connection)
    elif user.state is UserState.Requested:
        user_requested_state_func(user, message, connection)
    elif user.state is UserState.Chatting:
        user_chatting_state_func(user, message)
    elif user.state is UserState.GroupChatting:
        user_group_chatting_state_func(user, message, connection)
    else:
        user_idle_state_func(user, message, connection)


# Handles all "idling" functionality which includes authentication
# and menu routing.
def user_idle_state_func(user, message, connection):
    if not user.login_status:
        user.username = message.decode()
        username_validation(user, connection)
    else:
        if message.decode() == SHOW_USER_LIST:
            show_user_list(connection)
        elif message.decode() == PRIVATE_CHATTING:
            initiate_private_chat(user, connection)
        elif message.decode() == GROUP_CHATTING:
            initiate_group_chat(user, connection)
        elif message.decode() == EXIT:
            remove_connection(connection)
        else:
            send_general_error(connection)


# Basic group chatting state. Users in a group chat broadcast
# their messages to all other people in the chat. Their name
# is prepended to the message. 'Quit' exits the chat.
def user_group_chatting_state_func(user, message, connection):
    if message.decode() == QUIT:
        exit_user_from_group_chat(user)
    else:
        formatted_chat_message = user.username + ": " + message.decode()
        broadcast_message_for_group_chat(formatted_chat_message, connection, False)


# Private chatting state. Users in a private chat send their
# message to one other person (who has previously accepted the request).
# For this implementation, the other user's username is stored in the
# 'availability' field of the user. In future implementation it should
# be stored as a seperate variable. The sender's name is prepended to
# the chat and.
def user_chatting_state_func(user, message):
    temp_str_list = user.availability.split()
    other_user = get_user_from_name(temp_str_list[2])
    if message.decode() == QUIT:
        users_available(user, other_user)
        send_chat_end_to_users(user.connection, other_user.connection)
        send_menu(other_user.connection)
        send_menu(user.connection)
    else:
        formatted_chat_message = user.username + ": " + message.decode()
        send_user_to_user_message(user, other_user, formatted_chat_message)


# Requested state function. This state represents the user state when
# requested to chat from another user. In this state, the user can
# either choose to accept or decline the request. If the user
# accepts then the user is set to chatting state and the chat headers
# are sent. If the user declines, the user is put back into Idle mode,
# a rejection message sent, and menus sent to both users
def user_requested_state_func(user, message, connection):
    temp_str_list = user.availability.split()
    request_user = get_user_from_name(temp_str_list[2])
    if message.decode().lower() == 'y':
        # formally begin chatting
        user.state = UserState.Chatting
        request_user.state = UserState.Chatting
        send_chat_header(request_user, user, connection)
        send_chat_header(user, request_user, request_user.connection)
    elif message.decode().lower() == 'n':
        # send rejection message to user
        user.state = UserState.Idle
        request_user.state = UserState.Idle
        send_rejection_message(user, request_user.connection)
        send_menu(request_user.connection)
        send_menu(connection)
    else:
        # error message
        send_general_error(connection)


# Requesting state function. When a user is requesting to chat with
# with another user, their availability should be changed and
# a request message sent to the other user.
def user_requesting_state_func(user, message, connection):
    # current user in a state where they are requesting to chat with another user
    requested_user = get_user_from_name(message.decode())
    # turn off availability
    if requested_user is not None:
        user.availability = "chatting with " + requested_user.username
        requested_user.availability = "chatting with " + user.username
        requested_user.state = UserState.Requested
        send_request_waiting(requested_user, connection)
        request_message = "\nUser " + user.username + " is requesting to chat with you. Y/N?"
        send_user_to_user_message(user, requested_user, request_message)
    else:
        send_general_error(connection)


# User specific function which sends chat header, broadcasts welcome message,
# changes user state, and availability.
def initiate_group_chat(user, connection):
    if len(database) > 1:
        send_group_chat_header(connection)
        send_group_chat_welcome(connection)
        user.state = UserState.GroupChatting
        user.availability = "In group chat"
    else:
        send_single_user_warning(connection)
        send_menu(connection)


# User specific private chat initiation function. If the user is not
# only active client then private chat is ok. A source of confusion
# could be the user state is Requesting when we are beginning the
# chat sequence. This is because it is the first step in the process
# of private chatting.
def initiate_private_chat(user, connection):
    if len(database) > 1:
        user.state = UserState.Requesting
        send_user_list(connection)
        send_chat_request(connection)
    else:
        send_single_user_warning(connection)
        send_menu(connection)


# Shows the active user list to the user if the user is not the
# only active client. Otherwise, the user receives the single-user
# warning and a menu is sent.
def show_user_list(connection):
    if len(active_clients) > 1:
        send_user_list(connection)
        send_menu(connection)
    else:
        send_single_user_warning(connection)
        send_menu(connection)


# Group message broadcasting function.
# @param all_flag a flag sent to the function. If true it will
# broadcast message to all users. Otherwise, if the flag is false
# the message will be broadcasted to all users except the sending user.
def broadcast_message_for_group_chat(message, connection, all_flag):
    if ":" in message:
        tmp_list = message.split(':')
        print(username_from_connection(connection) + " is broadcasting '" + tmp_list[1] + "'")
    # sends to all except client
    if not all_flag:
        for key, value in active_clients.items():
            if value in database and value is not connection:
                if database[value].state == UserState.GroupChatting:
                    value.send(message.encode())
    # send to all including client
    else:
        for key, value in active_clients.items():
            if value in database:
                if database[value].state == UserState.GroupChatting:
                    value.send(message.encode())


# Retrieves username from database for a connection
def username_from_connection(connection):
    if connection in database:
        return database[connection].username


# Exits user from group chat
def exit_user_from_group_chat(user):
    print(user.username + " has left the group chat")
    user.state = UserState.Idle
    user.availability = "Available"
    send_menu(user.connection)


# Utility function for stripping username in chat messages
def format_incoming_msg(message):
    # strip off chat prefix
    format_msg_list = message.split(':')
    return format_msg_list[1]


# Database retrieval and sends user list to connection
def send_user_list(connection):
    send_user_list_header(connection)
    print(username_from_connection(connection) + " requested current user list. See below: ")
    for key, value in active_clients.items():
        user_list = ""
        if value in database:
            temp_user = database[value]
            if key == temp_user.username:
                user_list += "\t" + temp_user.username + "\t\t" + str(temp_user.availability) \
                            + "\t\t" + str(temp_user.login_status) + "\n"
                connection.send(user_list.encode())
                print(user_list)


# Utility function used in server side logging
def get_user_from_name(username):
    if username in active_clients:
        conn = active_clients[username]
        if conn in database:
            return database[conn]


# Non-user specific function to change users who were in private
# message to an available state
def users_available(user, other_user):
    print(user.username + " has become available to chat with")
    print(other_user + " has become available to chat with")
    user.state = UserState.Idle
    other_user.state = UserState.Idle
    user.availability = "Available"
    other_user.availability = "Available"


# This function performs the username validation for the chat app.
# User is allowed to pick any name that is not currently in use and is
# not an empty string. Upon validation of unique name, the login status
# is set and menu sent to the client.
def username_validation(user, connection):
    if user.username == '':
        print("Error: Validation not successful for " + user.username)
        response = "Error: Username cannot be empty. Please choose another: "
        connection.send(response.encode())
    else:
        if user.username in active_clients:
            print("Error: Validation not successful for " + user.username)
            response = "Error: Username already taken. Please choose another: "
            connection.send(response.encode())
        else:
            print("Success, validated username for " + user.username)
            active_clients[user.username] = connection
            user.login_status = True
            user.availability = "Available"
            response = "Login successful."
            connection.send(response.encode())
            send_menu(connection)


# This function deletes a connection from both active user dictionary
# and the main database of Users. A special command "FORCE_EXIT" is
# sent to the client which signals that it is ok for them to disconnect
# from server.
def remove_connection(connection):
    for key, value in active_clients.items():
        if value in database:
            temp_user = database[value]
            if connection in database:
                del database[connection]
                del active_clients[temp_user.username]
                print("deleted " + temp_user.username + "'s records from server")
                message = FORCE_EXIT
                connection.send(message.encode())
                connection.close()


# ========================================================
# Below represent the simple chat server template messages
# which are sent to the client to display.
# ========================================================

def send_group_chat_header(connection):
    print(username_from_connection(connection) + " is entering the group chat")
    header = "\n\n**** Group Chat ****\n\n"
    connection.send(header.encode())


def send_group_chat_welcome(connection):
    welcome_message = "\n*** " + username_from_connection(connection) + " has joined the chat ***\n"
    broadcast_message_for_group_chat(welcome_message, connection, True)


def send_general_error(connection):
    print("invalid input from " + username_from_connection(connection))
    error_message = "\nInvalid input, try again\n"
    connection.send(error_message.encode())


def send_chat_end_to_users(connection, other_connection):
    print("Exiting chat for " + username_from_connection(connection))
    end_message = "chat session ended"
    connection.send(end_message.encode())
    other_connection.send(end_message.encode())


def send_rejection_message(user, connection):
    print("Sent chat rejection message to " + user.username)
    rejection_message = "\n " + user.username + " has denied the chat."
    connection.send(rejection_message.encode())


def send_chat_header(user, other_user, connection):
    header = '\n\n**** Private Chat with ' + user.username + " ****\n\n"
    connection.send(header.encode())


def send_welcome(connection):
    welcome = '\nWelcome to the chat server!\n\nEnter a username for yourself: '
    connection.send(welcome.encode())


def send_menu(connection):
    menu = "\n\n1. List users\n2. Chat\n3. Group Chat\n4. Exit\n\nEnter your choice: "
    connection.send(menu.encode())


def send_single_user_warning(connection):
    print("Sent single user warning to " + username_from_connection(connection))
    warning = '\nYou are the only person in this server\n'
    connection.send(warning.encode())


def send_request_waiting(user, connection):
    print("Sent wait request to " + username_from_connection(connection))
    wait_message = '\nWaiting for ' + user.username + ' to accept your invitation. Please wait.\n'
    connection.send(wait_message.encode())


def send_chat_request(connection):
    print(username_from_connection(connection) + " is requesting a private chat")
    message = '\nEnter the name of the person you would like to chat with: '
    connection.send(message.encode())


def send_user_list_header(connection):
    user_list_header =  "\n\n------------------------------------------------------------------------------------\n"
    user_list_header += "\tusername\tavailability\t\tlogin status\t\n"
    user_list_header += "------------------------------------------------------------------------------------\n"
    connection.send(user_list_header.encode())


# Function used in private messaging between two parties.
def send_user_to_user_message(current_user, requested_user, message):
    print(current_user.username + " sent message: \n" + message + "\nto " + requested_user.username)
    requested_user.connection.send(message.encode())


# ======================================================
# Main driving function for the chat server. The server
# binds creates up to 100 user threads, and is constantly
# listening for connections. For debugging purposes the
# server IP and port are set to 0.0.0.0 and 12000.
# ======================================================

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(THREAD_LIMIT)
    print("Server initialization is complete. Chat server listening for connections.")
    while True:
        client_connection, addr = s.accept()
        thread = threading.Thread(target=handle_client, args=(client_connection, addr))
        thread.start()


if __name__ == '__main__':
    main()
