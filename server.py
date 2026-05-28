import threading
import socket
import rsa
import Chat_bot as chatbot

public_key, private_key = rsa.newkeys(1024)

host = '127.0.0.1'
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients =[]
nicknames=[]
public_client_keys = {}

def broadcast(message):
    for client in clients:
        client.send(rsa.encrypt(message, public_client_keys.get(nicknames[clients.index(client)], public_key)))

def handle(client):
    while True:
        try:
            msg=message = rsa.decrypt(client.recv(1024),private_key)
            if msg.decode('ascii').startswith('KICK'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_kick = msg.decode('ascii')[5:]
                    kick_user(name_to_kick)
                else:
                    client.send(rsa.encrypt(':( only admin can use commands!'.encode('ascii'), public_client_keys.get(nicknames[clients.index(client)], public_key)))
            elif msg.decode('ascii').startswith('BAN'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_ban = msg.decode('ascii')[4:]
                    kick_user(name_to_ban)
                    with open('ban.txt','a') as f:
                        f.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} is banned!')
                else:
                    client.send(rsa.encrypt(':( only admin can use commands!'.encode('ascii'), public_client_keys.get(nicknames[clients.index(client)], public_key)))
            elif msg.decode('ascii').startswith('BOT'):
                bot = chatbot.ChatbotAssistant('intents.json',function_mappings={'stocks':chatbot.get_stock})
                bot.parse_intents()
                bot.Load_model('chatbot_model.pth','dimensions.json')
                input_message = msg.decode('ascii')[4:]
                out_message = f'{nicknames[clients.index(client)]}:@Bot:{msg.decode('ascii')[4:]} \nBot:{bot.process_message(input_message)}'
                broadcast(out_message.encode('ascii'))
                
            else:
                broadcast(message)
            
        except:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f'{nickname} left the chat !'.encode('ascii'))
                nicknames.remove(nickname)
                break

            
def receive():
    while True:
        client, address = server.accept()
        print(f'connected with {str(address)}')

        client.send(public_key.save_pkcs1('PEM'))

        client.send('NIKE'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')

        public_client_keys[nickname] = rsa.PublicKey.load_pkcs1(client.recv(1024))
        
        with open('ban.txt','r') as f:
            ban = f.readlines()
        if nickname+'\n' in ban:
            client.send(rsa.encrypt('BAN'.encode('ascii'), public_client_keys.get(nickname, public_key)))
            client.close()
            continue 
        


        if nickname == "admin":
            client.send(rsa.encrypt('PASS'.encode('ascii'), public_client_keys.get(nickname, public_key)))
            password = rsa.decrypt(client.recv(1024), private_key).decode('ascii')
            if password != '12345':
                client.send(rsa.encrypt('REFUSE'.encode('ascii'), public_client_keys.get(nickname, public_key)))
                client.close()
                continue

        nicknames.append(nickname)
        clients.append(client)

        print(f'Nickname of the client is {nickname}')
        broadcast(f'{nickname} joined !'.encode('ascii'))
        client.send(rsa.encrypt('connected'.encode('ascii'),public_client_keys.get(nickname,public_key)))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send(rsa.encrypt('You were kicked by the admin!'.encode('ascii'), public_client_keys.get(name, public_key)))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f'{name} was kicked by admin!'.encode('ascii'))


print('I am listening...')
receive()