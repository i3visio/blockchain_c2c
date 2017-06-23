# !/usr/bin/python2
# -*- coding: utf-8 -*-

from binascii import hexlify
import codecs
import sys

from pycoin.key import Key
from pycoin.services.blockr_io import BlockrioProvider
from pycoin.tx import script
from pycoin.tx import tx_utils
from pycoin.tx import TxOut

def generatePrivateKey(seed, net="XTN"):
    """ Generating a private key from any hexadecimal seed and net.
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
    print "\tSeed: ", seed
    print "\tAddress: ", priv.address()
    print "\tWIF: ", priv.wif()
    return priv


if __name__ == "__main__":
    # Getting the brain wallet
    network = raw_input("> Choose type of network (BTC, XTN, LTC, ...) [XTN]: ") or "XTN"
    print "\tNetwork: " + network

    # Getting the brain wallet
    brain = raw_input("> Say word for the brainwallet: ")
    priv = generatePrivateKey(brain)

    # Get the spendable outputs we are going to use to pay the fee
    provider =  BlockrioProvider(netcode=network)
    spendables = provider.spendables_for_address(priv.address())

    # Summing it up
    source_balance = sum(spendable.coin_value for spendable in spendables)
    print "\tBalance: " + str(source_balance)

    # Defining the message to be send
    message_str = raw_input("> Set message to send: ")
    # No more than 80 caracters please!
    if(len(message_str) > 80):
        sys.exit("Message must be 80 characters or less")
    print "\tMessage (string): " + message_str
    message_hex = hexlify(message_str.encode()).decode('utf8')
    print "\tMessage (hexadecimal): " + message_hex

    # Defining the target address
    target_type = raw_input("> Set target address: 'brain' or 'other'? [brain] ") or "brain"

    if target_type == "brain":
        brain_dst = raw_input("> Say word for the TARGET brainwallet: ")
        print "\tWe will generate the details for the target address:"
        target = generatePrivateKey(brain_dst)
        dst_address = target.address()
    else:
        print "\tNote that you might not know the private key of this address so you can lose your balance:"
        dst_address = raw_input("> Set the target address: ")


    # Defining the default fee
    try:
        fee = int(raw_input("> Set the fee [10000]: "))
    except:
        fee = 10000
    print "\tDefault fee: " + str(fee)

    # Generating the transaction
    print "> We'll try to create the transaction using all the spendables for " + priv.address()
    # Creating the transaction
    tx = tx_utils.create_tx(
        spendables,
        [
            (dst_address, source_balance - fee )
        ],
        fee=fee
    )
    print "\tTx:\n" + str(tx)

    print "> We will create the OP_RETURN script for the message '" + message_str + "'."
    # We need the hexadecimal representation of the message
    op_return_output_script = script.tools.compile("OP_RETURN %s" % message_hex)
    print "\tOP_RETURN script:\n" + str([str(op_return_output_script)])

    print "> Appending the new OP_RETURN script to the transaction:"
    tx.txs_out.append(TxOut(0, op_return_output_script))
    print "\tTx:\n" + str(tx)
    print "\tNumber of outputs: " + str(len(tx.txs_out))
    print "\tDisplaying the outputs:\n"
    for o in tx.txs_out:
        print "\t\t- " + str(o)
    #print "\tDictionary representing the transaction:\n" + tx.__dict__

    print "> Signing the transaction:"
    tx_utils.sign_tx(
        tx,
        netcode=network,
        wifs=[priv.wif()]
    )
    print "\tNow tx is a signed transaction:"
    print "\tTx:\n" + str(tx)

    print "> Showing the hexadecimal information of the SIGNED transaction:"
    print tx.as_hex()

    print "> Now you can go to <https://tbtc.blockr.io/tx/push> to push this transaction. You might want to do it using Tor Browser to not let even Blockr.io to know who you are."
    print "> You can also manually push this to <http://tbtc.blockr.io/api/v1/tx/push> using a POST request."
