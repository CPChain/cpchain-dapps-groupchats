const GroupChat = artifacts.require("GroupChat");
const truffleAssert = require("truffle-assertions");
const utils = require("./utils")

contract("GroupChat", (accounts) => {
  it("Create group", async () => {
    const instance = await GroupChat.deployed();
    await instance.createPublicGroup('test', 'xxxx', 0, '{}')
  })
  it("Send Message", async ()=> {
    const instance = await GroupChat.deployed();
    let tx = await instance.sendMessage(1, 'message')
    
  })
  
})