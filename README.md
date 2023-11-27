# Socket Programming Bulletin Board

## Table of Contents
- [Description](#description)
- [Developers](#developers)
- [Instructions](#instructions)
  - [Server](#server)
  - [Client](#client)
- [Usability Instructions](#usability-instructions)
- [Known Issues](#known-issues)

## Description
The Chat Application is a simple yet powerful server-client communication system developed in Python using socket programming. The project provides a real-time chat environment where users can join different groups, post messages, and discuss with other participants.

### Key Features
- **User Management:** Users can register unique usernames upon connecting to the server, ensuring a personalized experience.
- **Group Interaction:** Participants can join various groups to focus their conversations, fostering collaboration and community building.
- **Messaging System:** The application supports posting messages both in public and group-specific channels, allowing for efficient communication.
- **Command-Based Interface:** Users interact with the system through a command-line interface, executing commands to perform various actions.

## Developers
- **Parker Manson**
- **Joshua Miles**
- **Trysten Giorgione**

## Instructions

### Server
1. **Compile and Run:**
    ```bash
    python server.py
    ```
2. The server will listen on port 9999.

### Client
1. **Compile and Run:**
    ```bash
    python client.py
    ```
2. Enter you desired server address and port.
3. Enter your desired username.
4. Use the following commands:
   - `post <message>`: Post a message to the public group.
   - `users`: Display the list of users in the public group.
   - `getmessage <message_id>`: Get the content of a specific message.
   - `leave <group>`: Leave a group.
   - `join <group>`: Join a group.
   - `help`: Display a list of commands.
   - `exit`: Disconnect from the server and exit the client program.
   - `grouppost <group> <message>`: Post a message to a specific group.
   - `grouplist`: Display the list of available groups.
   - `groupjoin <group>`: Join a specific group.
   - `grouppost <group>`: Post a message to a specific group.
   - `groupusers <group>`: Display the list of users in a specific group.
   - `groupleave <group>`: Leave a specific group.
   - `groupmessage <group> <message_id>`: Get the content of a specific message in a specific group.

## Usability Instructions
- When joining the server, the user is automatically added to the Public group.
- The server will provide a welcome message with instructions.
- Type `help` for a list of available commands.

## Known Issues

## 
