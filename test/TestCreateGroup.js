const GroupChat = artifacts.require("GroupChat");
const truffleAssert = require("truffle-assertions");
const utils = require("./utils")

contract("GroupChat", (accounts) => {
  it("Create public group", async () => {
    const instance = await GroupChat.deployed();
    // check group name
    assert.equal(await instance.checkGroupName('test'), false, 'The name should not exists!')
    // Create a group
    let tx = await instance.createPublicGroup('test', 'xxxx', 0, '{}')
    assert.equal(await instance.checkGroupName('test'), true, 'The name should exists!')

    // two events
    truffleAssert.eventEmitted(tx, "CreateGroup", (e) => {
      assert.equal(e.id, 1, "id error")
      assert.equal(e.name, 'test')
      assert.equal(e.price, 0)
      assert.equal(e.extend, '{}')
      assert.equal(e.is_private, false)
      return true;
    })

    truffleAssert.eventEmitted(tx, 'JoinGroup', (e) => {
      assert.equal(e.id, 1)
      assert.equal(e.addr, accounts[0])
      return true
    })

    assert.equal(await instance.getGroupName(1), 'test', 'The name is error')
    assert.equal(await instance.countOf(1), 1, 'The cnt of group is error')
    assert.equal(await instance.has(1, accounts[0]), true, 'should has the owner')

    try {
      await instance.createPublicGroup('test', 'xxxx', 0, '{}')
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("This group already exists"))
    }

    tx = await instance.createPrivateGroup('test2', 0, '{}')
    truffleAssert.eventEmitted(tx, "CreateGroup", (e) => {
      assert.equal(e.is_private, true)
      return e.id == 2
    })

    assert.equal(await instance.checkGroupName('test2'), true, 'The name should exists!')
    assert.equal(await instance.getGroupName(2), 'test2', 'The name is error')
    assert.equal(await instance.countOf(2), 1, 'The cnt of group is error')
    assert.equal(await instance.has(2, accounts[0]), true, 'should has the owner')

  })
  it('Join a group', async ()=> {
    const instance = await GroupChat.deployed();
    try {
      await instance.join(1)
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("You have joinned this group"))
    }
    let tx = await instance.join(1, {from: accounts[1]})
    truffleAssert.eventEmitted(tx, 'JoinGroup', (e) => {
      assert.equal(e.id, 1)
      assert.equal(e.addr, accounts[1])
      return true
    })
    assert.equal(await instance.countOf(1), 2, 'The cnt of group is error')
  })
  it('quit a group', async () => {
    const instance = await GroupChat.deployed();
    try {
      await instance.quit(1)
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("Owner can't quit"))
    }
    let tx = await instance.quit(1, {from: accounts[1]})
    truffleAssert.eventEmitted(tx, 'QuitGroup', (e) => {
      assert.equal(e.id, 1)
      assert.equal(e.addr, accounts[1])
      return true
    })
    assert.equal(await instance.has(1, accounts[1]), false, 'should not have this address')
    assert.equal(await instance.countOf(1), 1, 'The cnt of group is error')
  })
  it("set group name", async () => {
    const instance = await GroupChat.deployed();
    assert.equal(await instance.getGroupName(1), 'test', 'group name is error')
    
    let tx = await instance.setGroupName(1, 'test1')
    truffleAssert.eventEmitted(tx, 'ModifyGroupName', (e) => {
      assert.equal(e.id, 1)
      assert.equal(e.name, 'test1')
      return true
    })

    assert.equal(await instance.getGroupName(1), 'test1', 'group name is error')

    await instance.createPublicGroup('test3', 'xxxx', 0, '{}', {from: accounts[1]})
    
    try {
      await instance.setGroupName(3, 'test3-1')
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("Only the owner can set the name"))
    }
  })
  it("set price", async () => {
    const instance = await GroupChat.deployed();
    let tx = await instance.setPrice(1, utils.cpc(1))
    truffleAssert.eventEmitted(tx, 'ModifyGroupPrice', (e) => {
      assert.equal(e.id, 1)
      assert.equal(e.price, utils.cpc(1))
      return true
    })
    assert.equal(await instance.getPrice(1), utils.cpc(1), "price of group1 is error")
    assert.equal(await instance.getPrice(2), utils.cpc(0), "price of group2 is error")

    assert.equal(await instance.getPrice(3), utils.cpc(0), "price of group3 is error")

    try {
      await instance.setPrice(3, utils.cpc(1))
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("Only the owner can set the price"))
    }
  })
  it("set encrypted AES key", async () =>{
    const instance = await GroupChat.deployed();
    let tx = await instance.setEncrypedAES(1, 'x')
    truffleAssert.eventEmitted(tx, 'UpgradeEncryptedAES', (e) => {
      assert.equal(e.id, 1)
      assert.equal(e.encryptedAES, 'x')
      assert.equal(e.blockNumber, tx.receipt.blockNumber)
      return true
    })
    assert.equal(await instance.getEncryptedAES(1), 'x', 'Encrypted AES key is error')
    try {
      await instance.setEncrypedAES(1, 'x', {from: accounts[1]})
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("Only the owner can upgrade the AES key"))
    }
  })
  it('set extend', async () => {
    const instance = await GroupChat.deployed()
    let tx = await instance.setExtend(1, '{"a":0}')
    truffleAssert.eventEmitted(tx, 'ModifyGroupExtend', (e) => {
      assert.equal(e.id, 1)
      assert.equal(e.extend, '{"a":0}')
      return true
    })
    assert.equal(await instance.getExtend(1), '{"a":0}')
    try {
      await instance.setExtend(3, '{"a":0}')
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("Only the owner can set the extend information"))
    }
  })
  it('change owner of a group', async ()=> {
    const instance = await GroupChat.deployed()
    try {
      await instance.changeOwnerOfGroup(1, accounts[1], {from: accounts[1]})
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("You're not the admin of the group"))
    }
    let tx = await instance.changeOwnerOfGroup(1, accounts[1])
    truffleAssert.eventEmitted(tx, 'ChangeGroupOwner', (e) => {
      assert.equal(e.id, 1)
      assert.equal(e.admin, accounts[1])
      return true
    })
    await instance.changeOwnerOfGroup(1, accounts[1], {from: accounts[1]})
  })
})
