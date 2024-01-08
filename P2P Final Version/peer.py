import socket
import threading
from colorama import Fore, Style

# Global variables for peer server socket and username
peer_server_socket = None
username = None
counter = 0
flag02 = 0
x = ""
z = ""
my_listening_port =""
def get_user_ip(username, server_socket):
    try:
        # Send a request to the server to get the IP address of the specified username
        server_socket.send(f"get,{username}".encode())
        response = server_socket.recv(4096)
        # print(response.decode())
        return response.decode()  # Return the IP address obtained from the server
    except Exception as e:
        print(f"Error: {e}")
        return None
def get_user_port(username, server_socket):
    try:
        # Send a request to the server to get the IP address of the specified username
        server_socket.send(f"ge_port,{username}".encode())
        response = server_socket.recv(4096)
        #print(response.decode())
        return response.decode()  # Return the IP address obtained from the server
    except Exception as e:
        print(f"Error: {e}")
        return None

def establish_peer_connection(target_username, target_ip, target_port):
    global flag02,my_listening_port
    flag02 = 1
    try:

        # Establish a peer-to-peer connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as peer_socket:
            peer_socket.connect((target_ip, target_port))  # Fix: Use (target_ip, target_port)
            print("Peer-to-peer connection established.")
            _, my_listening_port = peer_server_socket.getsockname()
            peer_socket.sendall(str(my_listening_port).encode())
            # Start a thread to handle messages from the peer
            threading.Thread(target=handle_peer_messages, args=(peer_socket,)).start()
            print("Enter message to send (or '--exit--' to close the connection): ")
            while True:
                # Send messages to the peer
                message = input()
                if message.lower() == '--exit--':
                    peer_socket.sendall(message.encode())
                    flag02 = 0
                    return
                if flag02==0:
                    #peer_socket.sendall(f"{message}".encode())
                    #flag02 = 0
                    return
                    
                    
                else:
                    peer_socket.sendall(f"{username} : {message}".encode())
    except Exception as e:
        print(f"Peer connection error: {e}")
        return
    finally:
        print("Peer-to-peer connection closed.")
        flag02=0
        #peer_socket.close()

def handle_peer_messages(peer_socket):
    global flag02
    x=0
    try:
        while True:
            message = peer_socket.recv(1024).decode()
            if not message:
                break
            if message == '--exit--':
                flag02=0
                print("other peer left please type 'exit' to go back")
                peer_socket.send("exit".encode())
                x=1
                return
            if message == 'exit':
                x=1
                return
            print(f" {message}")
    except Exception as e:
        if flag02==1:
            print(f"Peer message error: {e}")
        return
    finally:
        x=1
        peer_socket.close()
def recv_msgs(peer_socket):
    try:
        while True:
            message = peer_socket.recv(1024).decode()
            if not message:
                break
            if message == "--exit--":
                return
            print(f" {message}")
    except Exception as e:
        print(f"Peer message error: {e}")

def start_peer_server(host, port):
    global flag02 
    global peer_server_socket,x,z,my_listening_port
    try:
        
        peer_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_server_socket.bind((host, port))
        peer_server_socket.listen(5)
        _, assigned_port = peer_server_socket.getsockname()
        print(f"Peer server listening on {host}:{assigned_port}")
        my_listening_port=assigned_port
        while True:
            if flag02 == 0:
                client_socket, client_address = peer_server_socket.accept()
                client_ip, _ = client_address
                print(f"Accepted connection from {client_address}")
                peer_listening_port = int(client_socket.recv(1024).decode())
                print(f"Peer is listening on port {peer_listening_port}")
                threading.Thread(target=handle_peer_messages, args=(client_socket,)).start()
            try:
                # Read the listening port from the peer
                # Start a thread to handle messages from the connected peer
                # Automatically establish a connection back to the peer
                if flag02==0:
                    print(f"Connecting back to the peer at {client_ip}:{peer_listening_port}")
                    print('\n press Enter to procceed')
                    x=client_ip
                    z=peer_listening_port
                    flag02 = 1
            except ValueError:
                print("Invalid listening port received from peer.")
            except Exception as e:
                print(f"Error handling incoming connection: {e}")
    except Exception as e:
        print(f"Peer server error: {e}")
    finally:
        if peer_server_socket:
            peer_server_socket.close()

def connect_to_server(host, port):
    global username,my_listening_port
    try:
        # Establish a connection to the server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((host, port))
            print(f"{Fore.BLUE}Connected to the server.{Style.RESET_ALL}")
            while my_listening_port=="":
                continue
            client.send(f"{str(my_listening_port)}".encode())
            while True:
                if flag02==1:
                    establish_peer_connection(" ",x,z)
                # Prompt the user for input based on the current state
                if username:
                    command = input(f"Enter {Fore.BLUE}'show online peers',{Fore.GREEN}'show chat rooms',{Fore.YELLOW}'peer connect',{Fore.MAGENTA}'create chat room',{Fore.CYAN}'join chat room',{Fore.RED}'logout'{Style.RESET_ALL}: ").lower().strip()
                else:
                    command = input(f"Enter {Fore.BLUE}'register' or 'login'{Style.RESET_ALL}: ").lower().strip()
                # Process user commands
                if command == 'logout':
                    # Send logout command to the server
                    client.send(f"{command}".encode())
                    response = client.recv(4096)
                    print(f"Server response: {Fore.RED}{response.decode()}{Style.RESET_ALL}")
                    print("Logged out successfully.")
                    username = None
                elif command == 'show online peers':
                    # Send request to the server to show online peers
                    client.send(f"{command}".encode())
                    response = client.recv(4096)
                    print(f"Server response: {Fore.BLUE}{response.decode()}{Style.RESET_ALL}")
                elif command == 'show chat rooms':
                    # Send request to the server to show online peers
                    client.send(f"{command}".encode())
                    response = client.recv(4096)
                    print(f"Server response: {Fore.BLUE}{response.decode()}{Style.RESET_ALL}")
                elif command == 'get':
                    target_username = input("Enter the username to get the IP address: ").strip()
                    porto=get_user_ip(target_username, client)
                    print(porto)
                elif command == 'getb':
                    target_username = input("Enter the username to get the IP address: ").strip()
                    porta=get_user_port(target_username, client)
                    print(porta)
                elif command == 'peer connect':
                    target_username = input("Enter the username to connect to: ").strip()
                    target_ip = get_user_ip(target_username, client)
                    
                    if target_ip:
                        target_port = get_user_port(target_username, client)
                        establish_peer_connection(target_username, target_ip, int(target_port))
                    else:
                        print(f"{target_username} is not online or does not exist.")
                elif command == 'create chat room':
                    chatRoomName=input("Enter Chatroom : ")
                    client.send(f"create chat room,{chatRoomName}".encode())
                    print(client.recv(4096).decode())
                elif command == 'join chat room':
                    chatRoomName=input("Enter Chatroom : ")
                    client.send(f"join chat room,{chatRoomName}".encode())
                    t1= threading.Thread(target=recv_msgs, args=(client,))
                    t1.start()
                    print("Enter message to send (or '--exit--' to close the connection): ")
                    while True:
                        msg = input()
                        client.send(f"{username} : {msg}".encode())
                        if msg=="--exit--":
                            break
                    
                elif command not in ['register', 'login' , 'exit' , 'show online peers', 'show chat rooms', 'peer connect', 'create chat room', 'join chat room', 'logout']:
                    if flag02 != 1:
                        print("Invalid command. Please try again.")
                else:
                    # Process registration or login commands
                    if not username:
                        username = input("Enter username: ").strip()
                        password = input("Enter password: ").strip()
                    # Send registration or login command with username and password to the server
                    client.send(f"{command},{username},{password}".encode())
                    response = client.recv(4096)
                    print(f"Server response: {Fore.BLUE}{response.decode()}{Style.RESET_ALL}")
                    # Handle server responses for login and registration
                    if command == 'login':
                        if response.decode().endswith('successful'):
                            print(f"Login successful. You can now use {Fore.BLUE}'show online peers',{Fore.GREEN}'show chat rooms',{Fore.YELLOW}'peer connect',{Fore.MAGENTA}'create chat room',{Fore.CYAN}'join chat room',{Fore.RED}'logout'{Style.RESET_ALL}.")
                        elif response.decode().endswith('username'):
                            print(f"{Fore.RED}Wrong Username{Style.RESET_ALL}")
                            username = None  # Reset the username if login failed
                        elif response.decode().endswith('password'):
                            print(f"{Fore.RED}Wrong Password{Style.RESET_ALL}")
                            username = None  # Reset the username if login failed
                        elif response.decode().endswith('failed'):
                            print(f"{Fore.RED}Login failed. Please try again.{Style.RESET_ALL}")
                            username = None  # Reset the username if login failed
                        elif response.decode().endswith('logged in'):
                            print(f"{Fore.RED}Login failed. Please try again.{Style.RESET_ALL}")
                            username = None  # Reset the username if login failed
                    elif command == 'register':
                        if response.decode().endswith('successful'):
                            print(f"Registration successful. You can now use {Fore.BLUE}'show online peers',{Fore.GREEN}'show chat rooms',{Fore.YELLOW}'peer connect',{Fore.MAGENTA}'create chat room',{Fore.CYAN}'join chat room',{Fore.RED}'logout'{Style.RESET_ALL}.")
                        elif response.decode().endswith('failed'):
                            print(f"{Fore.RED}Already Registered Username{Style.RESET_ALL}")
                            username = None  # Reset the username if registration failed
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    server_host = 'localhost'  # Replace with server's IP address if needed
    server_port = 12345
    # Start the peer server in a separate thread
    threading.Thread(target=start_peer_server, args=('localhost', 0)).start()
    # Connect to the main server
    connect_to_server(server_host, server_port)