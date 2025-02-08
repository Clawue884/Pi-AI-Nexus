require("dotenv").config();
const Web3 = require("web3");

const PI_RPC_URL = "https://api.pi-network.io";
const web3 = new Web3(new Web3.providers.HttpProvider(PI_RPC_URL));

const CONTRACT_ADDRESS = "0x1234567890abcdef1234567890abcdef12345678";
const PRIVATE_KEY = process.env.PRIVATE_KEY;
const account = web3.eth.accounts.privateKeyToAccount(PRIVATE_KEY);
web3.eth.accounts.wallet.add(account);

module.exports = { web3, CONTRACT_ADDRESS, account };
