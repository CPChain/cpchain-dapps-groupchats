pragma solidity ^0.4.24;

contract Greeter {
    string name;
    constructor(string initial) public {
        name = initial;
    }

    function greet() view returns (string) {
        return name;
    }
}