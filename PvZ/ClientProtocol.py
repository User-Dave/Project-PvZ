import os

KEYS = ["MainServerMessages".upper(),
        "GameMessages".upper()]
PORTSFORCOMMS = [8999, # main server from client (waiting room conn)
                 9000, # P2P TCP
                 9001] # P2P UDP

def open_file_with(this_file,file_to_open,open_mode):
    # Feed this_file with __file__ only!
    path_to_here = (os.path.realpath(this_file))
    path_to_dir = path_to_here[:path_to_here.rfind("\\")]
    path_to_file = os.path.join(path_to_dir,file_to_open)
    x = open(path_to_file, open_mode)
    return x

def ceasar_cipher_encode(msg, offset):
    ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    offsetalphabet = ALPHABET[offset:] + ALPHABET[:offset]
    s=""
    for i in msg:
        if i in ALPHABET:
            s += offsetalphabet[ALPHABET.index(i)]
        else:
            s += i
    return s

def ceasar_cipher_decode(msg, offset):
    ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    offsetalphabet = ALPHABET[offset:] + ALPHABET[:offset]
    s=""
    for i in msg:
        if i in ALPHABET:
            s += ALPHABET[offsetalphabet.index(i)]
        else:
            s += i
    return s

def create_vigenere_table():
  ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  table = []
  for i in range(26):
    string = ceasar_cipher_encode(ALPHABET,i)
    curr_table = list(string)
    table.append(curr_table)
  return table

def vigenere_encode(plaintext,key):
    ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    keylong = ""
    for i in range(len(plaintext)):
      keylong += key[i%len(key)].upper()
    TABLE = create_vigenere_table()
    ans = ""
    for i in range(len(plaintext)):
        if (plaintext[i] in ALPHABET):
            ans += TABLE[ord((plaintext.upper())[i])-65][ord(keylong[i])-65]
        else:
            ans += plaintext[i]
    return ans

def vigenere_decode(ciphertext,key):
    ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    keylong = ""
    ciphertext = ciphertext.upper()
    for i in range(len(ciphertext)):
      keylong += key[i%len(key)].upper()
    TABLE = create_vigenere_table()
    ans = ""
    for i in range(len(ciphertext)):
        if (ciphertext[i] in ALPHABET):
            ans += chr(65+TABLE[ord(keylong[i])-65].index(ciphertext[i]))
        else:
            ans += ciphertext[i]
    return ans

def encrypt(text, key):
    return vigenere_encode(text, key)

def decrypt(text, key):
    return vigenere_decode(text, key)


def parse_mouse_and_click_msg(txt):
    txt = decrypt(txt, KEYS[1])
    print("parsing",txt)
    parts = txt.split("|")
    if parts[0] == "MOUSE":
        x,y,ismouse = parts[1].split("#")
        return ((int(x),int(y)),(ismouse == "TRUE"))
    elif parts[0] == "WIN":
        return (None,parts[1])
    else:
        print(f"RETURNING SMTH ELSE FOR TXT={txt}")
        return ((0,0),True)


if __name__ == '__main__': # TESTING ENCRYPTION AND DECRYPTION
    x = input("msg:")
    y=encrypt(x, KEYS[0])
    z=decrypt(y, KEYS[0])
    print(y)
    print(z)
