import socket
import threading
import datetime
import sys # for the exit function

# Data structures to store user information and messages
users = []
messages = []
groups = {"Public": [], "Group1": [], "Group2": [], "Group3": [], "Group4": [], "Group5": []}

# Data structure to store last two messages for each group
last_two_messages = {"Public": ["", ""], "Group1": ["", ""], "Group2": ["", ""], "Group3": ["", ""], "Group4": ["", ""], "Group5": ["", ""]}

# Function to handle client connections
def handle_client(client_socket, username):
    try:
        #join_group(client_socket, username, "Public")                                              #auto join to public group - Trysten
        #broadcast_message(client_socket,"Server", "Public", f"{username} joined the public bulletin.\n")
        client_socket.send(f"Welcome to the server {username}!\n".encode('utf-8'))
        print_groups(client_socket)
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

#function to disconnect from the server and exit the client program
def exit(client_socket, username):
    try:
        client_socket.send("exit".encode('utf-8')) #notifies the server that the client is exiting
    except Exception as e:
        print(f"Error sending exit signal to server for client {username}: {e}")
    finally:
        remove_user(username)
        client_socket.close()
        print(f"Disconnected from the server.  Exiting {username}'s client program.")
        sys.exit(0) # exits the program

# Function to process client data
def process_client_data(client_socket, username, data):
    if data.startswith('post'):
        _, *rest = data.split(' ', 1)

        if len(rest) < 1:
            client_socket.send("Invalid 'users' command. Use 'users <group>'.\n".encode('utf-8'))
            return
        message = rest[0].strip()
        post_message(client_socket, username, "Public", message)
    elif data.startswith('grouppost'):
        _, *rest = data.split(' ', 2)

        if len(rest) < 2:
            client_socket.send("Invalid 'post' command. Use 'post <group> <message>'.\n".encode('utf-8'))
            return
        group, message = rest
        post_message(client_socket, username, group, message)
    elif data.startswith('groupusers'):
        _, *rest = data.split(' ', 1)

        if len(rest) < 1:
            client_socket.send("Invalid 'users' command. Use 'users <group>'.\n".encode('utf-8'))
            return

        group = rest[0].strip()
        display_user_list(client_socket, group)
    elif data.startswith('users'):
        display_user_list(client_socket, "Public")
    elif data.startswith('groupmessage'):
        _, *rest = data.split(' ', 2)

        if len(rest) < 2:
            client_socket.send("Invalid 'post' command. Use 'post <group> <message>'.\n".encode('utf-8'))
            return
        group, message_id = rest
        get_message(client_socket, message_id)  
    elif data.startswith('getmessage'):
        _, *rest = data.split(' ', 1)

        if len(rest) < 1:
            client_socket.send("Invalid 'getmessage' command. Use 'getmessage <message_id>'.\n".encode('utf-8'))
            return

        message_id = rest[0].strip()
        get_message(client_socket, message_id)
    elif data.startswith('leave'):                                   
        response = leave_group(username, "Public")    #added client socket so we could output a message if trying to leave public in the leave_group function - Trysten
        client_socket.send(response.encode('utf-8'))
    elif data.startswith('groupleave'):                                      
        _, *rest = data.split(' ', 1)

        if len(rest) < 1:
            client_socket.send("Invalid 'leave' command. Use 'leave <group>'.\n".encode('utf-8'))
            return

        group = rest[0].strip()
        response = leave_group(username, group)    #added client socket so we could output a message if trying to leave public in the leave_group function - Trysten
        client_socket.send(response.encode('utf-8'))
    elif data.startswith('join'):           
        response = join_group(client_socket,username, "Public")
        client_socket.send(response.encode('utf-8'))
    elif data.startswith('groupjoin'):
        _, *rest = data.split(' ', 1)

        if len(rest) < 1:
            client_socket.send("Invalid 'join' command. Use 'join <group>'.\n".encode('utf-8'))
            return

        group = rest[0].strip()
        response = join_group(client_socket,username, group)
        client_socket.send(response.encode('utf-8'))
    elif data.startswith('grouplist'):
        print_groups(client_socket)
    elif data.startswith('help'):
        help_message = (
            "\nAvailable commands:\n"
            "post <message> - Post a message to the public board.\n"
            "users - Display the list of users in the public.\n"
            "getmessage <message_id> - Get the content of the message with the specified ID.\n"
            "leave - Leave the public chat.\n" 
            "join - Join the public chat.\n" 
            "help - Gives a list of commands\n"
            "exit - Disconnects from the server and exits client program\n"
            "grouplist - Display the list of available groups.\n"
            "groupjoin <group> - Join the specified group.\n"
            "grouppost <group> - Post a message to a specified group.\n"
            "groupusers <group> - Display the list of users in the specified group.\n"
            "groupleave <group> - Leave the specified group.\n"
            "groupmessage <group> <message_id> - Get the content of the message with the specified ID and group.\n"
        )
        client_socket.send(help_message.encode('utf-8'))
    elif data.startswith('exit'):
        print(f"Disconnecting from Server and exiting client program!")
        exit(client_socket, username)
    else:
        client_socket.send("Invalid command. Type 'help' for a list of commands.".encode('utf-8'))


# Function to post a message to the user's current group
def post_message(client_socket,sender,group_ID, message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    

    # Check if the group exists
    if group_ID not in groups:
        try:
            if 1 <= int(group_ID) <= 5:
                group = "Group" + group_ID
                # print(group)
                # group = groups[str(group_ID)]
                # Check if the user is a member of the group
                if sender not in groups[group]:
                    client_socket.send(f"You are not a member of {group}. Use 'join {group}' to join the group.\n".encode('utf-8'))
                    return
                    # Check if the message is empty
                if not message.strip():
                    client_socket.send("Message cannot be empty. Please try again.\n".encode('utf-8'))
                    return
                message_data = f"{len(messages) + 1}, {sender}, {timestamp}, <{group}> {message}"
                messages.append(message_data)
                last_two_messages[group] = [last_two_messages[group][1], message_data]
                broadcast_message(client_socket,sender, group, message_data)
                return
        except ValueError:
            client_socket.send(f"Invalid group '{group_ID}'. Use 'grouplist' to see available groups.\n".encode('utf-8'))    
            return

    
    # Check if the user is a member of the group
    if sender not in groups[group_ID]:
        client_socket.send(f"You are not a member of {group_ID}. Use 'join {group_ID}' to join the group.\n".encode('utf-8'))
        return

    # Check if the message is empty
    if not message.strip():
        client_socket.send("Message cannot be empty. Please try again.\n".encode('utf-8'))
        return
    
    

    message_data = f"{len(messages) + 1}, {sender}, {timestamp}, <{group_ID}> {message}"
    messages.append(message_data)


    # Update last two messages for the group
    last_two_messages[group_ID] = [last_two_messages[group_ID][1], message_data]

    broadcast_message(client_socket,sender, group_ID, message_data)

# Function to find the group of a user
def find_user_group(username):
    for group, members in groups.items():
        if username in members:
            return group
    return None

def print_groups(client_socket):
    available_groups = ", ".join(groups.keys())
    client_socket.send(f"Available groups: {available_groups}\n".encode('utf-8'))

# Function to broadcast messages to all clients in a group
def broadcast_message(client_socket,sender, group, message_data):
    print(f"Broadcasting message from {sender} in group {group}: {message_data}")
    if group in groups:
        for username, client_socket in users:
            if username in groups[group]:  #If we want the sender to see the post Broad delete (username != sender) and it will send to everyone in the group including sender
                try:
                    client_socket.send(f"{message_data}".encode('utf-8'))
                except Exception as e:
                    print(f"Error broadcasting message to user {username}: {e}")

# Function to add a new user to the server and place them in the public group
def add_user(client_socket,username):
    while username_exists(username):
        client_socket.send(f"Username '{username}' is already in use. Please choose a different username: ".encode('utf-8'))
        username = client_socket.recv(1024).decode('utf-8').strip()
        
    # add the new username to the users
    print(username)
    users.append((username,client_socket))
    return username

# Function to check if a username already exists
def username_exists(username):
    for user_info in users:
        if user_info[0].lower() == username.lower():
            return True
    return False 
    

# Function to join a user to a group
def join_group(client_socket,username, group):
    if group not in groups:
        try:
            if 1 <= int(group) <= 5:
                        group = "Group" + group
        except ValueError:
            return f"Invalid group. Use command 'grouplist' to see available groups." 
        
    message_data = f"{username} joined {group}."    
    client_socket_test = client_socket
    if group in groups:
        if username not in groups[group]:
            groups[group].append(username)
            if group in groups:
                for sender, client_socket_test in users:
                    if sender != username and sender in groups[group]:  #If we want the sender to see the post Broad delete (username != sender) and it will send to everyone in the group including sender
                        try:
                            client_socket_test.send(f"{message_data}".encode('utf-8'))
                        except Exception as e:
                            print(f"Error broadcasting message to user {username}: {e}")
            #broadcast_message(client_socket,username, group, f"{username} joined {group}.")
            display_user_list(client_socket, group)             #use our created display user list function to print the current users in the joined group. (ONLY DISPLAYED FOR USER JOINING)
            
            # Send the last two messages to the client
            for msg in last_two_messages[group]:
                if msg:
                    client_socket.send(f"{msg}\n".encode('utf-8'))
            
            return f"You joined {group}."
        else:
            return f"You are already in {group}\n"
    else:
        return f"Invalid group. Use command 'grouplist' to see available groups." 

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
    if group not in groups:
        try:
            if 1 <= int(group) <= 5:
                group = "Group" + group
                if group in groups:
                    user_list = ', '.join(groups[group])
                    client_socket.send(f"Users in {group}: {user_list}\n".encode('utf-8'))
                else:
                    client_socket.send("Invalid group. Use command 'grouplist' to see available groups.".encode('utf-8'))
            else:
                client_socket.send("Invalid group. Use command 'grouplist' to see available groups.".encode('utf-8'))
        except ValueError:
            client_socket.send("Invalid group. Use command 'grouplist' to see available groups.".encode('utf-8'))
    else:
        if group in groups:
            user_list = ', '.join(groups[group])
            client_socket.send(f"Users in {group}: {user_list}\n".encode('utf-8'))
        else:
            client_socket.send("Invalid group. Use command 'grouplist' to see available groups.".encode('utf-8'))


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
def leave_group(username, group):  
    if group not in groups:
        try:
            if 1 <= int(group) <= 5:
                        group = "Group" + group
        except ValueError:
            return f"Invalid group. Use command 'grouplist' to see available groups." 
    
    # Check if the user is a member of the group
    if username not in groups[group]:
        if group == "Public":
            return f"You are not a member of {group}. Simply type 'join' join the public discussion.\n"
        else:
            return f"You are not a member of {group}. Use 'groupjoin {group}' to join the group.\n"
        
    groups[group].remove(username)
    return f"You have left {group}!"


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

            username = add_user(client_socket,username)

            #client_socket.send('Welcome to the public message board!\n'.encode('utf-8'))                #when joining public this is redunant message 1/2. Should we have just the broadcast message? I think so --Trysten

            # Start a thread to handle the client
            client_handler = threading.Thread(target=handle_client, args=(client_socket, username))
            client_handler.start()

    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server.close()

if __name__ == "__main__":
    main()
