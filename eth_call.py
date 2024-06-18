from web3 import Web3
from web3.middleware import geth_poa_middleware
import json

# Constants for the RPC URL and contract details
CONTRACT_ADDRESS = Web3.to_checksum_address('0x5A7d6b2F92C77FAD6CCaBd7EE0624E64907Eaf3E')

# Create a Web3 instance connected to the specified RPC URL
w3 = Web3(Web3.HTTPProvider('https://mainnet.era.zksync.io'))

# Check for connection to the Ethereum network
if not w3.is_connected():
    raise ConnectionError("Failed to connect to HTTPProvider")

# Load the contract ABI from a file
with open('abi.json') as abi_file:
    contract_abi = json.load(abi_file)

# Create a contract object
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

TO_ADDRESS = 'TO_ADDRESS'
private_key = 'YOUR_PRIVATE_KEY'
token_amount = w3.to_wei(1, 'ether')
nonce = w3.eth.get_transaction_count(w3.eth.account.from_key(private_key).address)
tx = contract.functions.transfer(TO_ADDRESS, token_amount).build_transaction({
    'chainId': 324,
    'gas': 2000000,  # Adjust the gas limit as needed
    'gasPrice': w3.eth.gas_price,  # Adjust the gas price as needed or use w3.eth.generate_gas_price()
    'nonce': nonce,
})
tx = w3.eth.account.sign_transaction(tx, private_key)
tx_hash(w3.eth.send_raw_transaction(tx.rawTransaction))

# Attempt to send the transaction
try:
    print(f"symbol = {contract.functions.symbol().call()}");
    print(f"name = {contract.functions.name().call()}");
    print(f"decimals = {contract.functions.decimals().call()}");
except Exception as e:
    print(f"Error sending transaction: {e}")
