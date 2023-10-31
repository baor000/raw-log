import websocket
import threading
# import pymongo
import json
import os
import psycopg2

def connect_to_csgo_empire_websocket():

    # Read the connection string from the environment variable
    # Read the connection string, database name, and collection name from environment variables
    postgres_uri = os.environ.get('POSTGRES_URI')
    # connection_string = os.environ.get('MONGODB_CONNECTION_STRING')
    # database_name = os.environ.get('MONGODB_DATABASE_NAME') or 'logs'
    # collection_name = os.environ.get('MONGODB_COLLECTION_NAME') or 'raw-log'

    # Connect to the MongoDB cluster
    # client = pymongo.MongoClient(connection_string)

    # Access the database and collection
    # db = client[database_name]
    # collection = db[collection_name]

    conn = psycopg2.connect(postgres_uri,sslmode='require')
    cur = conn.cursor()
    
    def handle_data(data):
        sql = ""
        # if data['type'] == "match_created":
        #     data = data['data']
        #     list_key = ['id','game','status','format']
        #     sql = f"""INSERT INTO match_created({','.join(list_key)}) VALUES({str(data[i]) for i in list_key}) RETURNING id;"""
        # if data['type'] == "market_created":
        #     data = data['data']
        #     list_key = ['id','match_id']
        #     sql = f"""INSERT INTO market_created({','.join(list_key)}) VALUES({data[i] for i in list_key}) RETURNING id;"""
        # this handle match detail infomation
        # if data['type'] == "match_updated":
        #     data = data['data']
        #     list_key = ['id','match_id']
        #     sql = f"""INSERT INTO match_created({','.join(list_key)}) VALUES({data[i] for i in list_key}) RETURNING id;"""
        # this handle match status
        # if data['type'] == "market_updated":
        #     data = data['data']
        #     list_key = ['id','match_id']
        #     sql = f"""INSERT INTO match_created({','.join(list_key)}) VALUES({data[i] for i in list_key}) RETURNING id;"""
        if data['type'] == "selection_updated":
            # this will be a list
            data = data['data']
            # if 'odds' not in data[0]:
            #     return
            list_key = ['id','match_id','market_id','odds']

            grouped_data = {}

           # Assuming your list of dictionaries is named `data`
            grouped_data = {}

            for d in data:
                if 'odds' not in d:
                    continue
                match_id = d['match_id']
                market_id = d['market_id']
                if (match_id, market_id) not in grouped_data:
                    grouped_data[(match_id, market_id)] = []
                grouped_data[(match_id, market_id)].append(d)
            query = []
            # print(grouped_data)
            for key, value in grouped_data.items():
                if len(value) != 2 or all([i['odds'] > 2 for i in value]):
                    continue
                else:
                    for ind,val in enumerate(value):
                        if ind % 2:
                            values = '(' + ','.join([str(val[i]) for i in list_key]) + ',1)'
                        else:
                            values = '(' + ','.join([str(val[i]) for i in list_key]) + ',0)'
                        query.append(values)

            r = ','.join(query)
            if r:
                sql = f"""INSERT INTO selection_updated({','.join(list_key)+',site'}) VALUES{r} RETURNING 1;"""

        if sql:
            cur.execute(sql)
            result = cur.fetchone()[0]
            conn.commit()
            return result
        return True

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
            handle_data(data_dict)
            # print(handle_data(data_dict))


    def on_close(ws, close_status_code, close_msg):
        cur.close()
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
