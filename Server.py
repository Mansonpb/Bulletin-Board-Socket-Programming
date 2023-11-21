import socket
import threading
import datetime

# Data structures to store user information and messages
users = []
messages = []
groups = {"Group1": [], "Group2": [], "Group3": [], "Group4": [], "Group5": []}

# Function to handle client connections
def handle_client(client_socket, username):
    try:
        welcome_message = f"Welcome, {username}!\nType 'help' for a list of commands."
        client_socket.send(welcome_message.encode('utf-8'))

        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break

            process_client_data(client_socket, username, data)

    except Exception as e:
        print(f"Error handling client {username}: {e}")

    finally:
        remove_user(username)
        client_socket.close()

# Function to process client data
def process_client_data(client_socket, username, data):
    if data.startswith('post'):
        _, group, message = data.split(' ', 2)
        post_message(username, group, message)
    elif data.startswith('list'):
        group = data.split(' ', 1)[1].strip()
        display_user_list(client_socket, group)
    elif data.startswith('get'):
        message_id = data.split(' ', 1)[1].strip()
        get_message(client_socket, message_id)
    elif data.startswith('join'):
        _, group = data.split(' ', 1)
        response = join_group(username, group)
        client_socket.send(response.encode('utf-8'))
    elif data.startswith('leave'):
        leave_group(username)
    elif data.startswith('help'):
        help_message = "\nAvailable commands:\njoin <group>\npost <group> <message>\nlist <group>\nget <message_id>\nleave\n\n"
        client_socket.send(help_message.encode('utf-8'))
    else:
        client_socket.send("Invalid command. Type 'help' for a list of commands.".encode('utf-8'))

# Function to post a message to a group
def post_message(sender, group, message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message_data = f"{len(messages) + 1}, {sender}, {timestamp}, {message}"
    messages.append(message_data)

    if group in groups:
        groups[group].append(len(messages))

    broadcast_message(sender, group, message_data)

# Function to join a user to a group
def join_group(username, group):
    if group in groups:
        groups[group].append(username)
        broadcast_message("Server", group, f"{username} joined the group.")
    else:
        return f"Invalid group. Use 'list <group>' to see available groups."

# Function to broadcast messages to all clients in a group
def broadcast_message(sender, group, message_data):
    if group in groups:
        for user_socket in groups[group]:
            try:
                user_socket.send(message_data.encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting message to user: {e}")

# Function to add a new user to the server
def add_user(username):
    users.append(username)

# Function to remove a user from the server
def remove_user(username):
    if username in users:
        users.remove(username)

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
def leave_group(username):
    for group in groups.values():
        if username in group:
            group.remove(username)

# Main server loop
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))
    server.listen(5)
    print("Server listening on port 9999...")

    try:
        while True:
            client_socket, addr = server.accept()
            print(f"Accepted connection from {addr}")

            username = client_socket.recv(1024).decode('utf-8')
            add_user(username)

            client_socket.send('Welcome to the public message board!'.encode('utf-8'))

            # Start a thread to handle the client
            client_handler = threading.Thread(target=handle_client, args=(client_socket, username))
            client_handler.start()

    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server.close()

if __name__ == "__main__":
    main()
