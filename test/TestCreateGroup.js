const GroupChat = artifacts.require("GroupChat");
const truffleAssert = require("truffle-assertions");

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

    tx = await instance.createPrivateGroup('test1', 1, '{}')
    let id = 0;
    truffleAssert.eventEmitted(tx, "CreateGroup", (e) => {
      id = e.id
      assert.equal(e.is_private, true)
      return e.id == 2
    })

    assert.equal(await instance.checkGroupName('test1'), true, 'The name should exists!')
    assert.equal(await instance.getGroupName(2), 'test1', 'The name is error')
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
  })
})
