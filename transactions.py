from web3 import Web3
import time

# Connect to local geth node
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8001'))

if w3.is_connected():
    print("Connected to Ethereum node")

# Set up account information
account_from = {
    'private_key': '0x86c39ccc304adb058903a9bff981982a1790ed44c77307a78546015d546d9cbd',
    'address': '0xb59616524d51f5F557f94f6cF7Ac258599DF3A97'
}

nonce = w3.eth.get_transaction_count(account_from['address'])
gas_limit = 21000
max_fee_per_gas = w3.to_wei('100', 'gwei')  # Max fee per gas
max_priority_fee_per_gas = w3.to_wei('2', 'gwei')  # Max priority fee per gas
chain_id = 32382

nbr_transactions = 10

# Contract address
contract_address = '0x4242424242424242424242424242424242424242'

# Create and collect transactions
for i in range(nbr_transactions):
    # Alternate between the original recipient address and the contract address
    recipient = '0x8D512169343cc6e108a8bB6ec5bc116C416eFc8E' if i % 2 == 0 else contract_address

    # Set up transaction details
    tx = {
        'type': 2,  # Specify EIP-1559 transaction
        'nonce': nonce + i,
        'to': recipient,
        'value': w3.to_wei(0.01, 'ether'),
        'gas': gas_limit,
        'maxFeePerGas': max_fee_per_gas,
        'maxPriorityFeePerGas': max_priority_fee_per_gas,
        'chainId': chain_id,
        'data': '0x' if recipient == contract_address else ''  # Data field is empty unless sending to the contract
    }
    
    print(f'Transaction {i} details: {tx}')

    # Sign the transaction
    signed_tx = w3.eth.account.sign_transaction(tx, account_from['private_key'])
    
    # Send the transaction
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    print(f'Transaction {i} sent with hash: {tx_hash.hex()}')

    # Increment the nonce for the next transaction
    tx['nonce'] += 1

    # Sleep for a very short time to avoid hitting rate limits
    time.sleep(0.01)