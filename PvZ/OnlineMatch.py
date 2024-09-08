import threading, time, sys
import socket, pygame, constants, drawable, buttons, menu, Match, ClientProtocol

class WaitingRoom(menu.Game_Menu):
    def __init__(self, game=None, server_ip = "0.0.0.0"):
        super().__init__(game=game, bg=[], but=[buttons.Button(origin="chooseTeamPlants",
                                                                visual_rect=[10,30,540,810],
                                                                  touch_rect=[15,35,530,800],
                                                                    button_function=buttons.make_msg_function_waitingroom("PLAY|P")),
                                                buttons.Button(origin="chooseTeamZombies",
                                                                visual_rect=[560,30,540,810],
                                                                  touch_rect=[565,35,530,800],
                                                                    button_function=buttons.make_msg_function_waitingroom("PLAY|Z")),
                                                buttons.Button(origin="StartBetaButton",
                                                                visual_rect=[1450,0,150,80],
                                                                  touch_rect=[1455,5,140,70],
                                                                    button_function=buttons.make_msg_function_waitingroom("QUIT|"))],
                                                                      fg=[], screen_color=(95,135,95))
        self.tcp_conv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = server_ip
        self.has_not_connected = True
    
    def update(self):
        if self.has_not_connected: # lazy initing the connection, because we cannot guarentee player will want to go online
            #print(self.tcp_conv.gettimeout(),"   TCP TIMEOUT") Testing message
            self.tcp_conv.connect((self.server_ip,ClientProtocol.PORTSFORCOMMS[0])) # only now connect to server
            self.tcp_conv.settimeout(0.02) # now have a timeout for message reception so the screen can refresh
            self.has_not_connected = False # mark that the connection happeneds
        data = ""
        try:
            l=self.tcp_conv.recv(5).decode() # recieve data length
            length_of_message = int(l[:4])
            data = self.tcp_conv.recv(length_of_message).decode() # recieve data
            data = ClientProtocol.decrypt((l + data),ClientProtocol.KEYS[0])[5:]
            print("Server Sent",data)
        except:
            pass
        self.react_to_server_msg(data)
        return super().update()
    
    def react_to_server_msg(self,big_data): # react to server sent messages
        data = big_data.split("|")
        if (data[0] == "ISWAITING"): # need to send connection verification msg
            print("OnlineMatch.WaitingRoom:",data[0],"recieved from server")
            msg = "WAITING|"
            msg = str(len(msg)).zfill(4)+ "|" + msg
            msg = ClientProtocol.encrypt(msg,ClientProtocol.KEYS[0])
            self.tcp_conv.send(msg.encode())
            print("Sending",msg)
        elif (data[0] == "PLAYWITH"): # got a match
            print("OnlineMatch.WaitingRoom:",data[0],"recieved from server")
            parts = data[1].split("#")
            self.game.displays[4] = WaitingRoom(self.game, self.server_ip) # open new lobby for later games
            self.game.displays[5] = OnlineMatch(self.game, parts[0], int(parts[2]), int(parts[1]))# create the game
            self.game.current_display = 5 # go to the new display
            self.tcp_conv.close()
        elif (data[0] == "DISCONNECT"): # got disconnected
            print("OnlineMatch.WaitingRoom:",data[0],"recieved from server")
            self.game.displays[4] = WaitingRoom(self.game, self.server_ip) # open new lobby for later games
            self.game.current_display = 0 # return to start screen
            self.tcp_conv.close()
        elif (data[0] == ""):
            pass
        else:
            print("OnlineMatch.WaitingRoom:","ELSE","recieved from server")

        return
    
    def quit_game(self):
        msg = "QUIT|"
        msg = str(len(msg)).zfill(4)+ "|" + msg
        self.tcp_conv.send(ClientProtocol.encrypt(msg,ClientProtocol.KEYS[0]).encode())
        time.sleep(0.3)
        self.tcp_conv.close()
        super().quit_game()




class OnlineMatch(Match.MatchPvZ):
    def __init__(self, game, ip_address, team_of_this, randomseed=None):
        print("Start of init")
        super().__init__(game, randomseed)
        self.team_of_player = team_of_this

        self.enemy_move_text = [ClientProtocol.encrypt("MOUSE|0000#0000#TRUE",ClientProtocol.KEYS[1])]
        print(ip_address)
        self.TCP_listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Listen for win messages
        if self.team_of_player == 0:
            self.TCP_listener_socket.bind(("0.0.0.0", ClientProtocol.PORTSFORCOMMS[1]))
            client_address = ("999.999.999.999",15615)
            self.TCP_listener_socket.listen(1)
            while not (client_address[0] == ip_address):
                (conn, client_address) = self.TCP_listener_socket.accept()
            self.TCP_conv_socket = conn
        else:
            time.sleep(1)
            print(self.TCP_listener_socket.gettimeout(),"   TCP2 TIMEOUT")
            self.TCP_listener_socket.connect((ip_address,ClientProtocol.PORTSFORCOMMS[1]))
            self.TCP_conv_socket = self.TCP_listener_socket
        self.UDP_conv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Send game info messages
        self.UDP_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Send game info messages
        
        print("Middle of init")

        self.udp_thread = threading.Thread(target=self.udp_thread_func, args=[self.UDP_server,ip_address,self.enemy_move_text])
        self.tcp_thread = threading.Thread(target=self.tcp_thread_func, args=[self.TCP_conv_socket])
        self.udp_thread.start()
        self.tcp_thread.start()

        self.online_address= ip_address

        self.mouse_of_enemy = drawable.drawable(screen=self.screen, origin="cursor", visual_rect=[0,0,26,32])
        self.fg_obj.append(self.mouse_of_enemy)
        print("End of init")
    
    def react_to_input(self):
        my_mouse_pos = pygame.mouse.get_pos()
        my_mouse_clicked = pygame.mouse.get_pressed()[0]

        enemy_mouse_pos, enemy_is_clicked = ClientProtocol.parse_mouse_and_click_msg(self.enemy_move_text[0]) # In win states mouse pos is None and isclicked is the winning team
        
        if enemy_mouse_pos == None: # Got a win command
            self.win(team=int(is_clicked))
            enemy_mouse_pos, enemy_is_clicked = (0,0) , False
            return
        
        self.mouse_of_enemy.transpose_to(enemy_mouse_pos[0],enemy_mouse_pos[1]-32)

        msg = "MOUSE|"
        msg += str(my_mouse_pos[0]).zfill(4)+"#"+str(my_mouse_pos[1]).zfill(4)
        msg += "#" + ("FALSE","TRUE")[int(my_mouse_clicked)]
        # print("UDP sending",msg)
        msg = str(ClientProtocol.encrypt(msg,ClientProtocol.KEYS[1])).encode()
        self.UDP_conv_socket.sendto(msg, (self.online_address,ClientProtocol.PORTSFORCOMMS[2]))

        if self.game_state[0] == self.team_of_player:
            mouse_pos = my_mouse_pos
            is_clicked = my_mouse_clicked
        else:
            mouse_pos = enemy_mouse_pos
            is_clicked = enemy_is_clicked
        self.handle_but_presses(mouse_pos=mouse_pos, is_mouse_pressed=is_clicked)

    @staticmethod
    def udp_thread_func(UDP_serveresque_socket, ip_address, enemy_move_text):
        UDP_SOCKET_MAX_SIZE = 21
        UDP_serveresque_socket.bind(("0.0.0.0",ClientProtocol.PORTSFORCOMMS[2]))
        response = ClientProtocol.encrypt("MOUSE|0000#0000#TRUE",ClientProtocol.KEYS[1])
        while len(response) > 0:
            try:
                (new_response, remote_address) = UDP_serveresque_socket.recvfrom(UDP_SOCKET_MAX_SIZE)
                #print("UDP recv",new_response,"from",remote_address[0],(ip_address == remote_address[0]))
            except Exception as e:
                print("closed UDP due to exception",e)
                UDP_serveresque_socket.close()
                return
            if ip_address == remote_address[0]:
                # Check if overwriting is even necessary
                data = enemy_move_text[0]
                if ClientProtocol.decrypt(data,ClientProtocol.KEYS[1]).startswith("WIN"):
                    print("closed UDP due to win text")
                    UDP_serveresque_socket.close()
                    return

                # Else, write the new data in
                response = new_response.decode()
                enemy_move_text[0] = response
            
        print("closed UDP due to none text")
        return
  
    @staticmethod
    def tcp_thread_func(conv_socket):
        TCP_SOCKET_MAX_SIZE=11
        response = "DontQuitYet"
        while len(response) > 0:
            try:
                response = conv_socket.recv(TCP_SOCKET_MAX_SIZE)
            except Exception as e:
                print("closed TCP due to exception",e)
                conv_socket.close()
                return
            response = ClientProtocol.decrypt(response,ClientProtocol.KEYS[1])
            if response.startswith("WIN|"):
                info = "PZ"["PZ".find(response[-1])]
                print("closing TCP due to win text",response,info)
                try:
                    conv_socket.send((ClientProtocol.encrypt("WINCONFIRM|")).encode())
                except:
                    pass

                print("closed TCP due to win text")
                time.sleep(2)
                conv_socket.close()
                return
            
            elif response.startswith("WINCONFIRM|"):
                print("closing TCP due to winconfirm text",response)
                time.sleep(2)
                conv_socket.close()
                return
            
        print("closed TCP due to none text")
        conv_socket.close()
        return
    
    def win(self, unit_responsible=None, team=0):
        print("WIN GAME",team)
        self.enemy_move_text[0] = "WIN|"+str(team)
        self.TCP_conv_socket.close()
        self.TCP_listener_socket.close()
        self.UDP_server.close()
        self.tcp_thread.join()
        self.udp_thread.join()
        super().win(unit_responsible, team)
    
    def quit_game(self):
        self.TCP_conv_socket.close()
        try:
            self.TCP_listener_socket.close()
        except Exception as e:
            print("QuitErr1",e)
        self.UDP_server.close()
        self.UDP_conv_socket.close()
        self.tcp_thread.join()
        self.udp_thread.join()
        return super().quit_game()
