#!/bin/bash

# Configuration
NODE_URL="http://localhost:8001"
SENDER_ADDRESS="0xb59616524d51f5F557f94f6cF7Ac258599DF3A97"
PRIVATE_KEY="0x86c39ccc304adb058903a9bff981982a1790ed44c77307a78546015d546d9cbd"
RECEIVER_ADDRESS="0x8D512169343cc6e108a8bB6ec5bc116C416eFc8E"
NUM_TRANSACTIONS=100
GAS_PRICE="10"  # in gwei
GAS_LIMIT=21000
VALUE="0.01ether"

send_transaction() {
    TX_HASH=$(cast send -r $NODE_URL --private-key $PRIVATE_KEY $RECEIVER_ADDRESS --value $VALUE)
    echo "Transaction sent: $TX_HASH"
}

NONCE=$(cast nonce -r $NODE_URL $SENDER_ADDRESS)

echo "Begin sending transactions"
for((i=0; i<$NUM_TRANSACTIONS; i++)) do
    send_transaction
    sleep 0.1
done
echo "All transactions sent"