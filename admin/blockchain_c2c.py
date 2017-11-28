# !/usr/bin/python2
# -*- coding: utf-8 -*-
#
################################################################################
#
#    Copyright 2017 Félix Brezo and Yaiza Rubio (i3visio, contacto@i3visio.com)
#
#    This file is part of blockchain_c2c. You can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

import argparse
from binascii import hexlify
import codecs
import json
import random
import requests
import sys

from pycoin.key import Key
from pycoin.services.chain_so import ChainSoProvider
from pycoin.tx import script
from pycoin.tx import tx_utils
from pycoin.tx import TxOut


__version__  = "0.2.0"


VALID_NETWORKS = {
    'BTC': "BTC",
    'DASH': "DASH",
    'DOGE': "DOGE",
    'LTC': "LTC",
    "XTN": "BTCTEST",
    "tDASH": "DASHTEST",
    "XDT": "DOGETEST",
    "XLT": "LTCTEST"
}

def generatePrivateKey(seed, net="XTN"):
    """
    Generating a private key from any hexadecimal seed and net

    Args:
    -----
        seed: The seed to be used to generate the private key.
        net: The network to be used.

    Returns:
    --------
        The private key to be used.
    """
    # Generating the hexadecimal representation of the brainwallet
    key_bytes = hexlify(seed)
    # '68656c6c6f' for "hello"
    priv = Key(
        secret_exponent=int(
            codecs.encode(key_bytes, "hex"),
            16
        ),
        netcode=net
    )

    # Representation of the wallet
    print("\tSeed: " + seed)
    print("\tAddress: " + priv.address())
    print("\tWIF: " + priv.wif())
    return priv


def getProvider(network="XTN"):
    """
    Get a provider

    Args:
    -----
        network: The network to be used.

    Returns:
    --------
        A Pycoin provider.
    """
    provider = ChainSoProvider(
        netcode=network
    )
    print("\tProvider choosen: " + provider.__class__.__name__)
    return provider


def pushTx(network, tx_hex):
    """
    A method that wraps up the signed transaction from chain.so.

    Args:
    -----
        network: The network in which this will be pushed.
        tx_hex: The hexadecimal string representing the signed transaction.
    """
    payload = {
        "tx_hex": tx_hex
    }

    url = "https://chain.so/api/v2/send_tx/" + VALID_NETWORKS[network]
    print("\n> Sending POST request to <" + url + ">.")
    r = requests.post(url, data=payload)
    print(r.content)
    return r


def getParser():
    parser = argparse.ArgumentParser(description='Blockchain C2C [Admin] - Issueing orders to different blockchains.', add_help=False)
    parser._optionals.title = "Input options (one required)"

    # Configuring the processing options
    groupProcessing = parser.add_argument_group('Processing arguments', 'Configuring the way in which the applicaiton will behave.')
    groupProcessing.add_argument('--push', required=False, default=False, action='store_true', help='Defines whether to push the transaction to the blockchain or just show the output.')


    # About options
    groupAbout = parser.add_argument_group('About arguments', 'Showing additional information about this program.')
    groupAbout.add_argument('-h', '--help', action='help', help='shows this help and exists.')
    groupAbout.add_argument('--version', action='version', version=__version__, help='shows the version of the program and exists.')

    return parser


def main(params=[]):
    """
    Main function that deals with the information

    Args:
    -----
        params: List of arguments received from the command line.
    """
    banner = """
     ____  _            _        _           _          ____ ____   ____
    | __ )| | ___   ___| | _____| |__   __ _(_)_ __    / ___|___ \ / ___|
    |  _ \| |/ _ \ / __| |/ / __| '_ \ / _` | | '_ \  | |     __) | |
    | |_) | | (_) | (__|   < (__| | | | (_| | | | | | | |___ / __/| |___
    |____/|_|\___/ \___|_|\_\___|_| |_|\__,_|_|_| |_|  \____|_____|\____|

                    A PoC to push data to several blockchains by:
                            - Yaiza Rubio (@yrubiosec)
                            - Félix Brezo (@febrezo)"""
    print(banner)
    # Grabbing the parser
    parser = getParser()

    if params != None:
        args = parser.parse_args(params)
    else:
        args = parser.parse_args()

    # Getting the brain wallet
    network = raw_input("\n> Choose type of network (BTC, XTN, LTC, XLT...) [XTN] ") or "XTN"
    while network not in VALID_NETWORKS:
        print("> The value provided '" + network +  "' is not a possible option. Choose one of the following:\n" + json.dumps(VALID_NETWORKS.keys(), indent=2))
        network = raw_input("\n> Choose type of network (BTC, XTN, LTC, XLT...) [XTN] ") or "XTN"
    print("\tNetwork: " + network)

    # Defining the target address
    admin_type = None
    while admin_type not in ["brain", "other"]:
        admin_type = raw_input("\n> Set ADMIN address: 'brain' or 'other'? [brain] ") or "brain"
        if admin_type == "brain":
            brain = raw_input("\n> Say word for the ADMIN brainwallet: ")
            print("\tWe will generate the details for the target address:")
            priv = generatePrivateKey(brain)
            src_address = priv.address()
        elif admin_type == "other":
            print("\tNote that you might not know the private key of this address so you can lose your balance:")
            src_WIF = raw_input("\n> Set the admin private key in WIF format: ")
            #TODO:
            priv = Key.from_text(src_WIF)
        else:
            admin_type = raw_input("\n> Set ADMIN address: 'brain' or 'other'? [brain] ") or "brain"

    # Get the spendable outputs we are going to use to pay the fee
    print("\n> Choosing a provider!")
    provider = getProvider(network=network)
    spendables = provider.spendables_for_address(priv.address())

    # Summing it up
    source_balance = sum(spendable.coin_value for spendable in spendables)
    print("\tBalance: " + str(source_balance))

    if source_balance <= 0:
        print("\n> No money in the account! You will need an account with some! Exiting!")
        sys.exit()

    # Defining the message to be send
    message_str = raw_input("\n> Set message to send: ")
    # No more than 80 caracters please!
    if(len(message_str) > 80):
        sys.exit("Message must be 80 characters or less")
    print("\tMessage (string): " + message_str)
    message_hex = hexlify(message_str.encode()).decode('utf8')
    print("\tMessage (hexadecimal): " + message_hex)

    # Defining the target address
    target_type = None
    while target_type not in ["brain", "other"]:
        target_type = raw_input("\n> Set target address: 'brain' or 'other'? [brain] ") or "brain"
        if target_type == "brain":
            brain_dst = raw_input("\n> Say word for the TARGET brainwallet: ")
            print("\tWe will generate the details for the target address:")
            target = generatePrivateKey(brain_dst)
            dst_address = target.address()
        elif target_type == "other":
            print("\tNote that you might not know the private key of this address so you can lose your balance:")
            dst_address = raw_input("\n> Set the target address: ")
        else:
            target_type = raw_input("\n> Set target address: 'brain' or 'other'? [brain] ") or "brain"

    # Defining the default fee
    try:
        fee = int(raw_input("\n> Set the fee [10000]: "))
    except:
        fee = 10000
    print("\tFee assigned: " + str(fee))

    # Generating the transaction
    print("\n> We'll try to create the transaction using all the spendables for " + priv.address())
    # Creating the transaction
    tx = tx_utils.create_tx(
        spendables,
        [
            (dst_address, source_balance - fee )
        ],
        fee=fee
    )
    print("\tTx:\n" + str(tx))

    print("\n> We will create the OP_RETURN script for the message '" + message_str + "'.")
    # We need the hexadecimal representation of the message
    op_return_output_script = script.tools.compile("OP_RETURN %s" % message_hex)
    print("\tOP_RETURN script:\n" + str([str(op_return_output_script)]))

    print("\n> Appending the new OP_RETURN script to the transaction:")
    tx.txs_out.append(TxOut(0, op_return_output_script))
    print("\tTx:\n" + str(tx))
    print("\tNumber of outputs: " + str(len(tx.txs_out)))
    print("\tDisplaying the outputs:\n")
    for o in tx.txs_out:
        print("\t\t- " + str(o))
    #print "\tDictionary representing the transaction:\n" + tx.__dict__

    print("\n> Signing the transaction:")
    tx_utils.sign_tx(
        tx,
        netcode=network,
        wifs=[priv.wif()]
    )
    print("\tNow tx is a signed transaction:")
    print("\tTx:\n" + str(tx))

    print("\n> Showing the hexadecimal information of the SIGNED transaction:")
    print(tx.as_hex())

    if args.push:
        print("\n> We will try to push the signed transaction now:")
        pushTx(network=network, tx_hex=tx.as_hex())
    else:
        print("\n> You can push this transaction manually using curl:")
        print("\tcurl -d 'tx_hex=" + tx.as_hex() + "' https://chain.so/api/v2/send_tx/" + VALID_NETWORKS[network] )
        print("\n> You can also manually push this with the Web UI of BlockExplorer at <https://testnet.blockexplorer.com/tx/send>.")
        print("\n> You might want to do it using Tor Browser Bundle or torify to not let even a trace to know who you are in the provider.")


if __name__ == "__main__":
    main(sys.argv[1:])
