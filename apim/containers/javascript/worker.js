#!/usr/bin/env node

var amqplib = require('amqplib');

function consume(host, port, queue) {
    url = 'amqp://' + host + ':' + port;
    amqplib.connect(url).then(function(conn) {
        return conn.createChannel().then(function(ch) {
            var ok = ch.assertQueue(queue, {durable: true});
            ok = ok.then(function(_qok) {
                return ch.consume(queue, on_consume, {noAck: true});
            });
            return ok;
        });
    }).then(null, console.warn);
}

function on_consume(msg) {
    console.log('got', msg.content.toString());
}

function results(responder) {
    console.log = function (data) {
        responder('---');
        responder(data);
    }
    var main = require('./main.js');
    main.process({foo: 3});
}


function worker() {
    var host = process.argv[3];
    var port = process.argv[5];
    var queue = process.argv[7];
    consume(host, port, queue);
}

worker();
