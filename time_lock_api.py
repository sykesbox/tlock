from flask import Flask, request, jsonify
import hashlib
import requests
import base64
from charm.toolbox.pairinggroup import PairingGroup, G1, G2, GT, pair

app = Flask(__name__)
group = PairingGroup('SS512')

def hash_to_group(value):
    return group.hash(value, G1)

def hash_function(value):
    return hashlib.sha256(value.encode()).digest()

def encrypt_message(message, future_round):
    Qid = hash_to_group(str(future_round))
    P = group.random(G1)
    Gid = pair(Qid, P)

    theta = group.random(GT)
    r = hash_function(str(theta) + message)

    U = r
    V = base64.b64encode(hash_function(str(U) + str(Gid))).decode()
    W = base64.b64encode(bytes(a ^ b for a, b in zip(message.encode(), hash_function(str(theta))))).decode()

    return {
        "U": base64.b64encode(U).decode(),
        "V": V,
        "W": W,
        "epoch": future_round
    }

def fetch_drand_randomness(round_number):
    url = f"https://api.drand.sh/public/{round_number}"
    response = requests.get(url)
    data = response.json()
    return data['randomness']

def decrypt_message(ciphertext):
    epoch = ciphertext['epoch']
    U = base64.b64decode(ciphertext['U'])
    V = base64.b64decode(ciphertext['V'])
    W = base64.b64decode(ciphertext['W'])

    drand_randomness = fetch_drand_randomness(epoch)
    
    Qid = hash_to_group(str(epoch))
    P = group.random(G1)
    Gid = pair(Qid, P)

    theta = base64.b64encode(hash_function(str(U) + str(Gid))).decode()
    decrypted_message = "".join(chr(a ^ b) for a, b in zip(W, hash_function(str(theta))))

    return decrypted_message

@app.route('/encrypt', methods=['POST'])
def encrypt_api():
    data = request.json
    return jsonify(encrypt_message(data['message'], data['future_round']))

@app.route('/decrypt', methods=['POST'])
def decrypt_api():
    data = request.json
    return jsonify({"decrypted_message": decrypt_message(data)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
