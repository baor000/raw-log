import websocket
import threading
import pymongo
import json
import os

def connect_to_csgo_empire_websocket():

    # Read the connection string from the environment variable
    # Read the connection string, database name, and collection name from environment variables
    connection_string = os.environ.get('MONGODB_CONNECTION_STRING')
    database_name = os.environ.get('MONGODB_DATABASE_NAME')
    collection_name = os.environ.get('MONGODB_COLLECTION_NAME')

    # Connect to the MongoDB cluster
    client = pymongo.MongoClient(connection_string)

    # Access the database and collection
    db = client[database_name]
    collection = db[collection_name]
    def on_open(ws):
        print('WebSocket connection opened')
        ws.send('40/matchbetting,')

        def send_message():
            ws.send('2')
            threading.Timer(40, send_message).start()

        send_message()

    def on_message(ws, message):
        # print('WebSocket message received:', message)
        parts = message.split(',')
        if len(parts) > 1:
            data = parts[1:]
            # print('Processed data:', data)

            list_data = json.loads(','.join(data))

            # Create a dictionary containing the processed data with specified field names
            data_dict = {
                "type": list_data[0],
                "data": list_data[1]
            }

            # Insert the data into the collection
            result = collection.insert_one(data_dict)
            print(result)


    def on_close(ws, close_status_code, close_msg):
        print('WebSocket connection closed with status code:', close_status_code, 'and message:', close_msg)

    def on_error(ws, error):
        print('WebSocket error occurred:', error)

    headers = {
        'Connection': 'Upgrade',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Upgrade': 'websocket',
        'Origin': 'https://csgoempire.com',
        'Sec-WebSocket-Version': '13',
        'Sec-WebSocket-Key': 'EN6EKWfQKi3nCa0GdS6mfA==',
        'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits'
    }

    ws = websocket.WebSocketApp('wss://roulette.csgoempire.com/s/?EIO=3&transport=websocket',
                                header=headers,
                                on_open=on_open,
                                on_message=on_message,
                                on_close=on_close,
                                on_error=on_error)

    ws.run_forever()

def main():
    connect_to_csgo_empire_websocket()

if __name__ == "__main__":
    main()
