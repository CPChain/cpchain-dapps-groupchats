# CPChain Encrypted Group Chats

![Test Coverage Badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/zgljl2012/676521a4ad619576708a8aad39a1eaaa/raw/cpchain_dapps_groupchats__heads_main.json)

## Deploy

```bash

pip install cpc-fusion

cpc-fusion deploy --keystore <your keystore> --abi build/contracts/GroupChat.json

# Get configs
cpc-fusion get-configs --abi build/contracts/GroupChat.json --address <address>

# Set the upper limit of members
cpc-fusion call-func --abi build/contracts/GroupChat.json --address <address> --keystore <your keystore> --function setUpperLimit --parameters 120

```

## AES Key

Please use 128 bit (16 Byte) AES, e.g. FsFSlCZ5Zqe6E2Hp.
