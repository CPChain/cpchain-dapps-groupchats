var GroupChat = artifacts.require("./GroupChat.sol");

module.exports = function(deployer) {
     deployer.deploy(GroupChat, {gas: 6000000 });
};
