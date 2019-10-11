import sys
import random
import string
from datetime import datetime
from rethinkdb import RethinkDB

r = RethinkDB()
connection = r.connect('localhost', 28015, db='chat')

conversations = r.table('conversations')
messages = r.table('messages')
users = r.table('users')
tables = [conversations, messages, users]

now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

if len(sys.argv) < 2:
    print("ACTIONS: -help | -newc | -newm | -newu | -listc | -listm | -listu | -removem | -clean")
elif sys.argv[1] == '-help':
    print(
"""* CLI for adding in, listing from and cleaning conversations and messages tables ------------------------------------------*
| -newc    | python chat.py -newc id_conversation user1,user2,user3 dm | creates a new conversation could be a dm or group |
| -newm    | python chat.py -newm user message 1                       | creates a new message in the given conversation   |
| -newu    | python chat.py -newu 1 user1                              | creates a new user                                |
| -listc   | python chat.py -listc                                     | list all conversation                             |
| -listm   | python chat.py -listm id_conversation                     | list all the messages in the given conversation   |
| -listu   | python chat.py -listu                                     | list all users                                    |
| -removec | python chat.py -removec id_conversation                   | remove a conversation based on id                 |
| -removem | python chat.py -removem id_user                           | remove a user based on id                         |
| -removeu | python chat.py -removeu id_usert                          | remove a user based on id                         |
| -clean   | python chat.py -clean                                     | clean the conversations and the messages tables   |
*--------------------------------------------------------------------------------------------------------------------------*""")
elif sys.argv[1] == '-newc':
    conversations.insert({
        "id_conversation": sys.argv[2],
        "members": sys.argv[3].split(','),
        "type": sys.argv[4],
        'created_at': now,
        'updated_at': now
    }).run(connection)
elif sys.argv[1] == '-newm':
    messages.insert({
        'payload':
        {
            'user': sys.argv[2],
            'message': sys.argv[3],
        },
        'id_conversation': sys.argv[4],
        'sent': 0,
        'created_at': now,
        'updated_at': now
    }).run(connection)
elif sys.argv[1] == '-newu':
    users.insert({
        'id_user': sys.argv[2],
        'username': sys.argv[3],
        'created_at': now,
        'updated_at': now
    }).run(connection)
elif sys.argv[1] == '-listc':
    print(conversations.run(connection))
elif sys.argv[1] == '-listu':
    print(users.run(connection))
elif sys.argv[1] == '-listm':
    print(messages.filter({
        "id_conversation": sys.argv[2]
    }).run(connection))
elif sys.argv[1] == '-removem':
    messages.filter({
        "id": sys.argv[2]
    }).delete().run(connection)
elif sys.argv[1] == '-removec':
    conversations.filter({
        "id": sys.argv[2]
    }).delete().run(connection)
elif sys.argv[1] == '-removeu':
    users.filter({
        "id": sys.argv[2]
    }).delete().run(connection)
elif sys.argv[1] == '-clean':
    for table in tables:
        table.delete().run(connection)
