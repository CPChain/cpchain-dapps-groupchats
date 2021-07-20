const GroupChat = artifacts.require("GroupChat");
const truffleAssert = require("truffle-assertions");
const utils = require("./utils")

contract("GroupChat", (accounts) => {
  it("Set upper limit", async () => {
    const instance = await GroupChat.deployed();
    try {
      await instance.setUpperLimit(5, {from: accounts[1]})
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("You're not the owner of this contract"))
    }
    await instance.setUpperLimit(5)
    assert.equal(await instance.members_upper_limit(), 5)
  })
  it("change the owner of contract", async ()=> {
    const instance = await GroupChat.deployed();
    try {
      await instance.changeOwner(accounts[1], {from: accounts[1]})
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("You're not the owner of this contract"))
    }
    await instance.changeOwner(accounts[1])
  })
  // it("Add 6 members to a group", async () => {
  //   const instance = await GroupChat.deployed();
  //   await instance.createPublicGroup('test', 'xxxx', 0, '{}')

  //   for(let i = 0; i < 5; i++) {
  //     await instance.join(1, {from: accounts[1+i]})
  //   }
  //   assert.equal(await instance.countOf(1), 6)
  //   // add another
  //   try {
  //     await instance.join(1, {from: accounts[6]})
  //     assert.fail()
  //   } catch(error) {
  //     assert.ok(error.toString().includes("The group is full"))
  //   }
  // })
  it("enable and disable", async ()=> {
    const instance = await GroupChat.deployed();
    await instance.disableContract({from: accounts[1]})
    assert.equal(await instance.enabled(), false)
    await instance.enableContract({from: accounts[1]})
    assert.equal(await instance.enabled(), true)
  })
})
