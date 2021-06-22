const truffleAssert = require("truffle-assertions");

var BN = web3.utils.BN;

exports.cpc = (val) => {
  return web3.utils.toWei(String(val), "ether")
}
