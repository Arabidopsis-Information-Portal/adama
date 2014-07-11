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

            function on_consume(msg) {
                var lines = [];
                var responder = function(data) {
                    ch.publish('', msg.properties.replyTo,
                               new Buffer(data));
                };
                console.log = function(data) {
                    if (data === '---' || data === 'END') {
                        responder(lines.join(' '));
                        lines = [];
                    } else {
                        lines.push(data);
                    }
                    if (data === 'END') {
                        responder(data);
                    }
                };
                try {
                    var main = require('./user_code/main.js');
                    main.process(JSON.parse(msg.content.toString()));
                    responder(JSON.stringify({'time_in_main': 0}));
                }
                catch (err) {
                    responder(JSON.stringify({error: err.message}));
                    responder('END');
                    responder(JSON.stringify({'time_in_main': 0}));
                }
            };

        });
    }).then(null, function (msg) {
        console.error('*** WORKER ERROR');
        console.error(msg);
    });
}

function worker() {
    var host = process.argv[3];
    var port = process.argv[5];
    var queue = process.argv[7];
    console.error('*** WORKER STARTED');
    consume(host, port, queue);
}

worker();
