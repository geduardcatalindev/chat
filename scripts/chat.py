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
    print("ACTIONS: -help | -newc | -newm | -newu | -listc | -listm | -listu | -clean")
elif sys.argv[1] == '-help':
    print(
"""* CLI for adding in, listing from and cleaning conversations and messages tables ------------------------------------*
| -newc  | python chat.py -newc id_conversation user1,user2,user3 | creates a new conversation                       |
| -newm  | python chat.py -newm user message id_conversation      | creates a new message in the given conversation  |
| -newu  | python chat.py -newu user1                             | creates a new user                               |
| -listc | python chat.py -listc                                  | list all conversation                            |
| -listm | python chat.py -listm id_conversation                  | list all the messages in the given conversation  |
| -listu | python chat.py -listu                                  | list all users                                   |
| -clean | python chat.py -clean                                  | clean the conversations and the messages tables  |
*--------------------------------------------------------------------------------------------------------------------*""")
elif sys.argv[1] == '-newc':
    conversations.insert({
        "id_conversation": sys.argv[2],
        "members": sys.argv[3].split(','),
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
        'username': sys.argv[2],
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
elif sys.argv[1] == '-clean':
    for table in tables:
        table.delete().run(connection)
