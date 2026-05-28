import threading
import socket
import rsa

public_key, private_key = rsa.newkeys(1024)

nickname = input("choose your nickname:")
if nickname == "admin":
    password = input('Enter password admin plz: ')

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1',55555))

public_server = rsa.PublicKey.load_pkcs1(client.recv(1024))


stop_thread = False

def receive():
    while True:
        global stop_thread 
        if stop_thread:
            break
        try:
            massage = client.recv(1024)
            try:
                massage = massage.decode('ascii')
            except:
                massage = rsa.decrypt(massage, private_key).decode('ascii')
            if massage == 'NIKE':
                client.send(nickname.encode('ascii'))
                client.send(public_key.save_pkcs1('PEM'))
                next_massage = rsa.decrypt(client.recv(1024), private_key).decode('ascii')
                if next_massage == 'PASS':
                    client.send(rsa.encrypt(password.encode('ascii'), public_server))
                    if rsa.decrypt(client.recv(1024), private_key).decode('ascii') == 'REFUSE':
                        print('ops! wrong password')
                        stop_thread = True
                elif next_massage == 'BAN':
                    print('sorry you were banned by the server!')
                    client.close()
                    stop_thread = True

            else:
                print(massage)
        except:
            print(f"something went wrong!")
            client.close()
            break

def write():
    while True:
        if stop_thread:
            break
        massage = f'{nickname}:{input("")}'
        if massage[len(nickname)+2:].startswith('/'):
            if nickname == 'admin':
                if massage[len(nickname)+2:].startswith('/kick'):
                    client.send( rsa.encrypt(f'KICK {massage[len(nickname)+2+6:]}'.encode('ascii'), public_server))
                elif massage[len(nickname)+2:].startswith('/ban'):
                    client.send(rsa.encrypt(f'BAN {massage[len(nickname)+2+5:]}'.encode('ascii'), public_server))
            elif massage[len(nickname)+2:].startswith('/bot'):
                client.send(rsa.encrypt(f'BOT {massage[len(nickname)+2+4:]}'.encode('ascii'), public_server))
            else:
                print(':( only admin can use commands!')
        else:
            client.send(rsa.encrypt(massage.encode('ascii'), public_server))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
