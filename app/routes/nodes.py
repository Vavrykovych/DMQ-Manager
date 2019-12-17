from flask import Blueprint
from app import *
import requests
from app.services.JSONService import JSONService
from queues import create_queue, delete_queue, QUEUE

nodes = Blueprint('nodes', __name__)
node_service = JSONService("app/data/data_nodes.json")
data_nodes_id_count = 0


@nodes.route('/connect_node', methods=['POST'])
def add_node():
    if not request.json:
        abort(404)

    try:
        payload = User().verify_token(request.headers['access_token'])
        if payload['connect_nodes']:
            url = request.json['ip'] + ':' + request.json['port']
            ping = requests.get(url=url + '/ping')
            if ping.text == 'pong':
                global data_nodes_id_count
                NODES = node_service.read()
                NODES.append(
                    {
                        "id": data_nodes_id_count,
                        "host": request.json["ip"],
                        "port": request.json["port"]
                    }
                )
                node_service.write(NODES)
                data_nodes_id_count += 1
                rsa_key = {'public_key': RSA_PUBLIC_KEY}
                requests.post(url=url + '/connect', json=rsa_key)
                for queue in QUEUE:
                    name = queue["name"]
                    requests.post(url=url + '/queues', json={"name": name}, headers = request.headers['access_token'])

            else:
                abort(404)
        else:
            abort(403)
    except:
        abort(404)
