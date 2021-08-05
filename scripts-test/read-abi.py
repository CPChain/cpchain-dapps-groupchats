"""

get abi

"""

import json

def read_abi():
    with open('build/contracts/GroupChat.json', 'r') as fr:
        print(json.dumps(json.load(fr)['abi']))

if __name__ == '__main__':
    read_abi()
