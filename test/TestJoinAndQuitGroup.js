const GroupChat = artifacts.require("GroupChat");
const truffleAssert = require("truffle-assertions");
const utils = require("./utils")

contract("GroupChat", (accounts) => {
  it("Create group", async () => {
    const instance = await GroupChat.deployed();
    await instance.createPublicGroup('test', 'xxxx', 0, '{}')
  })
  it("Join group with 0 cpc", async () => {
    const instance = await GroupChat.deployed();
    try {
      await instance.join(1)
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes('You have joinned this group'))
    }
    let tx = await instance.join(1, {from: accounts[1]})
    truffleAssert.eventEmitted(tx, 'JoinGroup', (e) => {
      assert.equal(e.id, 1)
      assert.equal(e.addr, accounts[1])
      return true
    })
    assert.equal(await instance.countOf(1), 2, 'The cnt of group is error')
    assert.equal(await instance.has(1, accounts[1]), true)
    assert.equal(await instance.has(1, accounts[2]), false)
  })
  it('create a group with price', async ()=> {
    const instance = await GroupChat.deployed();
    await instance.createPublicGroup('test2', 'xxxx', utils.cpc(1), '{}')
  })
  it('join group with cpc', async ()=> {
    const instance = await GroupChat.deployed();
    const balance0_1 = await utils.getBalance(accounts[0])
    try {
      await instance.join(2, {from: accounts[2]})
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes('The value is not equal to the price'))
    }
    let tx = await instance.join(2, {from: accounts[2], value: utils.cpc(1)})
    truffleAssert.eventEmitted(tx, 'JoinGroup', (e) => {
      assert.equal(e.id, 2)
      assert.equal(e.addr, accounts[2])
      return true
    })
    assert.equal(await instance.countOf(2), 2, 'The cnt of group is error')
    assert.equal(await instance.has(2, accounts[2]), true)

    const balance0_2 = await utils.getBalance(accounts[0])
    assert.equal(utils.add(balance0_1, utils.cpc(1)).toString(), balance0_2, "balance should equal")
  })
})