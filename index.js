require('./configs/env');

const http = require('http');
const express = require('express');
const socket = require('socket.io');
const async = require('async');
const rdb = require('rethinkdb');

const config = {
    rethinkdb: {
        host: 'localhost',
        port: 28015,
        authKey: '',
        db: 'chat'
    },
    express: {
        port: 7356
    }
};

const app = express();
const server = http.createServer(app);
const io = socket(server);

function startExpress(connection) {
    server._rdbConn = connection;
    server.listen(config.express.port);
}

async.waterfall([
    function connect(callback) {
        rdb.connect(config.rethinkdb, callback);
    },
    
    // create the database in case it does not exist already
    function createDatabase(connection, callback) {
        rdb.dbList().contains(config.rethinkdb.db).do(function(databaseExists) {
            return rdb.branch(databaseExists, { dbs_created: 0 }, rdb.dbCreate(config.rethinkdb.db));
        }).run(connection, function(err) {
            callback(err, connection);
        });
    },
    
    // create the tables in case it does not exist already
    function createConversationsTable(connection, callback) {
        rdb.tableList().contains('conversations').do(function(tableExists) {
            return rdb.branch(tableExists, { tables_created: 0 }, rdb.tableCreate('conversations'));
        }).run(connection, function(err) {
            callback(err, connection);
        });
    },
    function createMessagesTable(connection, callback) {
        rdb.tableList().contains('messages').do(function(tableExists) {
            return rdb.branch(tableExists, { tables_created: 0 }, rdb.tableCreate('messages'));
        }).run(connection, function(err) {
            callback(err, connection);
        });
    },
    function createUsersTable(connection, callback) {
        rdb.tableList().contains('users').do(function(tableExists) {
            return rdb.branch(tableExists, { tables_created: 0 }, rdb.tableCreate('users'));
        }).run(connection, function(err) {
            callback(err, connection);
        });
    },
    
    function listen(connection, callback) {
        rdb.table('messages').changes().run(connection, function (err, cursor) {
            if (err) throw err;
            cursor.each(function (err, row) {
                if (err) throw err;
    
                // console.log(JSON.stringify(row, null, 2));
                
                let data = row.new_val;
                io.sockets.emit('new_message', {
                    // TODO: emit the new message through the socket in the right conversation
                });
            });
            callback(err, connection);
        });
    }
], function(err, connection) {
        if(err) {
            console.error(err);
            process.exit(1);
            return;
        }
    startExpress(connection);
    io.on('connection', (socket) => {
        socket.on('received', (data) => {
            rdb.table('conversations').update({sent: 1}).run(connection);
        });
    });
});
