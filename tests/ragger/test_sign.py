from pathlib import Path
from web3 import Web3
import json

from ragger.error import ExceptionRAPDU
from ragger.backend import BackendInterface
from ragger.firmware import Firmware
from ragger.navigator import Navigator, NavInsID
from ragger.navigator.navigation_scenario import NavigateWithScenario

from client.client import EthAppClient, StatusWord
import client.response_parser as ResponseParser
from client.settings import SettingID, settings_toggle
from client.utils import recover_transaction


# Values used across all tests
ADDR = bytes.fromhex("0011223344556677889900112233445566778899")
ADDR2 = bytes.fromhex("5a321744667052affa8386ed49e00ef223cbffc3")
ADDR3 = bytes.fromhex("dac17f958d2ee523a2206206994597c13d831ec7")
ADDR4 = bytes.fromhex("b2bb2b958afa2e96dab3f3ce7162b87daea39017")
BIP32_PATH = "m/44'/60'/0'/0/0"
BIP32_PATH2 = "m/44'/60'/1'/0/0"
NONCE = 21
NONCE2 = 68
GAS_PRICE = 13
GAS_PRICE2 = 5
GAS_LIMIT = 21000
AMOUNT = 1.22
AMOUNT2 = 0.31415

def test_sign_simple(firmware: Firmware,
                     backend: BackendInterface,
                     navigator: Navigator,
                     scenario_navigator: NavigateWithScenario,
                     test_name: str,
                     default_screenshot_path: Path):
   
    # https://www.quicknode.com/guides/ethereum-development/transactions/how-to-send-erc20-tokens-using-web3py
    # https://ethereum.org/en/developers/docs/standards/tokens/erc-20/
    # https://explorer.zksync.io/address/0x5A7d6b2F92C77FAD6CCaBd7EE0624E64907Eaf3E#contract

    # ledger supported stuff
    # https://support.ledger.com/hc/en-us/articles/10479755500573-Supported-Coins-and-Tokens-in-Ledger-Live?docs=true

    # https://github.com/LedgerHQ/ledger-live/tree/develop/libs/ledgerjs/packages/cryptoassets

    # Constants for the RPC URL and contract details
    CONTRACT_ADDRESS = Web3.to_checksum_address('0x5A7d6b2F92C77FAD6CCaBd7EE0624E64907Eaf3E') 

    # Create a Web3 instance connected to the specified RPC URL
    CHAIN_ID = 324
    w3 = Web3(Web3.HTTPProvider('https://mainnet.era.zksync.io'))

    # Check for connection to the Ethereum network
    if not w3.is_connected():
        raise ConnectionError("Failed to connect to HTTPProvider")

    # Load the contract ABI from a file
    with open('abis/erc20.json') as abi_file:
        contract_abi = json.load(abi_file)

    # Create a contract object
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)
  
    path = "m/44'/60'/1'/0/0"
    app_client = EthAppClient(backend)
    with app_client.get_public_addr(bip32_path=path, display=False):
        pass
    _, FROM_ADDR, _ = ResponseParser.pk_addr(app_client.response().data)
    nonce = w3.eth.get_transaction_count(FROM_ADDR)

    symbol = contract.functions.symbol().call()
    decimals = contract.functions.decimals().call()
    response = app_client.provide_token_metadata(symbol,
        bytes.fromhex(CONTRACT_ADDRESS[2:]), decimals, CHAIN_ID)
    assert response.status == StatusWord.OK

    TO_ADDR = ADDR2 
    token_amount = w3.to_wei(1, 'ether')
    tx_params = contract.functions.transfer(TO_ADDR, token_amount).build_transaction({
        'chainId': CHAIN_ID,
        'gas': 2000000,  # Adjust the gas limit as needed
        'gasPrice': w3.eth.gas_price,  # Adjust the gas price as needed or use w3.eth.generate_gas_price()
        'nonce': nonce,
    })

    with app_client.sign(path, tx_params):
        end_text = "Accept"
        scenario_navigator.review_approve(default_screenshot_path, test_name, end_text, True)

    # verify signature
    vrs = ResponseParser.signature(app_client.response().data)
    # TODO: this doesn't work yet, because we use legacy transaction format.
    # It would be preferrable to use one of the new transaction formats instead,
    # but if that's not feasible, we will just revert the changes I did to
    # the implementation of recover_transaction
    # addr = recover_transaction(tx_params, vrs)
    #assert addr == FROM_ADDR

    # TODO: send the transaction
    # also we will need to combine the received signature with the generated
    # transaction before sending it out (that's what Ivan is working on)
    # tx_hash(w3.eth.send_raw_transaction(tx.rawTransaction))
