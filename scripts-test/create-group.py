"""

1. 拉取身份注册的公钥
2. 与存储的私钥进行验证
3. 生成 AES 密钥并存储在文件中
4. 使用私钥加密
5. 创建公开群

!pip install eciespy
!pip install ecdsa

{"message":{"iv":"MmM0MDEyM2NhMmYyYWY5M2UzZmIzNTc3OTJkNWFmNGE=","ciphertext":"Zjk3ODdmMzdhN2U5M2U3Yzg1NjM3NzY1OWYzOGQ3NTE=","mac":"MTMyNDRmODg0N2M0OTU4MjI4ZTE1MGM0MDM1YWUxOTIyYTU1MDE0MGIyYjdkYTZhOGQ1Yjg0ZjU0ZGE5MjQyZA=="},"version":1}

"""

import string
import random
import hashlib
import getpass
import os
import json
import base64
import logging
import sys
import ecdsa
from Crypto.Cipher import AES
from Crypto import Random

from cpc_fusion import Web3

from ecies import encrypt, decrypt

pwd = os.path.dirname(os.path.abspath(__file__))

cf = Web3(Web3.HTTPProvider("https://civilian.cpchain.io"))

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger()

identity_abi = "[{\"constant\":true,\"inputs\":[],\"name\":\"count\",\"outputs\":[{\"name\":\"\",\"type\":\"uint256\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[],\"name\":\"enabled\",\"outputs\":[{\"name\":\"\",\"type\":\"bool\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[],\"name\":\"enableContract\",\"outputs\":[],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[],\"name\":\"disableContract\",\"outputs\":[],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[],\"name\":\"remove\",\"outputs\":[],\"payable\":true,\"stateMutability\":\"payable\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[{\"name\":\"addr\",\"type\":\"address\"}],\"name\":\"get\",\"outputs\":[{\"name\":\"\",\"type\":\"string\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[{\"name\":\"content\",\"type\":\"string\"}],\"name\":\"register\",\"outputs\":[],\"payable\":true,\"stateMutability\":\"payable\",\"type\":\"function\"},{\"inputs\":[],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"constructor\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":false,\"name\":\"who\",\"type\":\"address\"},{\"indexed\":false,\"name\":\"identity\",\"type\":\"string\"}],\"name\":\"NewIdentity\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":false,\"name\":\"who\",\"type\":\"address\"},{\"indexed\":false,\"name\":\"identity\",\"type\":\"string\"}],\"name\":\"UpdateIdentity\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":false,\"name\":\"who\",\"type\":\"address\"}],\"name\":\"RemoveIdentity\",\"type\":\"event\"}]"
identity_addr = "0xC53367856164DA3De57784E0c96710088DA77e20"

address = "0x262Fced17e07FaE9e5750653bc6FF5882AF9953E"
abi = '[{"constant": true, "inputs": [], "name": "enabled", "outputs": [{"name": "", "type": "bool"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": true, "inputs": [], "name": "members_upper_limit", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": true, "inputs": [], "name": "name_len_limit", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "stateMutability": "view", "type": "function"}, {"inputs": [], "payable": false, "stateMutability": "nonpayable", "type": "constructor"}, {"anonymous": false, "inputs": [{"indexed": false, "name": "is_private", "type": "bool"}, {"indexed": false, "name": "name", "type": "string"}, {"indexed": false, "name": "encryptedAES", "type": "string"}, {"indexed": false, "name": "price", "type": "uint256"}, {"indexed": false, "name": "extend", "type": "string"}, {"indexed": false, "name": "id", "type": "uint256"}], "name": "CreateGroup", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "name": "id", "type": "uint256"}, {"indexed": false, "name": "name", "type": "string"}], "name": "ModifyGroupName", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "name": "id", "type": "uint256"}, {"indexed": false, "name": "extend", "type": "string"}], "name": "ModifyGroupExtend", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "name": "id", "type": "uint256"}, {"indexed": false, "name": "price", "type": "uint256"}], "name": "ModifyGroupPrice", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "name": "id", "type": "uint256"}, {"indexed": false, "name": "member", "type": "address"}, {"indexed": false, "name": "alias", "type": "string"}], "name": "ModifyAliasName", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "name": "id", "type": "uint256"}, {"indexed": false, "name": "addr", "type": "address"}], "name": "JoinGroup", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "name": "id", "type": "uint256"}, {"indexed": false, "name": "addr", "type": "address"}], "name": "QuitGroup", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "name": "id", "type": "uint256"}, {"indexed": false, "name": "admin", "type": "address"}, {"indexed": false, "name": "member", "type": "address"}], "name": "RemoveMember", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "name": "id", "type": "uint256"}, {"indexed": false, "name": "admin", "type": "address"}, {"indexed": false, "name": "member", "type": "address"}], "name": "BanMember", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "name": "id", "type": "uint256"}, {"indexed": false, "name": "admin", "type": "address"}, {"indexed": false, "name": "member", "type": "address"}], "name": "UnbanMember", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "name": "id", "type": "uint256"}, {"indexed": false, "name": "encryptedAES", "type": "string"}, {"indexed": false, "name": "blockNumber", "type": "uint256"}], "name": "UpgradeEncryptedAES", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "name": "id", "type": "uint256"}, {"indexed": false, "name": "sender", "type": "address"}, {"indexed": false, "name": "message", "type": "string"}, {"indexed": false, "name": "sentSeq", "type": "uint256"}, {"indexed": false, "name": "msgSeq", "type": "uint256"}, {"indexed": false, "name": "blockNumber", "type": "uint256"}], "name": "SendMessage", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "name": "id", "type": "uint256"}, {"indexed": false, "name": "admin", "type": "address"}], "name": "ChangeGroupOwner", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "name": "id", "type": "uint256"}, {"indexed": false, "name": "admin", "type": "address"}], "name": "BanAll", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "name": "id", "type": "uint256"}, {"indexed": false, "name": "admin", "type": "address"}], "name": "UnBanAll", "type": "event"}, {"constant": false, "inputs": [], "name": "enableContract", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": false, "inputs": [], "name": "disableContract", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": false, "inputs": [{"name": "name", "type": "string"}, {"name": "encryptedAES", "type": "string"}, {"name": "price", "type": "uint256"}, {"name": "extend", "type": "string"}], "name": "createPublicGroup", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": true, "inputs": [{"name": "name", "type": "string"}], "name": "checkGroupName", "outputs": [{"name": "", "type": "bool"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": false, "inputs": [{"name": "name", "type": "string"}, {"name": "price", "type": "uint256"}, {"name": "extend", "type": "string"}], "name": "createPrivateGroup", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": true, "inputs": [{"name": "id", "type": "uint256"}], "name": "getGroupName", "outputs": [{"name": "", "type": "string"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": false, "inputs": [{"name": "id", "type": "uint256"}, {"name": "name", "type": "string"}], "name": "setGroupName", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": true, "inputs": [{"name": "id", "type": "uint256"}], "name": "countOf", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": true, "inputs": [{"name": "id", "type": "uint256"}], "name": "getPrice", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": false, "inputs": [{"name": "id", "type": "uint256"}, {"name": "price", "type": "uint256"}], "name": "setPrice", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": true, "inputs": [{"name": "id", "type": "uint256"}], "name": "getExtend", "outputs": [{"name": "", "type": "string"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": false, "inputs": [{"name": "id", "type": "uint256"}, {"name": "extend", "type": "string"}], "name": "setExtend", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": true, "inputs": [{"name": "id", "type": "uint256"}], "name": "getEncryptedAES", "outputs": [{"name": "", "type": "string"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": false, "inputs": [{"name": "id", "type": "uint256"}, {"name": "encryptedAES", "type": "string"}], "name": "setEncrypedAES", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": false, "inputs": [{"name": "id", "type": "uint256"}], "name": "join", "outputs": [], "payable": true, "stateMutability": "payable", "type": "function"}, {"constant": false, "inputs": [{"name": "id", "type": "uint256"}], "name": "quit", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": false, "inputs": [{"name": "id", "type": "uint256"}, {"name": "alias", "type": "string"}], "name": "setAliasName", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": true, "inputs": [{"name": "id", "type": "uint256"}, {"name": "member", "type": "address"}], "name": "getAliasName", "outputs": [{"name": "", "type": "string"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": false, "inputs": [{"name": "id", "type": "uint256"}, {"name": "member", "type": "address"}], "name": "remove", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": false, "inputs": [{"name": "id", "type": "uint256"}, {"name": "member", "type": "address"}], "name": "ban", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": false, "inputs": [{"name": "id", "type": "uint256"}, {"name": "member", "type": "address"}], "name": "unban", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": true, "inputs": [{"name": "id", "type": "uint256"}, {"name": "member", "type": "address"}], "name": "isBanned", "outputs": [{"name": "", "type": "bool"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": true, "inputs": [{"name": "id", "type": "uint256"}, {"name": "member", "type": "address"}], "name": "has", "outputs": [{"name": "", "type": "bool"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": false, "inputs": [{"name": "limit", "type": "uint256"}], "name": "setUpperLimit", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": false, "inputs": [{"name": "id", "type": "uint256"}, {"name": "to", "type": "address"}], "name": "changeOwnerOfGroup", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": false, "inputs": [{"name": "id", "type": "uint256"}, {"name": "message", "type": "string"}], "name": "sendMessage", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": false, "inputs": [{"name": "id", "type": "uint256"}], "name": "banAll", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": false, "inputs": [{"name": "id", "type": "uint256"}], "name": "unbanAll", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": true, "inputs": [{"name": "id", "type": "uint256"}], "name": "isBanAll", "outputs": [{"name": "", "type": "bool"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": false, "inputs": [{"name": "len", "type": "uint256"}], "name": "setNameLenLimit", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": false, "inputs": [{"name": "to", "type": "address"}], "name": "changeOwner", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}]'


def identidy_decode(key):
    key = base64.b64decode(key)
    key = bytes.fromhex(key.decode())
    return key


def test_pri_pub():
    """
    对加密聊天的公私钥进行加解密测试
    """
    instance = cf.cpc.contract(abi=identity_abi, address=identity_addr)
    cpchain_tech = cf.toChecksumAddress(
        "0x1455d180e3ade94ebd9cc324d22a9065d1f5f575")
    pub_key_str = instance.functions.get(cpchain_tech).call()
    with open('pub_key', 'w') as f:
        f.write(json.loads(pub_key_str)['pub_key'])
    pub_key = identidy_decode(json.loads(pub_key_str)['pub_key'])

    # read private key in base64 format
    with open(os.path.join(pwd, 'priv_key'), 'r') as f:
        priv_key = "".join(f.readlines()).strip()
        priv_key = identidy_decode(priv_key)

    msg = encrypt(pub_key, b'hello world')

    result = decrypt(priv_key, msg)
    print(result.decode())


def test_ecdsa():
    with open(os.path.join(pwd, 'priv_key'), 'r') as f:
        priv_key = "".join(f.readlines()).strip()
        priv_key = identidy_decode(priv_key)

    sk = ecdsa.SigningKey.from_string(priv_key, ecdsa.SECP256k1, hashfunc=hashlib.sha256)
    vk = sk.verifying_key # 用私钥推出的公钥
    signature = sk.sign(b"message")
    assert vk.verify(signature, b"message")

    with open(os.path.join(pwd, 'pub_key'), 'r') as f:
        pub_key = "".join(f.readlines()).strip()
        pub_key = identidy_decode(pub_key)
    
    # 用存储的公钥
    vk = ecdsa.VerifyingKey.from_string(pub_key, ecdsa.SECP256k1, hashfunc=hashlib.sha256)
    assert vk.verify(signature, b"message")

def random_aes():
    return bytes(''.join(random.sample(string.ascii_letters + string.digits + string.punctuation, 32)), 'UTF-8')


def test_aes():
    key = random_aes()
    bs = AES.block_size
    iv = Random.new().read(bs) # iv 是偏移量
    print('len of key:', len(key))
    cipher = AES.new(key, AES.MODE_CBC, iv)

    pad = lambda s: s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

    msg = 'hello world'
    print("len of msg:", len(msg))

    encrypted = cipher.encrypt(bytes(pad(msg), 'utf-8'))
    encrypted = iv + encrypted
    print("len of encrypted msg:", len(encrypted))

    cipher2 = AES.new(key, AES.MODE_CBC, iv)
    # unpad = lambda s : s[0:-ord(s[-1])]
    decrypted = cipher2.decrypt(encrypted[bs:])
    print(decrypted.decode())



def load_keystore(keystorePath):
    with open(keystorePath, 'r') as fr:
        ks = json.load(fr)
        addr = cf.toChecksumAddress(ks['address'])
        return ks, addr


def submit_tx(cf, ks, tx, password_file=None):
    if password_file is None:
        password = getpass.getpass("Please input your password: ")
    else:
        with open(password_file, 'r') as f:
            password = "".join(f.readlines())
        password = password.strip()
    decrypted_key = cf.cpc.account.decrypt(ks, password)
    password = ""
    signed_txn = cf.cpc.account.signTransaction(tx, decrypted_key)
    tx_hash = cf.cpc.sendRawTransaction(signed_txn.rawTransaction)
    receipt = cf.cpc.waitForTransactionReceipt(tx_hash)
    if receipt.status == 0:
        print(receipt)
        log.info('Sorry, failed.')
    else:
        log.info('Success')
    return receipt


def main():
    instance = cf.cpc.contract(abi=abi, address=address)
    keystore = os.environ.get('ADMIN_KEYSTORE')
    password = os.environ.get('ADMIN_PASSWORD')

    # 获取私钥
    with open(os.path.join(pwd, 'priv_key'), 'r') as f:
        priv_key = "".join(f.readlines()).strip()
        priv_key = identidy_decode(priv_key)

    sk = ecdsa.SigningKey.from_string(priv_key, ecdsa.SECP256k1, hashfunc=hashlib.sha256)
    
    # 生成 AES-256


    
    group_name = "group1"
    encryptedAES = """
    {
        "key": "",
        "sig": ""
    }
    """
    print(encryptedAES)
    return

    extend = """
    {
        "description": ""
    }
    """

    ks, frm = load_keystore(keystore)
    gas_price = cf.cpc.gasPrice
    nonce = cf.cpc.getTransactionCount(frm)
    tx = instance.functions.createPublicGroup(group_name, encryptedAES, 0, extend).buildTransaction({
        'gasPrice': gas_price,
        "nonce": nonce,
        "gas": 300000,
        "from": frm,
        "value": cf.toWei(0, 'ether'),
        "type": 0,
        "chainId": 337
    })

    # send tx
    receipt = submit_tx(cf, ks, tx, password)

    if receipt.status != 0:
        events = instance.events['AdminAppealRefund']().createFilter(
            fromBlock=receipt.blockNumber).get_all_entries()
        for e in events:
            value = cf.fromWei(e.args['amount'], 'ether')
            log.info(
                f"Refund to: {e.args['user']}, value: {value}")


if __name__ == '__main__':
    # main()
    # test_pri_pub()
    # test_ecdsa()
    test_aes()
