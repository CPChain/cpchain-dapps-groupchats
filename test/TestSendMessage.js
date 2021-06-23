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
    truffleAssert.eventEmitted(tx, 'SendMessage', (e) => {
      assert.equal(e.id, 1)
      assert.equal(e.sender, accounts[0])
      assert.equal(e.message, 'message')
      assert.equal(e.sentSeq, 1)
      assert.equal(e.msgSeq, 1)
      assert.equal(e.blockNumber, tx.receipt.blockNumber)
      return true
    })
  })
  it('Send message to an unexists group', async ()=> {
    const instance = await GroupChat.deployed();
    try {
      await instance.sendMessage(2, 'message')
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("The group not exists"))
    }
  })
  it('Send message a unjoined group', async ()=> {
    const instance = await GroupChat.deployed();
    try {
      await instance.sendMessage(1, 'message', {from: accounts[1]})
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("You're not exists in this group"))
    }
  })
  it('accounts[1] join the group and send a message', async ()=> {
    const instance = await GroupChat.deployed();
    await instance.join(1, {from: accounts[1]})
    let tx = await instance.sendMessage(1, 'message', {from: accounts[1]})
    truffleAssert.eventEmitted(tx, 'SendMessage', (e) => {
      assert.equal(e.id, 1)
      assert.equal(e.sender, accounts[1])
      assert.equal(e.message, 'message')
      assert.equal(e.sentSeq, 1)
      assert.equal(e.msgSeq, 2)
      assert.equal(e.blockNumber, tx.receipt.blockNumber)
      return true
    })
  })
  it('accounts[0] send 10 transactions', async ()=> {
    const instance = await GroupChat.deployed();
    let sentSeq = 2
    let msgSeq = 3
    for(let i = 0; i < 10; i++) {
      let tx = await instance.sendMessage(1, 'message' + i)
      truffleAssert.eventEmitted(tx, 'SendMessage', (e) => {
        assert.equal(e.id, 1)
        assert.equal(e.sender, accounts[0])
        assert.equal(e.message, 'message' + i)
        assert.equal(e.sentSeq, sentSeq + i)
        assert.equal(e.msgSeq, msgSeq + i)
        assert.equal(e.blockNumber, tx.receipt.blockNumber)
        return true
      })
    }
  })
  it('Send message after quit group', async ()=> {
    const instance = await GroupChat.deployed();
    // quit
    await instance.quit(1, {from: accounts[1]})

    // send message
    try {
      await instance.sendMessage(1, 'message', {from: accounts[1]})
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("You're not exists in this group"))
    }
  })
})