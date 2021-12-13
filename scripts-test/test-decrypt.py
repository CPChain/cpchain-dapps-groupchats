
from Crypto.Cipher import AES
import base64
import json

def test():
    key = '6uOKbkFQ3NE8gyOuhs1quuE3Gf9fyrH2qRr1o6sDI8c='
    decoded_key = base64.b64decode(key)
    assert len(decoded_key) == 32

    msg = json.loads("{\"message\":{\"iv\":\"raa3PZPJe+u+dqMcliCFww==\",\"ciphertext\":\"WO0lb2mnp8y8k1h0sdHZpyETtiv0Qq47RGaGSbGxMMk=\",\"inputType\":\"text\"},\"version\":1}")
    iv = msg['message']['iv']
    decoded_iv = base64.b64decode(iv)
    assert len(decoded_iv) == 16

    text = msg['message']['ciphertext']
    decoded_text = base64.b64decode(text)

    # decrypt
    cipher = AES.new(decoded_key, AES.MODE_CBC, decoded_iv)
    decrypted = cipher.decrypt(decoded_text)
    print(decrypted.decode())

if __name__ == '__main__':
    test()
