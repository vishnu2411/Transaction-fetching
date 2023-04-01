import websocket
import json
import logging

logging.basicConfig(filename='transaction_log.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def on_message(ws, message):
    data = json.loads(message)
    if 'params' in data:
        txns = data['params']['result']['transactions']
        for txn in txns:
            logging.info(f"Transaction Hash: {txn['hash']}, Block Number: {txn['blockNumber']}, From: {txn['from']}, To: {txn['to']}, Value: {txn['value']}")

def on_error(ws, error):
    logging.error(error)

def on_close(ws):
    logging.info("WebSocket closed")

def on_open(ws):
    logging.info("WebSocket opened")

    # Subscribe to the Arbitrum Sequencer websocket feed
    subscribe_message = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_subscribe",
        "params": ["newPendingTransactions", {}]
    })
    ws.send(subscribe_message)

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "wss://arb-mainnet.g.alchemy.com/v2/2Tr4ddoBTTbiUsUsoA_ZP5-qlfEHNlYr",
        on_message = on_message,
        on_error = on_error,
        on_close = on_close,
        on_open = on_open
    )
    ws.run_forever()
