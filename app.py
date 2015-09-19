#!/usr/bin/env python3
from flask import Flask, render_template, send_from_directory
import os
import fcntl
import socket
import struct

import vincent

# For debugging
from pprint import pprint

app = Flask(__name__)

world_topo = r'world-countries.topo.json'


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/static/<path:path>")
def send_static_files(path):
    return send_from_directory('static', path)


# Not sure where the request for this comes from, would like to condense this
# in to the json catchall below if we can find it
@app.route("/world-countries.topo.json")
def world_topo_json():
    return send_from_directory('static', 'json/' + world_topo)


@app.route("/gen_map")
def gen_map():
    geo_data = [{'name': 'countries',
                 'url': world_topo,
                 'feature': 'world-countries'}]

    vis = vincent.Map(geo_data=geo_data, scale=200)

    # update_props =
    # click_props =
    hover_props = vincent.PropertySet(fill=vincent.ValueRef(value='red'))
    vis.marks[0].properties.hover = hover_props

    vis.to_json("static/json/map.json")
    return "Map Generated"


def get_local_ip():
    """
    Enumerates through a list of common interface names to resolve internal IP.
    Note that Python3 expects bytes objects for the struct.pack() call.
    """
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = [
            b'eth0',
            b'eth1',
            b'eth2',
            b'wlan0',
            b'wlan1',
            b'wifi0',
            b'ath0',
            b'ath1',
            b'ppp0',
        ]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip


def get_interface_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack(b'256s', ifname[:15])
    )[20:24])


if __name__ == "__main__":
    host = '0.0.0.0'
    port = 5000

    print("Other people can connect to me from: %s:%d" % (get_local_ip(), port))
    app.run(host=host, port=port, debug=True)
