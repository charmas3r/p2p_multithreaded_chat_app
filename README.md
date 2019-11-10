# p2p_multithreaded_chat_app
## Project Objective
In this project, you will develop a console-based client-server application that implements a
simplified chat application using socket programming in Python3. The implemented application
will have one single server and multiple clients.
### 1. Server initialization
In this program, the server is listening to the requests from clients. You may start with the
simple example given above. Use TCP for the transport layer. First run the server program on a
machine with IP address x.x.x.x. Now the server is listening and ready to accept registration
requests from the clients.
### 2. Client initialization
In this program, multiple clients will connect to the server. Once connected the server, each
client can request a chat with another client through the server. If accepted, they can start
chatting. Run a client program on another machine and specify x.x.x.x as the server’s IP
address. The server is listening and accepts the connection request from the client.
Note that for simplicity you can initially test your program on the same machine. Open a
terminal for the server and then open other terminals on the same machine and run the clients.
In that case, the server is localhost.
### 3. Initial Client log in
The client program should prompt the user to enter her/his username to connect to the server.
Then the server checks the entered username with the list of taken usernames at the server.
• If the username has already been taken, the server prompts the user to enter another
username.
• If the username has NOT been taken, the server then stores the client’s information
including username, client socket descriptor, and IP address. The information of the clients
can be stored in a file (or a list of JSONs or dictionary in Python) at the server.
### 4. Successful login
After successful login, the following menu should be displayed in the client’s console:
1. List users
2. Chat
3. Exit
Enter your choice: (Client enters 1, 2 or 3) 
### 5. List
If the choice is 1, the list of all current clients should be displayed. The list should also
demonstrate whether each client is available to chat. For example, assume users A, B and C
have already registered their usernames at the server, and A and B are currently chatting. When
user D registers at the server and requests the list of users, it should display the following list
and then the menu.
If there are no other client has registered at the server, you may display a message “No other
client.” The menu should be displayed again after that.
A client is identified with a particular username. Each client can open only one shell to chat
with other clients. Once the client enters choice 3 (Exit), she/he will be removed from the
server’s list and terminates its program.
### 6. Exit
If the choice is 3 (Exit), the client program should inform the server to remove this client from
the list of users and the client program terminates.
### 7. Chat
If the client selected item 2 (Chat), the available clients (apart from the ones currently in
conversation with) should be displayed and the user should be asked to enter the username of
one of those clients. Suppose there are four clients A, B, C and D. D requests to chat. If A and
B are busy chatting together, they should not be displayed for D as available users.
If no other clients are available for chat, the message “No clients to chat” should be displayed
followed by the menu.
Assume D requests to chat. The client’s program at D displays the list of available users. Only C
is available. Only C will be displayed as the list of available users. Then the client’s program
asks the user to enter the name of an available user to chat. If the client enters anything other
than C, the program will display the list of available users again and ask the client to enter an
available username.
If client D enters C, the request is sent to the server. The server informs client C that client D
has requested to chat with it. Prompt a question to client C whether she/he accepts the
invitation or not.
User Available/busy
A Chatting with B
B Chatting with A
C Available
If client C denied the invitation, prompt proper messages to C and D followed by the menu.
If Client C accepted the invitation, a chat session is established by the server. the server stores a
record for this session as an active session and changes the status of both parties to “busy”. They
will not be shown as available for chat anymore. Now C and D exchange messages through the
server in this chat session. Prompt a welcome message for both clients and inform them that
they can terminate the chat session if they enter the special message “Quit”. If one client entered
“Quit”, they both get a message “Chat session ended” followed by the menu.
Note: If clients A and B are chatting, clients C and D should be able to chat in parallel.
The format of messages is as following.
Sender: message.
Important note: Display all the exchanged messages on the server. Also, for each request arrives
at the server and each action the server takes (e.g. when the server changes the status of clients
from available to busy or establishes a chat session), prompt a proper message on the server
terminal.
### 8. Extra credit: Group chat
The menu contains a fourth item: 4. Group chat
For group chat, more than one client must be available to chat. For example, assume client D
selects item 4. Currently clients A, B, and C are available. The list of group chat options will
show up as the following:
Then client D can select one of the 4 groups. Assume D selects group 1. Then A and B will be
informed that client D would like to start a group chat with them. If both A and B accepted the
invitation, a group chat session will be established through the server between these three
clients. If any of A or D denied the invitation, the group chat will not be established. Prompt
proper messages for all involved clients followed by the menu. 
