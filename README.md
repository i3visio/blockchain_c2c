# A PoC of a Blockchain-based C&C

## Description

This project contains a Proof of Concept on how to push information to the Bitcoin blockchain using `OP_RETURN`. 
Some sample clients have been added to illustrate how the information in the blockhain can be used as a place from where we can extract commands to be run or any other orders.
This PoC was originally presented at EuskalHack Security Congress @ Donostia-San Sebastián in 2017.

## Authors

Yaiza Rubio (@yrubiosec) and Félix Brezo (@febrezo)

## License

GPLv3+.

## Administration Tool

To run the Python administration and victim tools, users need to run:
```
git clone https://github.com/i3visio/blockchain_c2c
cd blockchain_c2c
pip install -r requirements
```

To start the administration tool:

```
cd admin
python blockchain_c2c.py
```

Afterwards, the interactive menus can be followed up.

At the moment, the transaction needs to be pushed manually using a suitable provider like Blockr.io.

## Consumer tools

### Using the Python Client

The Python client can be found under `/vitcim/python`. The file is:
```
cd victim/python
python blockchain_client.py
```

### Using the Javascript Client

Under the `victim/javascript/` a sample implementation of the `bitcoin_client.py` code has been ported to Javascript. This can be added on any website or browser extension easily.
