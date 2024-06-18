from eth_account import Account
from eth_account.messages import encode_defunct, encode_typed_data
import rlp


# eth_account requires it for some reason
def normalize_vrs(vrs: tuple) -> tuple:
    vrs_l = list()
    for elem in vrs:
        vrs_l.append(elem.lstrip(b'\x00'))
    return tuple(vrs_l)


def get_selector_from_data(data: str) -> bytes:
    raw_data = bytes.fromhex(data[2:])
    return raw_data[:4]


def recover_message(msg, vrs: tuple) -> bytes:
    if isinstance(msg, dict):  # EIP-712
        smsg = encode_typed_data(full_message=msg)
    else:  # EIP-191
        smsg = encode_defunct(primitive=msg)
    addr = Account.recover_message(smsg, normalize_vrs(vrs))
    return bytes.fromhex(addr[2:])

def reencode_raw_transaction(tx_params, vrs: tuple) -> bytes:
    raw_tx = Account.create().sign_transaction(tx_params).rawTransaction
    assert raw_tx[0] in [0x01, 0x02]
    prefix = raw_tx[:1]
    decoded = rlp.decode(raw_tx[len(prefix):])
    reencoded = rlp.encode(decoded[:-3] + list(normalize_vrs(vrs)))
    return prefix + reencoded

def recover_transaction(tx_params, vrs: tuple) -> bytes:
    addr = Account.recover_transaction(reencode_raw_transaction(tx_params,vrs))
    return bytes.fromhex(addr[2:])
