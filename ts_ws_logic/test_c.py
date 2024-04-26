clients = {}  # {client_id: websocket}
clients['1'] = "hi"
clients['2'] = "mi"
client_id = 2

print("len: ", len(clients))

max_client_id = len(clients)
print(max_client_id)

# if client_id is None or ((client_id <= 0) and (client_id > max_client_id)):
if client_id is None or (client_id <= 0) or (client_id > max_client_id):
    print("don't connect")
else:
    print("connect")