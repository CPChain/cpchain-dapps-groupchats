const GroupChat = artifacts.require("GroupChat");
const truffleAssert = require("truffle-assertions");
const utils = require("./utils")

contract("GroupChat", (accounts) => {
  it("Create group", async () => {
    const instance = await GroupChat.deployed();
    await instance.createPublicGroup('test', 'xxxx', 0, '{}')
  })
  it("Add application", async () => {
    const instance = await GroupChat.deployed();
    let tx = await instance.addApplication(accounts[1])
    truffleAssert.eventEmitted(tx, 'AddApplication', (e) => {
      assert.equal(e.addr, accounts[1])
      return true
    })
    // add again
    try {
      await instance.addApplication(accounts[1])
      assert.fail()
    } catch(err) {
      assert.ok(err.toString().includes("This application already exists!"))
    }
  })
  it("Remove application", async () => {
    const instance = await GroupChat.deployed();
    let tx = await instance.removeApplication(accounts[1])
    truffleAssert.eventEmitted(tx, 'RemoveApplication', (e) => {
      assert.equal(e.addr, accounts[1])
      return true
    })
    // remove again
    try {
      await instance.removeApplication(accounts[1])
      assert.fail()
    } catch(err) {
      assert.ok(err.toString().includes("Not found"))
    }
    // add after remove
    await instance.addApplication(accounts[1])
  })
  it("send message", async ()=> {
    const instance = await GroupChat.deployed();
    // send message
    try {
      await instance.sendMessage(1, 'message', {from: accounts[2]})
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("You're not exists in this group"))
    }
    // send message with application
    await instance.sendMessage(1, 'message', {from: accounts[1]})
  })
})
