import socket
import threading

def receive_messages(client_socket):
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break
        print(message)

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Add a 'connect' command to specify the server address and port
    server_address = input("Enter the server address: ")
    server_port = int(input("Enter the server port: "))

    client_socket.connect((server_address, server_port))

    username = input("Enter your username: ")
    client_socket.send(username.encode('utf-8'))

    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    try:
        while True:
            message = input()
            client_socket.send(message.encode('utf-8'))

    except KeyboardInterrupt:
        print("Client shutting down.")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()