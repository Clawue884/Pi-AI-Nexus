// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PiSmartContract {
    address public owner;
    uint256 public balance;

    event Deposit(address indexed sender, uint256 amount);
    event Withdrawal(address indexed receiver, uint256 amount);

    constructor() {
        owner = msg.sender;
    }

    function deposit() public payable {
        balance += msg.value;
        emit Deposit(msg.sender, msg.value);
    }

    function withdraw(uint256 amount) public {
        require(msg.sender == owner, "Hanya pemilik yang bisa menarik dana!");
        require(amount <= balance, "Saldo tidak cukup!");
        balance -= amount;
        payable(owner).transfer(amount);
        emit Withdrawal(owner, amount);
    }
}
