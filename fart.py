#!/usr/bin/env python3

import os
import json
from tcp_proxy import HttpProxy, Arguments

class Handler:
    def __init__(self, token, editor):
        if editor is None:
            editor = "$EDITOR"
        self.editor = editor
        self.token = token
        self.expected_response = False

    def handle_response(self, header, payload):
        if self.expected_response:
            with open("/tmp/fart_reply.header", "w") as f:
                json.dump(header, f, indent=2)
            with open("/tmp/fart_reply.req", "wb") as f:
                f.write(payload)
            os.system(self.editor + " /tmp/fart_reply.req /tmp/fart_reply.header")
            with open("/tmp/fart_reply.req", "rb") as f:
                payload = f.read()
            with open("/tmp/fart_reply.header", "rb") as f:
                header = json.load(f)
            self.expected_response = False
        return header, payload

    def handle_request(self, header, payload):
        if self.token.encode() in payload:
            with open("/tmp/fart.header", "w") as f:
                json.dump(header, f, indent=2)
            with open("/tmp/fart.req", "wb") as f:
                f.write(payload)
            os.system(self.editor + " /tmp/fart.req /tmp/fart.header")
            with open("/tmp/fart.req", "rb") as f:
                payload = f.read()
            with open("/tmp/fart.header", "rb") as f:
                header = json.load(f)
            self.expected_response = True
        return header, payload

if __name__ == '__main__':
    args = Arguments()
    args.add_arguments("-e", "--editor",
        help="Command to run to edit the packet to be sent",
        type=str)
    args.add_arguments("-t", "--token",
        help="Token to use to intercept the correct packet",
        type=str)
    args = args.get_args()

    if args.token is None:
        raise Exception("Missing token")
    if args.editor is None:
        print("editor argument is missing, using EDITOR instead")

    h = Handler(args.token, args.editor)
    proxy = HttpProxy(h, args.port)
    proxy.loop()
