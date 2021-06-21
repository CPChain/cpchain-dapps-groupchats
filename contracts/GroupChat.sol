pragma solidity ^0.4.24;
pragma experimental ABIEncoderV2;

import "./lib/set.sol";

import "./interfaces/IGroupChat.sol";

contract Staking is IGroupChat {
    using Set for Set.Data;

    address owner; // owner has permissions to modify parameters
    bool public enabled = true; // if upgrade contract, then the old contract should be disabled

    uint group_seq = 0; // The sequence of all groups

    uint members_upper_limit = 100; // The member's upper_limit of a group.

    struct Member {
        uint groupID;
        address addr;
        bool banned; // A member can't send message when be banned
        uint seq; // sequence of this group
        bool existed;
    }

    struct Group {
        uint id;
        address owner;
        bool is_private;
        uint seq; // sequence of this group
        uint cnt; // cnt of the group
        string name;
        uint256 price;
        string encryptedAES;
        string extend;
        bool banAll; // If banAll, notify only.
        bool existed;
    }

    mapping(uint => Group) internal groups;

    mapping(string => bool) private group_names; // all groups

    mapping(uint => mapping(address => Member)) internal members;

    modifier onlyOwner() {
        require(msg.sender == owner, "You're not the owner of this contract");
        _;
    }

    modifier onlyEnabled() {
        require(enabled);
        _;
    }

    constructor() public {
        owner = msg.sender;
    }

    // owner can enable and disable rnode contract
    function enableContract() public onlyOwner {
        enabled = true;
    }

    function disableContract() public onlyOwner {
        enabled = false;
    }

    function createGroup(bool is_private, string name, string encryptedAES, uint256 price, string extend) internal returns (uint) {
        require(!group_names[name], "This group already exists");
        group_seq += 1;
        groups[group_seq] = Group({
            id: group_seq,
            owner: msg.sender,
            is_private: is_private,
            name: name,
            price: price,
            encryptedAES: encryptedAES,
            extend: extend,
            seq: 0,
            cnt: 0,
            banAll: false,
            existed: true
        });
        group_names[name] = true;
        // Add the first member to the group
        groups[group_seq].cnt += 1;
        members[group_seq][msg.sender] = Member({
            groupID: group_seq,
            addr: msg.sender,
            banned: false,
            seq: 0,
            existed: true
        });
        emit CreateGroup(is_private, name, encryptedAES, price, extend, group_seq);
        emit JoinGroup(group_seq, msg.sender);
        return group_seq;
    }

    /**
     * Create public group. You can set the price which if someone wants to join the chat he should pay.
     * Extend information is in JSON formation.
     * Returns a id of the group
     * Emits a {CreateGroup} event
     */
    function createPublicGroup(string name, string encryptedAES, uint256 price, string extend) external onlyEnabled returns (uint) {
        return createGroup(false, name, encryptedAES, price, extend);
    }

    /**
     * Create a private group
     * Returns a id of the group
     * Emits a {CreateGroup} event
     */
    function createPrivateGroup(string name, uint256 price, string extend) external onlyEnabled returns (uint) {
        return createGroup(true, name, "", price, extend);
    }

    /**
     * Get the group name
     */
    function getGroupName(uint id) external view returns(string) {
        return groups[id].name;
    }

    /**
     * Modify name of a group
     * Emits a {ModifyGroupName} event
     */
    function setGroupName(uint id, string name) external onlyEnabled {
        require(!group_names[name], "This group already exists");
        require(groups[id].owner == msg.sender, "Only the owner can set the name");
        group_names[groups[id].name] = false;
        groups[id].name = name;
        group_names[name] = true;
        emit ModifyGroupName(id, name);
    }

    function getGroup(uint id) external view returns (Group) {
        return groups[id];
    }

    /**
     * Count of group
     */
    function countOf(uint id) external view returns(uint) {
        return groups[id].cnt;
    }

    /**
     * Get the price
     */
    function getPrice(uint id) external view returns(uint256) {
        return groups[id].price;
    }

    /**
     * Set the price of a group-join
     * Emits a {ModifyGroupPrice} event.
     */
    function setPrice(uint id, uint256 price) external onlyEnabled {
        require(groups[id].existed, "The group not exists");
        require(groups[id].owner == msg.sender, "Only the owner can set the price");
        groups[id].price = price;
        emit ModifyGroupPrice(id, price);
    }

    /**
     * Get the extend information of a group.
     */
    function getExtend(uint id) external view returns (string) {
         return groups[id].extend;
    }

    /**
     * Set the extend information of a group.
     * Emits a {ModifyGroupExtend} event.
     */
    function setExtend(uint id, string extend) external onlyEnabled {
        require(groups[id].existed, "The group not exists");
        require(groups[id].owner == msg.sender, "Only the owner can set the extend information");
        groups[id].extend = extend;
        emit ModifyGroupExtend(id, extend);
    }

    /**
     * Get the encryptedAES of a group
     */
    function getEncryptedAES(uint id) external returns (string) {
        return groups[id].encryptedAES;
    }

    /**
     * Set the encryptedAES of a group
     * Emits a {UpgradeEncryptedAES} event.
     */
    function setEncrypedAES(uint id, string encryptedAES) external onlyEnabled {
        require(groups[id].existed, "The group not exists");
        require(groups[id].owner == msg.sender, "Only the owner can upgrade the AES key");
        groups[id].encryptedAES = encryptedAES;
        emit UpgradeEncryptedAES(id, encryptedAES, block.number);
    }

    /**
     * Join a group
     * Emits a {JoinGroup} event
     */
    function join(uint id) external payable onlyEnabled {
        require(groups[id].existed, "The group not exists");
        require(groups[id].cnt <= members_upper_limit, "The group is full");
        require(!members[id][msg.sender].existed, "You have joinned this group");
        require(msg.value == groups[id].price, "The value is not equal to the price");
        groups[id].owner.transfer(msg.value);
        groups[id].cnt += 1;
        members[id][msg.sender] = Member({
            groupID: id,
            addr: msg.sender,
            banned: false,
            seq: 0,
            existed: true
        });
        emit JoinGroup(id, msg.sender);
    }

    /**
     * Quit a group
     * Emits a {QuitGroup} event
     */
    function quit(uint id) external onlyEnabled {
        require(groups[id].existed, "The group not exists");
        require(groups[id].owner != msg.sender, "Owner can't quit");
        require(members[id][msg.sender].existed, "You haven't joinned this group");
        groups[id].cnt -= 1;
        members[id][msg.sender].existed = false;
        emit QuitGroup(id, msg.sender);
    }

    /**
     * The admin removes a member of a group
     * Emits a {RemoveMember} event
     */
    function remove(uint id, address member) external onlyEnabled {
        require(groups[id].existed, "The group not exists");
        require(groups[id].owner == msg.sender, "You're not the admin of the group");
        require(groups[id].owner != member, "You can remove the owner");
        require(members[id][member].existed, "The member not exists");
        groups[id].cnt -= 1;
        members[id][member].existed = false;
        emit RemoveMember(id, groups[id].owner, member);
    }

    /**
     * The admin bans a member of a group
     * Emits a {BanMember} event
     */
    function ban(uint id, address member) external onlyEnabled {
        require(groups[id].existed, "The group not exists");
        require(groups[id].owner == msg.sender, "You're not the admin of the group");
        require(groups[id].owner != member, "You can ban the owner");
        require(members[id][member].existed, "The member not exists");
        require(!members[id][member].banned, "The member is banned now");
        members[id][member].banned = true;
        emit BanMember(id, groups[id].owner, member);
    }

    /**
     * The admin unbans a member of a group
     * Emits a {UnbanMember} event
     */
    function unban(uint id, address member) external onlyEnabled {
        require(groups[id].existed, "The group not exists");
        require(groups[id].owner == msg.sender, "You're not the admin of the group");
        require(members[id][member].existed, "The member not exists");
        require(members[id][member].banned, "The member not banned now");
        members[id][member].banned = false;
        emit UnbanMember(id, groups[id].owner, member);
    }

    /**
     * Check a member whether is banned
     */
    function isBanned(uint id, address member) external view returns(bool) {
        return members[id][member].banned;
    }

    /**
     * Check a group if has this member
     */
    function has(uint id, address member) external view returns(bool) {
        return members[id][member].existed;
    }

    /**
     * Set the upper limit of group chat.
     */
    function setUpperLimit(uint limit) external onlyEnabled onlyOwner {
        members_upper_limit = limit;
    }

    /**
     * Change the owner to other address.
     * Emits a {ChangeGroupOwner} event.
     */
    function changeOwnerOfGroup(uint id, address to) external onlyEnabled {
        require(groups[id].existed, "The group not exists");
        require(groups[id].owner == msg.sender, "You're not the admin of the group");
        groups[id].owner = to;
        emit ChangeGroupOwner(id, to);
    }

    /**
     * Send Message to a chat
     * The formation of message need to reference: https://github.com/CPChain/cpchain-dapps-message#methods
     * Emits a {SendMessage} event
     */
    function sendMessage(uint id, string message) external onlyEnabled {
        require(groups[id].existed, "The group not exists");
        require(members[id][msg.sender].existed, "You're not exists in this group");
        require(!members[id][msg.sender].banned, "You're banned now");
        if (groups[id].banAll) {
            require(msg.sender == groups[id].owner, "The group only can allow the owner send message");
        }
        // recvSeq ++
        groups[id].seq += 1;
        members[id][msg.sender].seq += 1;
        emit SendMessage(id, msg.sender, message, members[id][msg.sender].seq, groups[id].seq, block.number);   
    }

    /**
     * Ban all members, make this chat be a notify-only chat.
     */
    function banAll(uint id) external {
        require(groups[id].existed, "The group not exists");
        require(groups[id].owner == msg.sender, "You're not the admin of the group");
        groups[id].banAll = true;
    }

    /**
     * Unban all members.
     */
    function unbanAll(uint id) external {
        require(groups[id].existed, "The group not exists");
        require(groups[id].owner == msg.sender, "You're not the admin of the group");
        groups[id].banAll = false;
    }

    /**
     * Change the owner of the contract. If the address is a contract, the contract should be IAdmin.
     */
    function changeOwner(address to) external onlyEnabled onlyOwner {
        owner = to;
    }
}
