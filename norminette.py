#!/usr/bin/env python3

import argparse
import os
import re
import json
import threading
import uuid
import pika

class Sender:
    connection = None
    channel = None
    exchange = None
    reply_queue = None
    routing_key = "norminette"
    cb = None
    counter = 0
    corr_id = str(uuid.uuid4())

    def initialize(self, cb):
        self.cb = cb
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            'norminette.42.fr',
            5672,
            '/',
            pika.PlainCredentials('guest', 'guest')
            ))
        self.channel = self.connection.channel()
        self.exchange = self.channel.exchange_declare(exchange=self.routing_key)
        self.reply_queue = self.channel.queue_declare(exclusive=True).method.queue
        self.channel.queue_bind(exchange=self.routing_key, queue=self.reply_queue)
        self.channel.basic_consume(self.consume, queue=self.reply_queue, no_ack=True)
        self.counter = 0

    def desinitialize(self):
        if self.channel is not None:
            self.channel.close()
        if self.connection is not None:
            self.connection.close()

    def publish(self, content):
        self.counter += 1
        self.channel.basic_publish(exchange='',
            routing_key=self.routing_key,
            body=content,
            properties=pika.BasicProperties(
                reply_to = self.reply_queue,
                correlation_id = self.corr_id
            ))

    def consume(self, channel, method_frame, properties, body):
        self.counter -= 1
        self.cb(body.decode("utf-8"))

    def sync_if_needed(self, max = os.cpu_count()):
        if self.counter >= max:
            self.connection.process_data_events()

    def sync(self):
        while self.counter != 0:
            self.sync_if_needed(0)


class Norminette:
    files = None
    sender = None
    lock = None

    def initialize(self):
        self.files = []
        self.lock = threading.Lock()
        self.sender = Sender()
        self.sender.initialize(lambda payload: \
            self.manage_result(json.loads(payload)))

    def desinitialize(self):
        print('\r\x1b', end='')
        self.sender.desinitialize()

    def check(self, options):
        if options.version:
            self.version()
        else:
            options.rules = ''
            if len(options.files_or_directories) is not 0:
                self.populate_recursive(options.files_or_directories)
            else:
                self.populate_recursive([ os.getcwd() ])
            self.send_files(options)

        self.sender.sync()
        print()

    def populate_recursive(self, objects):
        for o in objects:
            if not os.path.isabs(o):
                o = os.path.abspath(o)

            if os.path.isdir(o):
                self.populate_recursive(self.list_dir(o))
            else:
                self.populate_file(o)

    def list_dir(self, dir):
        entries = os.listdir(dir)
        final = []
        for e in entries:
            if e[0] is not '.':
                final.append(os.path.join(dir, e))
        return final

    def version(self):
        print("Local version:\n0.1 unofficial")
        print("Norminette version:")
        self.send_content(json.dumps({'action': "version"}))

    def file_description(self, file, opts = {}):
        with open(file, 'r') as f:
            return json.dumps({ 'filename': file, 'content': f.read(), 'opts': opts })

    def is_a_valid_file(self, f):
        return f is not None and os.path.isfile(f) \
            and re.match(".*\\.[ch]$", f) is not None

    def populate_file(self, f):
        if not self.is_a_valid_file(f):
            self.manage_result({
                'filename': f,
                'display': "Warning: Not a valid file"
                })
            return

        self.files.append(f)

    def send_files(self, options):
        for f in self.files:
            self.send_file(f, options.rules)
            self.sender.sync_if_needed

    def send_file(self, f, rules):
        self.send_content(self.file_description(f, {rules: rules}))

    def send_content(self, content):
        self.sender.publish(content)

    def cleanify_path(self, filename):
        return filename.replace(os.getcwd() + '/', '', 1)

    def manage_result(self, result):
        self.lock.acquire()
        if 'filename' in result:
            print("\r\x1b[K\x1b[;1mNorme: " + self.cleanify_path(result['filename'] + '\x1b[m'), end='')
        if 'display' in result and result['display'] is not None:
            print()
            print(result['display'])
        self.lock.release()
        if 'stop' in result and result['stop'] is True:
            print()
            exit(0)

class Parser:
    def parse(self):
        parser = argparse.ArgumentParser(
            usage="Usage: %(prog)s [options] [files_or_directories]",
            allow_abbrev=False
            )
        parser.add_argument(
            '--version', '-v',
            help='Print version',
            action="store_true"
            )
        parser.add_argument('files_or_directories', nargs=argparse.REMAINDER)

        args = parser.parse_args()
        return args


n = Norminette()
n.initialize()
n.check(Parser().parse())
n.desinitialize()
