import asyncio
import websockets
import json
import logging

logging.basicConfig(filename='transaction_log_async.log', level=logging.INFO, format='%(asctime)s - %(message)s')

async def handle_message(data):
    if 'params' in data:
        chain_id = data['params']['subscription']
        txns = data['params']['result']
        for txn in txns:
            logging.info(f"Chain ID: {chain_id}, Transaction Hash: {txn['hash']}, Block Number: {txn['blockNumber']}, From: {txn['from']}, To: {txn['to']}, Value: {txn['value']}")

async def subscribe(chain_id, ws):
    subscribe_message = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_subscribe",
        "params": ["newPendingTransactions", {}]
    })
    await ws.send(subscribe_message)
    await handle_message(json.loads(await ws.recv()))

async def main():
    try:
        arb_ws = await websockets.connect('wss://arb-mainnet.g.alchemy.com/v2/2Tr4ddoBTTbiUsUsoA_ZP5-qlfEHNlYr')
        logging.info("Arbitrum WebSocket connected")
        await subscribe('arbitrum', arb_ws)
    except Exception as e:
        logging.error(f"Arbitrum WebSocket error: {e}")
        arb_ws = None

    try:
        ovm_ws = await websockets.connect('wss://opt-mainnet.g.alchemy.com/v2/pXUHiwhSGSLfCQJ1tjM8LJqRGvYNxhBx')
        logging.info("Optimism WebSocket connected")
        await subscribe('optimism', ovm_ws)
    except Exception as e:
        logging.error(f"Optimism WebSocket error: {e}")
        ovm_ws = None

    while True:
        try:
            done, pending = await asyncio.wait(
                [arb_ws.recv() if arb_ws else asyncio.sleep(0),
                 ovm_ws.recv() if ovm_ws else asyncio.sleep(0)],
                return_when=asyncio.FIRST_COMPLETED
            )
            for task in done:
                data = json.loads(task.result())
                asyncio.create_task(handle_message(data))
        except Exception as e:
            logging.error(f"WebSocket error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
