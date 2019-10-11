module.exports = {
    userConversations: function(io, rdb, connection, username) {
        return rdb.table('conversations')
            .filter(function(entry) {
                return entry('members').contains(username);
            })
            .pluck('id_conversation')
            .run(connection, function(err, cursor) {
                if (err) throw err;
                cursor.toArray((err, result) => {
                    if (err) throw err;
                    io.sockets.emit('conversations', {conversations: JSON.stringify(result)});
                })
            });
    }
}
