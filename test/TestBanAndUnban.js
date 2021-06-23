const GroupChat = artifacts.require("GroupChat");
const truffleAssert = require("truffle-assertions");
const utils = require("./utils")

contract("GroupChat", (accounts) => {
  it("Create group", async () => {
    const instance = await GroupChat.deployed();
    await instance.createPublicGroup('test', 'xxxx', 0, '{}')
  })
  it("Ban user in a unexists group", async() => {
    const instance = await GroupChat.deployed();
    try {
      await instance.ban(2, accounts[0])
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("The group not exists"))
    }
  })
  it("Ban owner", async() => {
    const instance = await GroupChat.deployed();
    try {
      await instance.ban(1, accounts[0])
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("You can't ban the owner"))
    }
  })
  it("Ban an unexisted user", async() => {
    const instance = await GroupChat.deployed();
    try {
      await instance.ban(1, accounts[1])
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("The member not exists"))
    }
  })
  it("Ban an user with wrong admin", async() => {
    const instance = await GroupChat.deployed();
    try {
      await instance.ban(1, accounts[1], {from: accounts[2]})
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("You're not the admin of the group"))
    }
  })
  it("Ban a user", async ()=> {
    const instance = await GroupChat.deployed();
    await instance.join(1, {from: accounts[1]})
    let tx = await instance.ban(1, accounts[1])
    truffleAssert.eventEmitted(tx, 'BanMember', (e) => {
      assert.equal(e.id, 1)
      assert.equal(e.member, accounts[1])
      assert.equal(e.admin, accounts[0])
      return true
    })
    assert.equal(await instance.isBanned(1, accounts[1]), true, "This member should have been banned")

    await instance.join(1, {from: accounts[2]})
    assert.equal(await instance.isBanned(1, accounts[2]), false, "This member shouldn't have been banned")
  })
  it("Send message after been bannd", async ()=> {
    const instance = await GroupChat.deployed();
    // account[1] can't send message
    try {
      await instance.sendMessage(1, "message", {from: accounts[1]})
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("You're banned now"))
    }
    // account[2] can send message
    await instance.sendMessage(1, "message", {from: accounts[2]})
  })
  it("Unban without admin", async () => {
    const instance = await GroupChat.deployed();
    try {
      await instance.unban(1, accounts[1], {from: accounts[3]})
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("You're not the admin of the group"))
    }
  })
  it("Unban an unexists member", async () => {
    const instance = await GroupChat.deployed();
    try {
      await instance.unban(1, accounts[3])
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("The member not exists"))
    }
  })
  it("Unban with unexists group", async () => {
    const instance = await GroupChat.deployed();
    try {
      await instance.unban(10, accounts[3])
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("The group not exists"))
    }
  })
  it("Unban normal member", async () => {
    const instance = await GroupChat.deployed();
    try {
      await instance.unban(1, accounts[2])
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("The member not banned now"))
    }
  })
  it("Unban accounts[1]", async ()=> {
    const instance = await GroupChat.deployed();
    let tx = await instance.unban(1, accounts[1])
    truffleAssert.eventEmitted(tx, 'UnbanMember', (e) => {
      assert.equal(e.id, 1)
      assert.equal(e.member, accounts[1])
      assert.equal(e.admin, accounts[0])
      return true
    })
    assert.equal(await instance.isBanned(1, accounts[1]), false, "This member shouldn't have been banned")
    assert.equal(await instance.isBanned(1, accounts[2]), false, "This member shouldn't have been banned")
  })
  it('Ban All: unexisted group', async () => {
    const instance = await GroupChat.deployed();
    try {
      await instance.banAll(10)
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("The group not exists"))
    }
  })
  it('Ban All: wrong admin', async () => {
    const instance = await GroupChat.deployed();
    try {
      await instance.banAll(1, {from: accounts[1]})
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("You're not the admin of the group"))
    }
  })
  it("Ban all", async ()=> {
    const instance = await GroupChat.deployed();
    let tx = await instance.banAll(1)
    truffleAssert.eventEmitted(tx, 'BanAll', (e) => {
      assert.equal(e.id, 1)
      assert.equal(e.admin, accounts[0])
      return true
    })
    assert.equal(await instance.isBanned(1, accounts[1]), true, "This member should have been banned")
    assert.equal(await instance.isBanned(1, accounts[2]), true, "This member should have been banned")
    assert.equal(await instance.isBanAll(1), true)
  })
  it("Only admin can send message", async ()=> {
    const instance = await GroupChat.deployed();
    // accounts[2] can't send message
    try {
      await instance.sendMessage(1, "message", {from: accounts[2]})
    } catch(error) {
      assert.ok(error.toString().includes("The group only can allow the owner send message"))
    }
    await instance.sendMessage(1, "message", {from: accounts[0]})
  })
  it('Unban All: unexisted group', async () => {
    const instance = await GroupChat.deployed();
    try {
      await instance.unbanAll(10)
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("The group not exists"))
    }
  })
  it('Unban All: wrong admin', async () => {
    const instance = await GroupChat.deployed();
    try {
      await instance.unbanAll(1, {from: accounts[1]})
      assert.fail()
    } catch(error) {
      assert.ok(error.toString().includes("You're not the admin of the group"))
    }
  })
  it("Unban all", async ()=> {
    const instance = await GroupChat.deployed();
    let tx = await instance.unbanAll(1)
    truffleAssert.eventEmitted(tx, 'UnBanAll', (e) => {
      assert.equal(e.id, 1)
      assert.equal(e.admin, accounts[0])
      return true
    })
    assert.equal(await instance.isBanned(1, accounts[1]), false, "This member shouldn't have been banned")
    assert.equal(await instance.isBanned(1, accounts[2]), false, "This member shouldn't have been banned")

    // accounts[2] can send message now
    await instance.sendMessage(1, "message", {from: accounts[2]})
    assert.equal(await instance.isBanAll(1), false)
  })
})