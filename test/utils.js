const truffleAssert = require("truffle-assertions");

var BN = web3.utils.BN;

exports.cpc = (val) => {
  return web3.utils.toWei(String(val), "ether")
}

exports.getBalance = async (address) => {
  return await web3.eth.getBalance(address)
}

exports.add = (a, b) => {
  return new BN(a).add(new BN(b))
}
