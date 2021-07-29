pragma solidity ^0.4.24;

interface IApplicationManager {
    // add application
    event AddApplication(address addr);
    // remove application
    event RemoveApplication(address addr);

    /**
     * Add application to group chat
     * Emits {AddApplication} event
     */
    function addApplication(address addr) external;

    /**
     * Remove application from group chat
     * Emits {RemoveApplication} event
     */
    function removeApplication(address addr) external;
}
