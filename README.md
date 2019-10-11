# chat
RethinkDB + Node + React chat application

## specs
There are two types of chats:
- direct messages, between two users where the 'read' functionality is available;
- group chat, where two or more users could be active, but 'read' functionality is unavailable;

## ideas
- for direct messages, front-end should emit 'sent' and receive back a response from the server;
- for direct messages, front-end should receive from the server an event when the other user reads his message;
- front-end should retry for some time to send the message, and have a button to retry when the user wants to retry when the default time expires;

## TODO:
- change how tables are checked for existence
