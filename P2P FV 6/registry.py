import socket
import threading
import sqlite3
import bcrypt
import time
from colorama import Fore, Style

# Global variables
active_connections = []  # List to track active client addresses
online_peers = {} 
online_peers_ports={}      # Dictionary to store online peers and their addresses
shutdown_flag = False    # Flag to signal server shutdown
connected_peers = {}  # Dictionary to store connected peers and their sockets
chatRooms={}
clients_sockets=[]


def left(chatRoomName,client_socket):
    if chatRooms.__contains__(chatRoomName):
        chatRooms[chatRoomName].remove(client_socket)
        print(chatRooms)

def create_chatroom(name):
    chatRooms[name] =[]
    print(chatRooms)

def join_room(name,user_socket,username):
    if(chatRooms.__contains__(name)):
     chatRooms[name].append(user_socket)
     print(chatRooms)
     broadcast_chatRoom(name,user_socket,f"{username} has joined the chat   ")
    else:
        user_socket.send("--exit--".encode())

def broadcast_chatRoom(name,client_socket,msg):
    exit=''
    if msg.__contains__(':'):
     exit = msg.split(' : ')[1]
    if exit == "--exit--":

            print(msg)
            print(exit)
            broadcast_chatRoom(name,client_socket,f" {msg.split(' : ')[0]} has left   ")
            client_socket.send(exit.encode())
            left(name,client_socket)
    else:
        for i in chatRooms[name]:
            if i != client_socket:
                i.send(msg.encode())

def handle_peer_connection(target_username, client_socket):
    target_ip = get_ip_by_username(target_username)
    if target_ip:
        target_port = 12346  # Choose an available port for peer-to-peer connection
        try:
            # Establish a peer-to-peer connection
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as peer_socket:
                peer_socket.bind(('0.0.0.0', target_port))
                peer_socket.listen(1)
                client_socket.send(f"peer_connected,{target_ip},{target_port}".encode())
                peer_conn, _ = peer_socket.accept()
                print(f"Peer-to-peer connection established with {target_username} ({target_ip}:{target_port})")
                connected_peers[target_username] = peer_conn
                handle_peer_messages(target_username, client_socket, peer_conn)
        except Exception as e:
            print(f".rg Peer connection error: {e}")
    else:
        client_socket.send("peer_connection_failed".encode())

def handle_peer_messages(target_username, client_socket, peer_socket):
    try:
        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            peer_socket.sendall(message.encode())
    except Exception as e:
        print(f"Peer message error: {e}")
    finally:
        print(f"Peer-to-peer connection closed with {target_username}")
        connected_peers.pop(target_username, None)

def get_client_ip(client_socket):
    # Get the IP address of the connected client
    client_ip, _ = client_socket.getpeername()
    return client_ip

def get_ip_by_username(requested_username):
    # Get the IP address of a user by their username
    if requested_username in online_peers:
        return online_peers[requested_username][0]  # Only return the IP address, not the port
    else:
        print(f"Server Error")
        return None

def get_port_by_username(requested_username,peer_port):
    if requested_username in online_peers:
        print(online_peers_ports[requested_username])
        return online_peers_ports[requested_username]  # Only return the IP address, not the port
    else:
        print(f"Server Error")
        return None

def handle_client(client_socket, client_address):
    chatflag=0
    try:
        logged_in = 0
        chatflag = 0
        print(f"Connection from {client_address} ({get_client_ip(client_socket)})")
        active_connections.append(client_address)

        username = None  # Initialize username as None
        recv_port = client_socket.recv(1024).decode().split(',')
        peer_port = recv_port[0]
        print(peer_port)
        while True:
            # Receive message from the client
            message = client_socket.recv(1024).decode()
            if not message:
                break
            # Split the received message into parts
            parts = message.split(',')
            command = parts[0]
            
            # Handle different commands from the client
            if command == 'get':
                requested_username = parts[1]
                ip_response = get_ip_by_username(requested_username)
                if ip_response:
                    response = ip_response
                else:
                    response = f"{requested_username} is not online or does not exist."
                print(response)
            elif command == 'ge_port':
                requested_username = parts[1]
                port = get_port_by_username(requested_username,peer_port)
                if port:
                    response = port
                else:
                    response = f"{requested_username} is not online or does not exist."
            elif command == 'create chat room':
                if not logged_in:
                    response = f'{Fore.RED}Please login first{Style.RESET_ALL}'
                else:
                    chatRoomName = parts[1]
                    create_chatroom(chatRoomName)
                    response = f"{Fore.GREEN}Created{Style.RESET_ALL}"
            elif command == 'join chat room':
                if not logged_in:
                    response = f'{Fore.RED}Please login first{Style.RESET_ALL}'
                else:
                    chatRoomName = parts[1]
                    chatflag=1
                    join_room(chatRoomName,client_socket,username)
                    response = f"{Fore.GREEN}Joined{Style.RESET_ALL}"
            elif command == 'peer_connect':
                if not logged_in:
                    response = f'{Fore.RED}Please login first{Style.RESET_ALL}'
                else:
                    target_username = parts[1]
                    handle_peer_connection(target_username, client_socket,peer_port)
            # Handle different commands from the client
            elif command == 'register':
                if logged_in:
                    response = f'{Fore.RED}You are already logged in{Style.RESET_ALL}'
                else:          
                    provided_username, password = parts[1], parts[2]
                    # Attempt to register the user
                    if register_user(provided_username, password):
                        response = f'{Fore.BLUE}Registration successful{Style.RESET_ALL}'
                        logged_in=1
                        online_peers[provided_username] = client_address  # Add to online peers on successful 
                        online_peers_ports[username] = peer_port
                    else:
                        response = f'{Fore.RED}Registration failed{Style.RESET_ALL}'
            elif command == 'login':
                if logged_in:
                    response = f'{Fore.RED}You are already logged in{Style.RESET_ALL}'   
                else:          
                    provided_username, password = parts[1], parts[2]
                    # Validate user login credentials
                    if validate_login(provided_username, password):
                        response = f'{Fore.BLUE}Login successful{Style.RESET_ALL}'
                        logged_in=1
                        username = provided_username
                        online_peers[username] = client_address  # Update address on successful login
                        online_peers_ports[username] = peer_port
                    else:
                        response = f'{Fore.RED}Login failed{Style.RESET_ALL}'
                        if online_peers.__contains__(provided_username,):
                            response += "\n that user is already logged in"
                        elif provided_username not in get_all_usernames():
                            response += '_username'  # Indicate wrong username
                        elif not validate_password(provided_username, password):
                            response += '_password'  # Indicate wrong password
            elif command == 'logout':
                logged_in=0
                online_peers.pop(username, None)
                response = f'{Fore.RED}Logout successful{Style.RESET_ALL}'
            elif command == 'show online peers':
                if not logged_in:
                    response = f'{Fore.RED}Please login first{Style.RESET_ALL}'
                else: 
                    response = f'Online Peers: {", ".join(online_peers.keys())}'
            elif command == 'show chat rooms':
                if not logged_in:
                    response = f'{Fore.RED}Please login first{Style.RESET_ALL}'
                else: 
                    response = f'Available chat rooms: {", ".join(chatRooms.keys())}'
            else:
                if chatflag==1:
                    broadcast_chatRoom(chatRoomName,client_socket,command)
                    continue
                response = f'{Fore.BLACK}{message}{Style.RESET_ALL}'
            # Send the response back to the client
            print(response)
            client_socket.send(response.encode())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup on client disconnection
        print(f"Connection closed with {client_address}")
        active_connections.remove(client_address)
        if chatflag ==1:
            left(chatRoomName,client_socket)
            chatflag=0
        if username:
            online_peers.pop(username, None)  # Remove from online peers on unexpected disconnection
        client_socket.close()

def hash_password(password):
    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed_password

def register_user(username, password):
    try:
        # Attempt to register a new user in the database
        hashed_password = hash_password(password)
        connection = sqlite3.connect('user_database.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        connection.commit()
        return True
    except sqlite3.IntegrityError:
        print("Username already exists.")
        return False
    except sqlite3.Error as e:
        print("Database error:", e)
        return False
    finally:
        connection.close()

def validate_login(username, password):
    if online_peers.__contains__(username,):
        print("already logged")
        return False
    try:
        # Validate user login credentials against the database
        connection = sqlite3.connect('user_database.db')
        cursor = connection.cursor()
        cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
        stored_password_hash = cursor.fetchone()
        connection.close()
        if stored_password_hash:
            stored_password_hash = stored_password_hash[0]
            # Check if the provided password matches the stored hash
            is_password_correct = bcrypt.checkpw(password.encode(), stored_password_hash)
            return is_password_correct
        else:
            return False
    except sqlite3.Error as e:
        print("Database error:", e)
        return False

def validate_password(username, password):
    try:
        # Validate the password without logging the user in
        connection = sqlite3.connect('user_database.db')
        cursor = connection.cursor()
        cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
        stored_password_hash = cursor.fetchone()
        connection.close()
        if stored_password_hash:
            stored_password_hash = stored_password_hash[0]
            # Check if the provided password matches the stored hash
            is_password_correct = bcrypt.checkpw(password.encode(), stored_password_hash)
            return is_password_correct
        else:
            return False
    except sqlite3.Error as e:
        print("Database error:", e)
        return False

def get_all_usernames():
    try:
        # Retrieve all usernames from the database
        connection = sqlite3.connect('user_database.db')
        cursor = connection.cursor()
        cursor.execute('SELECT username FROM users')
        usernames = cursor.fetchall()
        connection.close()
        return [user[0] for user in usernames]
    except sqlite3.Error as e:
        print("Database error:", e)
        return []

def start_server(port):
    try:
        # Set up the server socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', port))
        server.listen(5)
        print("Server listening on port", port)
        # Thread for the loop that prints active connections
        def print_active_connections():
            while not shutdown_flag:
                print(f"Active connections: {len(active_connections)} - {online_peers}")
                time.sleep(5)
        # Start the active connections printing loop in a separate thread
        print_thread = threading.Thread(target=print_active_connections)
        print_thread.start()
        # Main server loop for handling incoming client connections
        while not shutdown_flag:
            client_socket, client_address = server.accept()
            clients_sockets.append(client_socket)
            #print(clients_sockets)
            # Start a new thread to handle the client
            thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            thread.start()
            print(f"Active connections: {len(active_connections)} - {active_connections}")
            #print(server.recv(1024).decode())

    except Exception as e:
        print(f"Server error: {e}")
    finally:
        # Cleanup and close the server socket on shutdown
        print("Server shutting down...")
        server.close()

if __name__ == "__main__":
    try:
        # Start the server on port 12345
        start_server(12345)
    except KeyboardInterrupt:
        # Handle keyboard interrupt to initiate a graceful shutdown
        print("Received shutdown signal. Exiting gracefully.")
        shutdown_flag = True