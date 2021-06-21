pragma solidity ^0.4.24;

interface IGroupChat {
    // CreateGroup
    event CreateGroup(bool is_private, string name, string encryptedAES, uint256 price, string extend, uint id);

    // Modify name
    event ModifyGroupName(uint id, string name);

    // Modify Extend
    event ModifyGroupExtend(uint id, string extend);

    // Modify price
    event ModifyGroupPrice(uint id, uint256 price);

    // Join a group
    event JoinGroup(uint id, address addr);

    // Quit a group
    event QuitGroup(uint id, address addr);

    // Remove member
    event RemoveMember(uint id, address admin, address member);

    // Ban member
    event BanMember(uint id, address admin, address member);

    // Unban member
    event UnbanMember(uint id, address admin, address member);

    // Upgrade the AES key
    event UpgradeEncryptedAES(uint id, string encryptedAES, uint256 blockNumber);

    // Send Message
    // SentSeq is the sequence of the sender in this chat.
    // MsgSeq is the sequence of this chat
    event SendMessage(uint id, address sender, string message, uint sentSeq, uint msgSeq, uint blockNumber);

    // Change the owner of a group
    event ChangeGroupOwner(uint id, address admin);

    /**
     * Create public group. You can set the price which if someone wants to join the chat he should pay.
     * Extend information is in JSON formation.
     * Returns a id of the group
     * Emits a {CreateGroup} event
     */
    function createPublicGroup(string name, string encryptedAES, uint256 price, string extend) external returns (uint);

    /**
     * Create a private group
     * Returns a id of the group
     * Emits a {CreateGroup} event
     */
    function createPrivateGroup(string name, uint256 price, string extend) external returns (uint);

    /**
     * Get the group name
     */
    function getGroupName(uint id) external view returns(string);

    /**
     * Modify name of a group
     * Emits a {ModifyGroupName} event
     */
    function setGroupName(uint id, string name) external;

    /**
     * Count of group
     */
    function countOf(uint id) external view returns(uint);

    /**
     * Get the price
     */
    function getPrice(uint id) external view returns(uint256);

    /**
     * Set the price of a group-join
     * Emits a {ModifyGroupPrice} event.
     */
    function setPrice(uint id, uint256 price) external;

    /**
     * Get the extend information of a group.
     */
    function getExtend(uint id) external view returns (string);

    /**
     * Set the extend information of a group.
     * Emits a {ModifyGroupExtend} event.
     */
    function setExtend(uint id, string extend) external;

    /**
     * Get the encryptedAES of a group
     */
    function getEncryptedAES(uint id) external returns (string);

    /**
     * Set the encryptedAES of a group
     * Emits a {UpgradeEncryptedAES} event.
     */
    function setEncrypedAES(uint id, string encryptedAES) external;

    /**
     * Join a group
     * Emits a {JoinGroup} event
     */
    function join(uint id) external payable;

    /**
     * Quit a group
     * Emits a {QuitGroup} event
     */
    function quit(uint id) external;

    /**
     * The admin removes a member of a group
     * Emits a {RemoveMember} event
     */
    function remove(uint id, address member) external;

    /**
     * The admin bans a member of a group
     * Emits a {BanMember} event
     */
    function ban(uint id, address member) external;

    /**
     * The admin unbans a member of a group
     * Emits a {UnbanMember} event
     */
    function unban(uint id, address member) external;

    /**
     * Check a member whether is banned
     */
    function isBanned(uint id, address member) external view returns(bool);

    /**
     * Check a group if has this member
     */
    function has(uint id, address member) external view returns(bool);

    /**
     * Set the upper limit of group chat.
     */
    function setUpperLimit(uint limit) external;

    /**
     * Change the owner to other address.
     * Emits a {ChangeGroupOwner} event.
     */
    function changeOwnerOfGroup(uint id, address to) external;

    /**
     * Send Message to a chat
     * The formation of message need to reference: https://github.com/CPChain/cpchain-dapps-message#methods
     * Emits a {SendMessage} event
     */
    function sendMessage(uint id, string message) external;

    /**
     * Ban all members exclude the owner, make this chat be a notify-only chat.
     */
    function banAll(uint id) external;

    /**
     * Unban all members.
     */
    function unbanAll(uint id) external;

    /**
     * Change the owner of the contract. If the address is a contract, the contract should be IAdmin.
     */
    function changeOwner(address owner) external;
}
