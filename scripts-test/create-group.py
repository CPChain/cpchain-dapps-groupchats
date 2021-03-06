"""

1. 拉取身份注册的公钥
2. 与存储的私钥进行验证
3. 生成 AES 密钥并存储在文件中
4. 使用私钥加密
5. 创建公开群

source .env

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

address = "0x99a1241822011A95aBF6d32c00BB3dF0A6b717Ee"
with open(os.path.join('/Users/liaojinlong/Workspace/CPChain/cpchain-dapps-groupchats/build/contracts/GroupChat.json'), 'r') as f:
    abi = json.load(f)['abi']

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


def create_group():
    instance = cf.cpc.contract(abi=abi, address=address)
    keystore = os.environ.get('ADMIN_KEYSTORE')

    # 获取私钥
    with open(os.path.join(pwd, 'priv_key'), 'r') as f:
        priv_key = "".join(f.readlines()).strip()
        priv_key = identidy_decode(priv_key)

    sk = ecdsa.SigningKey.from_string(priv_key, ecdsa.SECP256k1, hashfunc=hashlib.sha256)
    
    # 生成 AES-256
    key = random_aes()

    # 签名
    sig = sk.sign(key)

    key_s = base64.b64encode(key).decode()
    sig_s = base64.b64encode(sig).decode()
    group_name = "group3"
    encryptedAES = f"""{{"key": "{key_s}","sig": "{sig_s}"}}"""
    print(encryptedAES)

    extend = """
    {
        "description": "desc"
    }
    """

    ks, frm = load_keystore(keystore)
    log.info(f"From {frm}")
    gas_price = cf.cpc.gasPrice
    nonce = cf.cpc.getTransactionCount(frm)
    tx = instance.functions.createPublicGroup(group_name, encryptedAES, 0, extend).buildTransaction({
        'gasPrice': gas_price,
        "nonce": nonce,
        "gas": 3000000,
        "from": frm,
        "value": cf.toWei(0, 'ether'),
        "type": 0,
        "chainId": 337
    })

    # send tx
    receipt = submit_tx(cf, ks, tx)

    if receipt.status != 0:
        events = instance.events['CreateGroup']().createFilter(
            fromBlock=receipt.blockNumber).get_all_entries()
        for e in events:
            name = e.args['name']
            log.info(f"Create group {name}")


def modify_group_name():
    instance = cf.cpc.contract(abi=abi, address=address)
    keystore = os.environ.get('ADMIN_KEYSTORE')

    ks, frm = load_keystore(keystore)
    log.info(f"From {frm}")
    gas_price = cf.cpc.gasPrice
    nonce = cf.cpc.getTransactionCount(frm)
    tx = instance.functions.setGroupName(2, "group2").buildTransaction({
        'gasPrice': gas_price,
        "nonce": nonce,
        "gas": 3000000,
        "from": frm,
        "value": cf.toWei(0, 'ether'),
        "type": 0,
        "chainId": 337
    })

    # send tx
    receipt = submit_tx(cf, ks, tx)

    if receipt.status != 0:
        events = instance.events['ModifyGroupName']().createFilter(
            fromBlock=receipt.blockNumber).get_all_entries()
        actual = instance.functions.getGroupName(1).call()
        for e in events:
            name = e.args['name']
            log.info(f"Modify group name to {name}, actual: {actual}")


def modify_extend_info():
    instance = cf.cpc.contract(abi=abi, address=address)
    keystore = os.environ.get('ADMIN_KEYSTORE')

    ks, frm = load_keystore(keystore)
    log.info(f"From {frm}")
    gas_price = cf.cpc.gasPrice
    nonce = cf.cpc.getTransactionCount(frm)
    tx = instance.functions.setExtend(1, '{"description":"desc0805"}').buildTransaction({
        'gasPrice': gas_price,
        "nonce": nonce,
        "gas": 3000000,
        "from": frm,
        "value": cf.toWei(0, 'ether'),
        "type": 0,
        "chainId": 337
    })

    # send tx
    receipt = submit_tx(cf, ks, tx)

    if receipt.status != 0:
        events = instance.events['ModifyGroupExtend']().createFilter(
            fromBlock=receipt.blockNumber).get_all_entries()
        actual = instance.functions.getExtend(1).call()
        for e in events:
            name = e.args['extend']
            log.info(f"Modify group {e.args['id']} extend to {name}, actual: {actual}")

def modify_price():
    instance = cf.cpc.contract(abi=abi, address=address)
    keystore = os.environ.get('ADMIN_KEYSTORE')

    ks, frm = load_keystore(keystore)
    log.info(f"From {frm}")
    gas_price = cf.cpc.gasPrice
    nonce = cf.cpc.getTransactionCount(frm)
    tx = instance.functions.setPrice(1, cf.toWei(0, 'ether')).buildTransaction({
        'gasPrice': gas_price,
        "nonce": nonce,
        "gas": 3000000,
        "from": frm,
        "value": cf.toWei(0, 'ether'),
        "type": 0,
        "chainId": 337
    })

    # send tx
    receipt = submit_tx(cf, ks, tx)

    if receipt.status != 0:
        events = instance.events['ModifyGroupPrice']().createFilter(
            fromBlock=receipt.blockNumber).get_all_entries()
        actual = instance.functions.getPrice(1).call()
        for e in events:
            name = e.args['price']
            log.info(f"Modify group {e.args['id']} price to {name}, actual: {actual}")


def modify_alias_name():
    instance = cf.cpc.contract(abi=abi, address=address)
    keystore = os.environ.get('ADMIN_KEYSTORE')

    ks, frm = load_keystore(keystore)
    log.info(f"From {frm}")
    gas_price = cf.cpc.gasPrice
    nonce = cf.cpc.getTransactionCount(frm)
    tx = instance.functions.setAliasName(1, 'admin').buildTransaction({
        'gasPrice': gas_price,
        "nonce": nonce,
        "gas": 3000000,
        "from": frm,
        "value": cf.toWei(0, 'ether'),
        "type": 0,
        "chainId": 337
    })

    # send tx
    receipt = submit_tx(cf, ks, tx)

    if receipt.status != 0:
        events = instance.events['ModifyAliasName']().createFilter(
            fromBlock=receipt.blockNumber).get_all_entries()
        actual = instance.functions.getAliasName(1, frm).call()
        for e in events:
            name = e.args['alias']
            log.info(f"Modify alias name of {e.args['id']} to {name}, actual: {actual}")


def ban_all():
    instance = cf.cpc.contract(abi=abi, address=address)
    keystore = os.environ.get('ADMIN_KEYSTORE')

    ks, frm = load_keystore(keystore)
    log.info(f"From {frm}")
    gas_price = cf.cpc.gasPrice
    nonce = cf.cpc.getTransactionCount(frm)
    tx = instance.functions.banAll(1).buildTransaction({
        'gasPrice': gas_price,
        "nonce": nonce,
        "gas": 3000000,
        "from": frm,
        "value": cf.toWei(0, 'ether'),
        "type": 0,
        "chainId": 337
    })

    # send tx
    receipt = submit_tx(cf, ks, tx)

    if receipt.status != 0:
        events = instance.events['BanAll']().createFilter(
            fromBlock=receipt.blockNumber).get_all_entries()
        if len(events) == 0:
            raise Exception('未触发 BanAll 事件')


def unban_all():
    instance = cf.cpc.contract(abi=abi, address=address)
    keystore = os.environ.get('ADMIN_KEYSTORE')

    ks, frm = load_keystore(keystore)
    log.info(f"From {frm}")
    gas_price = cf.cpc.gasPrice
    nonce = cf.cpc.getTransactionCount(frm)
    tx = instance.functions.unbanAll(1).buildTransaction({
        'gasPrice': gas_price,
        "nonce": nonce,
        "gas": 3000000,
        "from": frm,
        "value": cf.toWei(0, 'ether'),
        "type": 0,
        "chainId": 337
    })

    # send tx
    receipt = submit_tx(cf, ks, tx)

    if receipt.status != 0:
        events = instance.events['UnBanAll']().createFilter(
            fromBlock=receipt.blockNumber).get_all_entries()
        if len(events) == 0:
            raise Exception('未触发 UnBanAll 事件')


def user1_join():
    instance = cf.cpc.contract(abi=abi, address=address)
    keystore = os.environ.get('USER1')

    ks, frm = load_keystore(keystore)
    log.info(f"From {frm}")
    gas_price = cf.cpc.gasPrice
    nonce = cf.cpc.getTransactionCount(frm)
    tx = instance.functions.join(1).buildTransaction({
        'gasPrice': gas_price,
        "nonce": nonce,
        "gas": 3000000,
        "from": frm,
        "value": cf.toWei(0, 'ether'),
        "type": 0,
        "chainId": 337
    })

    # send tx
    receipt = submit_tx(cf, ks, tx)

    if receipt.status != 0:
        events = instance.events['JoinGroup']().createFilter(
            fromBlock=receipt.blockNumber).get_all_entries()
        if len(events) == 0:
            raise Exception('未触发 JoinGroup 事件')

def user1_quit():
    instance = cf.cpc.contract(abi=abi, address=address)
    keystore = os.environ.get('USER1')

    ks, frm = load_keystore(keystore)
    log.info(f"From {frm}")
    gas_price = cf.cpc.gasPrice
    nonce = cf.cpc.getTransactionCount(frm)
    tx = instance.functions.quit(1).buildTransaction({
        'gasPrice': gas_price,
        "nonce": nonce,
        "gas": 5000000,
        "from": frm,
        "value": cf.toWei(0, 'ether'),
        "type": 0,
        "chainId": 337
    })

    # send tx
    receipt = submit_tx(cf, ks, tx)

    if receipt.status != 0:
        events = instance.events['QuitGroup']().createFilter(
            fromBlock=receipt.blockNumber).get_all_entries()
        if len(events) == 0:
            raise Exception('未触发 QuitGroup 事件')


def send_message():
    instance = cf.cpc.contract(abi=abi, address=address)
    keystore = os.environ.get('USER1')

    ks, frm = load_keystore(keystore)
    log.info(f"From {frm}")
    gas_price = cf.cpc.gasPrice
    nonce = cf.cpc.getTransactionCount(frm)
    tx = instance.functions.sendMessage(1, "xxxx").buildTransaction({
        'gasPrice': gas_price,
        "nonce": nonce,
        "gas": 5000000,
        "from": frm,
        "value": cf.toWei(0, 'ether'),
        "type": 0,
        "chainId": 337
    })

    # send tx
    receipt = submit_tx(cf, ks, tx)

    if receipt.status != 0:
        events = instance.events['SendMessage']().createFilter(
            fromBlock=receipt.blockNumber).get_all_entries()
        if len(events) == 0:
            raise Exception('未触发 SendMessage 事件')    


def ban_user():
    instance = cf.cpc.contract(abi=abi, address=address)
    keystore = os.environ.get('ADMIN_KEYSTORE')

    ks, frm = load_keystore(keystore)
    log.info(f"From {frm}")
    gas_price = cf.cpc.gasPrice
    nonce = cf.cpc.getTransactionCount(frm)
    tx = instance.functions.ban(1, '0x0cE388B3CB9cb7dC9D26adf1Dc834b6E98927F23').buildTransaction({
        'gasPrice': gas_price,
        "nonce": nonce,
        "gas": 3000000,
        "from": frm,
        "value": cf.toWei(0, 'ether'),
        "type": 0,
        "chainId": 337
    })

    # send tx
    receipt = submit_tx(cf, ks, tx)

    if receipt.status != 0:
        events = instance.events['BanMember']().createFilter(
            fromBlock=receipt.blockNumber).get_all_entries()
        if len(events) == 0:
            raise Exception('未触发 BanMember 事件')


def unban_user():
    instance = cf.cpc.contract(abi=abi, address=address)
    keystore = os.environ.get('ADMIN_KEYSTORE')

    ks, frm = load_keystore(keystore)
    log.info(f"From {frm}")
    gas_price = cf.cpc.gasPrice
    nonce = cf.cpc.getTransactionCount(frm)
    tx = instance.functions.unban(1, '0x0cE388B3CB9cb7dC9D26adf1Dc834b6E98927F23').buildTransaction({
        'gasPrice': gas_price,
        "nonce": nonce,
        "gas": 3000000,
        "from": frm,
        "value": cf.toWei(0, 'ether'),
        "type": 0,
        "chainId": 337
    })

    # send tx
    receipt = submit_tx(cf, ks, tx)

    if receipt.status != 0:
        events = instance.events['UnbanMember']().createFilter(
            fromBlock=receipt.blockNumber).get_all_entries()
        if len(events) == 0:
            raise Exception('未触发 UnbanMember 事件')



def remove_user():
    instance = cf.cpc.contract(abi=abi, address=address)
    keystore = os.environ.get('ADMIN_KEYSTORE')

    ks, frm = load_keystore(keystore)
    log.info(f"From {frm}")
    gas_price = cf.cpc.gasPrice
    nonce = cf.cpc.getTransactionCount(frm)
    tx = instance.functions.remove(2, '0x0cE388B3CB9cb7dC9D26adf1Dc834b6E98927F23').buildTransaction({
        'gasPrice': gas_price,
        "nonce": nonce,
        "gas": 3000000,
        "from": frm,
        "value": cf.toWei(0, 'ether'),
        "type": 0,
        "chainId": 337
    })

    # send tx
    receipt = submit_tx(cf, ks, tx)

    if receipt.status != 0:
        events = instance.events['RemoveMember']().createFilter(
            fromBlock=receipt.blockNumber).get_all_entries()
        if len(events) == 0:
            raise Exception('未触发 RemoveMember 事件')


def change_owner_of_group():
    instance = cf.cpc.contract(abi=abi, address=address)
    keystore = os.environ.get('USER1')

    ks, frm = load_keystore(keystore)
    log.info(f"From {frm}")
    gas_price = cf.cpc.gasPrice
    nonce = cf.cpc.getTransactionCount(frm)
    tx = instance.functions.changeOwnerOfGroup(1, '0x1455D180E3adE94ebD9cC324D22a9065d1F5F575').buildTransaction({
        'gasPrice': gas_price,
        "nonce": nonce,
        "gas": 3000000,
        "from": frm,
        "value": cf.toWei(0, 'ether'),
        "type": 0,
        "chainId": 337
    })

    # send tx
    receipt = submit_tx(cf, ks, tx)

    if receipt.status != 0:
        events = instance.events['ChangeGroupOwner']().createFilter(
            fromBlock=receipt.blockNumber).get_all_entries()
        if len(events) == 0:
            raise Exception('未触发 ChangeGroupOwner 事件')


def upgrade_aes():
    # 读取身份注册的私钥
    with open(os.path.join(pwd, 'priv_key'), 'r') as f:
        priv_key = "".join(f.readlines()).strip()
        priv_key = identidy_decode(priv_key)

    sk = ecdsa.SigningKey.from_string(priv_key, ecdsa.SECP256k1, hashfunc=hashlib.sha256)
    
    # 生成 AES-256
    key = random_aes()

    # 使用身份注册的私钥对 AES 密钥签名
    sig = sk.sign(key)

    key_s = base64.b64encode(key).decode()
    sig_s = base64.b64encode(sig).decode()
    encryptedAES = f"""{{"key": "{key_s}","sig": "{sig_s}"}}"""

    instance = cf.cpc.contract(abi=abi, address=address)
    keystore = os.environ.get('ADMIN_KEYSTORE')

    ks, frm = load_keystore(keystore)
    log.info(f"From {frm}")
    gas_price = cf.cpc.gasPrice
    nonce = cf.cpc.getTransactionCount(frm)
    tx = instance.functions.setEncrypedAES(1, encryptedAES).buildTransaction({
        'gasPrice': gas_price,
        "nonce": nonce,
        "gas": 3000000,
        "from": frm,
        "value": cf.toWei(0, 'ether'),
        "type": 0,
        "chainId": 337
    })

    # send tx
    receipt = submit_tx(cf, ks, tx)

    if receipt.status != 0:
        events = instance.events['UpgradeEncryptedAES']().createFilter(
            fromBlock=receipt.blockNumber).get_all_entries()
        if len(events) == 0:
            raise Exception('未触发 UpgradeEncryptedAES 事件')

def add_application():
    instance = cf.cpc.contract(abi=abi, address=address)
    keystore = os.environ.get('ADMIN_KEYSTORE')

    ks, frm = load_keystore(keystore)
    log.info(f"From {frm}")
    gas_price = cf.cpc.gasPrice
    nonce = cf.cpc.getTransactionCount(frm)
    tx = instance.functions.addApplication('0x0cE388B3CB9cb7dC9D26adf1Dc834b6E98927F23').buildTransaction({
        'gasPrice': gas_price,
        "nonce": nonce,
        "gas": 3000000,
        "from": frm,
        "value": cf.toWei(0, 'ether'),
        "type": 0,
        "chainId": 337
    })

    # send tx
    receipt = submit_tx(cf, ks, tx)

    if receipt.status != 0:
        events = instance.events['AddApplication']().createFilter(
            fromBlock=receipt.blockNumber).get_all_entries()
        if len(events) == 0:
            raise Exception('未触发 AddApplication 事件')

def remove_application():
    instance = cf.cpc.contract(abi=abi, address=address)
    keystore = os.environ.get('ADMIN_KEYSTORE')

    ks, frm = load_keystore(keystore)
    log.info(f"From {frm}")
    gas_price = cf.cpc.gasPrice
    nonce = cf.cpc.getTransactionCount(frm)
    tx = instance.functions.removeApplication('0x0cE388B3CB9cb7dC9D26adf1Dc834b6E98927F23').buildTransaction({
        'gasPrice': gas_price,
        "nonce": nonce,
        "gas": 3000000,
        "from": frm,
        "value": cf.toWei(0, 'ether'),
        "type": 0,
        "chainId": 337
    })

    # send tx
    receipt = submit_tx(cf, ks, tx)

    if receipt.status != 0:
        events = instance.events['RemoveApplication']().createFilter(
            fromBlock=receipt.blockNumber).get_all_entries()
        if len(events) == 0:
            raise Exception('未触发 RemoveApplication 事件')



if __name__ == '__main__':
    # create_group()
    # modify_group_name()
    # modify_extend_info()
    # modify_price()
    # modify_alias_name()
    # ban_all()
    # unban_all()
    user1_join()
    # user1_quit()
    # send_message()
    # ban_user()
    # unban_user()
    # change_owner_of_group()
    # upgrade_aes()
    # add_application()
    # remove_application()
    # remove_user()
    # test_pri_pub()
    # test_ecdsa()
    # test_aes()
