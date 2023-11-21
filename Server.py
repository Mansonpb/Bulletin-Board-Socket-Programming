import socket
import threading
import datetime

# Data structures to store user information and messages
users = []
messages = []
groups = {"Public": [], "Group1": [], "Group2": [], "Group3": [], "Group4": [], "Group5": []}


# Function to handle client connections
def handle_client(client_socket, username):
    try:
        join_group(username, "Public")                                              #auto join to public group - Trysten
        welcome_message = f"{username}, type 'help' for a list of commands.\n"
        client_socket.send(welcome_message.encode('utf-8'))

        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break

            process_client_data(client_socket, username, data)

    except ConnectionResetError:
        print(f"Connection with client {username} reset.")
    except Exception as e:
        print(f"Error handling client {username}: {e}")

    finally:
        remove_user(username)
        client_socket.close()

# Function to process client data
def process_client_data(client_socket, username, data):
    if data.startswith('post'):
        _, message = data.split(' ', 1)
        post_message(client_socket, username, message)
    elif data.startswith('list'):
        group = data.split(' ', 1)[1].strip()
        display_user_list(client_socket, group)
    elif data.startswith('get'):
        message_id = data.split(' ', 1)[1].strip()
        get_message(client_socket, message_id)
    elif data.startswith('leave'):
        leave_group(client_socket,username)
    elif data.startswith('join'):
        _, group = data.split(' ', 1)

        response = join_group(client_socket,username, group)
        client_socket.send(response.encode('utf-8'))
    elif data.startswith('help'):
        help_message = "Available commands:\npost <message>\nlist <group>\nget <message_id>\nleave\njoin <group>\n"
        client_socket.send(help_message.encode('utf-8'))
    else:
        client_socket.send("Invalid command. Type 'help' for a list of commands.".encode('utf-8'))

# Function to post a message to the user's current group
def post_message(client_socket,sender, message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message_data = f"{len(messages) + 1}, {sender}, {timestamp}, {message}"
    messages.append(message_data)

    user_group = find_user_group(sender)
    

    broadcast_message(client_socket,sender, user_group, message_data)

# Function to find the group of a user
def find_user_group(username):
    for group, members in groups.items():
        if username in members:
            return group
    return None

# Function to leave a specific group
def leave_group(client_socket,username):
    group = find_user_group(username)
    if group:
        groups[group].remove(username)
        broadcast_message(client_socket,"Server", group, f"{username} left the group.")
        return f"You left {group}."
    else:
        return "You are not in any group."

# Function to broadcast messages to all clients in a group
def broadcast_message(client_socket,sender, group, message_data):
    print(f"Broadcasting message from {sender} in group {group}: {message_data}")
    if group in groups:
        for username, client_socket in users:
            try:
                client_socket.send(f"{message_data}\n".encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting message to user {username}: {e}")

# Function to add a new user to the server and place them in the public group
def add_user(client_socket,username):
    users.append((username,client_socket))
    groups["Public"].append(username)
    broadcast_message(client_socket,"Server", "Public", f"{username} joined the group.")

# Function to join a user to a group
def join_group(client_socket,username, group):
    if group in groups:
        groups[group].append(username)
        broadcast_message(client_socket,"Server", group, f"{username} joined the group.")
        return f"You joined {group}."
    else:
        return f"Invalid group. Use 'list <group>' to see available groups."

# Function to remove a user from the server
def remove_user(username):
    for user_info in users:
        if user_info[0] == username:
            users.remove(user_info)
            break

    for group in groups.values():
        if username in group:
            group.remove(username)

# Function to display the list of users in a group
def display_user_list(client_socket, group):
    if group in groups:
        user_list = ', '.join(groups[group])
        client_socket.send(f"Users in {group}: {user_list}".encode('utf-8'))
    else:
        client_socket.send("Invalid group. Use 'list <group>' to see available groups.".encode('utf-8'))

# Function to get the content of a message
def get_message(client_socket, message_id):
    try:
        message_id = int(message_id)
        if 1 <= message_id <= len(messages):
            message_data = messages[message_id - 1]
            client_socket.send(message_data.encode('utf-8'))
        else:
            client_socket.send("Invalid message ID.".encode('utf-8'))
    except ValueError:
        client_socket.send("Invalid message ID. Must be an integer.".encode('utf-8'))

# Function to leave a group
def leave_group(username, group):           #added client socket and group -trysten
    if group != "Public":                   #if the request group to leave is not "public", continue
       for g in groups.values():            #loop through all group values trying to match the desired group to leave. Current implimentation does access public group, so must check for public again.
            if username in g:               #if username is in the group (g), proceed
                if g != "Public":           #now the group is checked again to make sure it isn't the public group
                    if g == group:          #checking if (g) is the desired group to leave
                        g.remove(username)  #if not public, remove
                        return f"You have left {group}!"
    else:
        return f"You cannot leave the Public bulletin!"

# Main server loop
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))
    server.listen(5)
    print("Server listening on port 9999...")

    try:
        while True:
            client_socket, addr = server.accept()
            print(f"Accepted connection from {addr}\n")

            username = client_socket.recv(1024).decode('utf-8')

            add_user(client_socket,username)

            client_socket.send('Welcome to the public message board!\n'.encode('utf-8'))

            # Start a thread to handle the client
            client_handler = threading.Thread(target=handle_client, args=(client_socket, username))
            client_handler.start()

    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server.close()

if __name__ == "__main__":
    main()
