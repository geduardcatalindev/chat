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

def randomString(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

if len(sys.argv) < 2:
    print("ACTIONS: newc | newm | listc | listm | clean")
elif sys.argv[1] == '-help':
    print(
"""* CLI for adding in, listing from and cleaning conversations and messages tables ------------------------------------*
| -newc  | python chat.py -newc id_conversation user1,user2,user3 | creates a new conversation                       |
| -newm  | python chat.py -newm user message id_conversation      | creates a new message in the given conversation  |
| -newu  | python chat.py -newu user1                             | creates a new user                               |
| -listc | python chat.py -listc                                  | list all conversation                            |
| -listc | python chat.py -listm id_conversation                  | list all the messages for the given conversation |
| -clean | python chat.py -clean                                  | clean the conversations and the messages tables  |
*--------------------------------------------------------------------------------------------------------------------*""")
elif sys.argv[1] == '-newc':
    members = sys.argv[3].split(',')
    conversations.insert({
        "id_conversation": sys.argv[2],
        "members": members,
        'created_at': now,
        'updated_at': now
    }).run(connection)
elif sys.argv[1] == '-newm':
    if len(sys.argv) >= 3:
        user = sys.argv[2]
    else:
        user = randomString(5)
    if len(sys.argv) >= 4:
        message = sys.argv[3]
    else:
        message = randomString(15)
    if len(sys.argv) >= 5:
        id_conversation = sys.argv[4]
    else:
        id_conversation = 1
    messages.insert({
        'payload':
        {
            'user': user,
            'message': message,
        },
        'id_conversation': id_conversation,
        'created_at': now,
        'updated_at': now,
        'sent': 0,
    }).run(connection)
elif sys.argv[1] == '-newu':
    users.insert({
        'username': sys.argv[2],
        'created_at': now,
        'updated_at': now
    }).run(connection)
elif sys.argv[1] == '-listc':
    print(conversations.run(connection))
elif sys.argv[1] == '-listm':
    print(messages.filter({
        "id_conversation": sys.argv[2]
    }).run(connection))
elif sys.argv[1] == '-clean':
    for table in tables:
        table.delete().run(connection)
