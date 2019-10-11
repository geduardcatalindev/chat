require('./configs/env');
const DB_CONFIG = require('./configs/db');
const EXPRESS_CONFIG = require('./configs/express');

const http = require('http');
const express = require('express');
const socket = require('socket.io');
const async = require('async');
const rdb = require('rethinkdb');

const d = require('./data/get');

const app = express();
const server = http.createServer(app);
const io = socket(server);

function startExpress(connection) {
    server._rdbConn = connection;
    server.listen(EXPRESS_CONFIG.express.port);
}

async.waterfall([
    function connect(callback) {
        rdb.connect(DB_CONFIG.rethinkdb, callback);
    },
    
    // create the database in case it does not exist already
    function createDatabase(connection, callback) {
        rdb.dbList().contains(DB_CONFIG.rethinkdb.db).do(function(databaseExists) {
            return rdb.branch(databaseExists, { dbs_created: 0 }, rdb.dbCreate(DB_CONFIG.rethinkdb.db));
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
    
    // listen for new messages and send them in the right conversation
    function listen(connection, callback) {
        rdb.table('messages').filter({sent: 0}).changes().run(connection, function (err, cursor) {
            if (err) throw err;
            cursor.each(function (err, row) {
                if (err) throw err;
                if (row.new_val) {
                    io.sockets.emit('new_message', {
                        id: row.new_val.id,
                        user: row.new_val.payload.user,
                        message: row.new_val.payload.message
                    });
                }
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
        socket.on('connected', (data) => {
            d.userConversations(io, rdb, connection, data.username);
        });
        socket.on('read', (data) => {
            rdb.table('messages')
            .filter({id: data.id})
            .update({sent: 1}).run(connection);
        });
    });
});
