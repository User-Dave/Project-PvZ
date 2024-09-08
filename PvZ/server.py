import socket, ClientProtocol, time, random
from datetime import datetime

def send_message(socket_info, msg, sock_groups=[]):
    sock = socket_info[0]
    msg = str(len(msg)).zfill(4)+ "|" + msg
    print("sending",msg)
    msg = ClientProtocol.encrypt(msg,ClientProtocol.KEYS[0]).encode()
    #print("sending2",msg) # TEST MESSAGE
    try:
        sock.send(msg)
    except Exception as e:
        print(f"{str(e)}, could not send {msg}.")
        for i in sock_groups:
            if socket_info in i:
                i.remove(socket_info)
        sock.close()


def listen_for_socks(listener, list_of_socks,ownip):
    #print('listening',list_of_socks) # TEST MESSAGE
    if len(list_of_socks) < 100:
        try:
            conn, addr = listener.accept()
            print(addr,type(addr))
        except Exception as e:
            return
        addr = addr[0]
        if addr == "127.0.0.1":
            addr = ownip[:]
        conn.settimeout(0.1)
        print("CONNECTION SECURED")
        list_of_socks.append([conn,datetime.now(),addr]) #socket, last message recv time, IP
        print(list_of_socks)

def interact_with_sockets(sockets, p_socks, z_socks):
    sock_groups = (sockets, p_socks, z_socks)
    #print('interacting') # TEST MESSAGE
    for socket_info in sockets:
        sock = socket_info[0]
        data=""
        try:
            length_of_message = sock.recv(5).decode()
            data = sock.recv(int(length_of_message[:4])).decode()
            data = ClientProtocol.decrypt(length_of_message + data,ClientProtocol.KEYS[0])[5:]
            print("Client Sent",data)
        except:
            pass
        
        msg = ""
        dt = (datetime.now() - socket_info[1]).total_seconds()
        if data == "" and  dt > 10:
            if dt > 30:
                msg = "DISCONNECT|"
                send_message(socket_info,msg, sock_groups)
                if socket_info in sockets:
                    sockets.remove(socket_info)
                    time.sleep(0.2)
                    sock.close()
            else:
                msg = "ISWAITING|"
                send_message(socket_info,msg, sock_groups)
        

        if data.startswith("PLAY"):
            data_parts = data.split("|")
            if data_parts[1] == 'P' and (not (socket_info in p_socks)):
                if socket_info in z_socks:
                    z_socks.remove(socket_info)
                p_socks.append(socket_info)
            if data_parts[1] == 'Z' and (not (socket_info in z_socks)):
                if socket_info in p_socks:
                    p_socks.remove(socket_info)
                z_socks.append(socket_info)
        elif data.startswith("CANCEL"):
            if socket_info in p_socks:
                p_socks.remove(socket_info)
            if socket_info in z_socks:
                z_socks.remove(socket_info)
        elif data.startswith("WAITING"):
            socket_info[1] = datetime.now()
        elif data.startswith("QUIT"):
            if socket_info in sockets:
                sockets.remove(socket_info)
            if socket_info in p_socks:
                p_socks.remove(socket_info)
            if socket_info in z_socks:
                z_socks.remove(socket_info)
            msg = "DISCONNECT|"
            send_message(socket_info, msg, sock_groups)
        else:
            pass

        if data != "":
            print(f"post reaction: listofsocks={str(len(sockets))},p={str(len(p_socks))},z={str(len(z_socks))}")
        
        

def pair_up(sockets, p_socks, z_socks): # Matches players for games
    sock_groups = (sockets, p_socks, z_socks) # all lists socket data can be in
    if (len(p_socks) > 0) and (len(z_socks) > 0): # if there's at least one willing plant/zombie
        p = p_socks[0] #info of plant
        z = z_socks[0] #info of zom
        dtp = (datetime.now() - p[1]).total_seconds()
        dtz = (datetime.now() - z[1]).total_seconds()
        print("pairup",dtp,dtz)
        if dtp < 5 and dtz < 5: # make sure to only match players who have proven to be active
            random_seed=random.randint(0,99999) # set a random seed
            send_message(p, "PLAYWITH|"+z[2]+"#"+str(random_seed)+"#0", sock_groups)
            send_message(z, "PLAYWITH|"+p[2]+"#"+str(random_seed)+"#1", sock_groups)
            for i in sock_groups:
                for x in (p,z):
                    if x in i:
                        i.remove(x)
        else: # if they're not definately active, try and make sure if they are
            send_message(p, "ISWAITING|", sock_groups)
            send_message(z, "ISWAITING|", sock_groups)
    pass

def main():
    list_of_sockets=[] # list^2, every sublist is [socket, last message recv time, IP]
    list_of_plants = []
    list_of_zombies = []
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("0.0.0.0", ClientProtocol.PORTSFORCOMMS[0]))
    listener.listen(1)
    listener.settimeout(1)
    ownip = socket.gethostbyname(socket.gethostname())
    print("server up and running. Server IP = ",ownip)
    while True:
        listen_for_socks(listener, list_of_sockets, ownip)
        interact_with_sockets(list_of_sockets, list_of_plants, list_of_zombies)
        pair_up(list_of_sockets, list_of_plants, list_of_zombies)


if __name__ == '__main__':
    main()
