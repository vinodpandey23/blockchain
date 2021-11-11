import datetime
import hashlib
import json
from http import HTTPStatus

from flask import Flask, jsonify


class Blockchain:

    def __init__(self):
        self.__chain = []
        self.create_block(proof=1, previous_hash='0')

    def get_chain(self):
        return self.__chain

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.__chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.__chain.append(block)
        return block

    def get_previous_block(self):
        return self.__chain[- 1]

    # noinspection PyMethodMayBeStatic
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False

        while check_proof is False:
            hash_operation = hashlib \
                .sha256(str(new_proof ** 2 - previous_proof ** 2)
                        .encode()) \
                .hexdigest()

            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    # noinspection PyMethodMayBeStatic
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self):
        previous_block = self.__chain[0]
        block_index = 1

        while block_index < len(self.__chain):
            current_block = self.__chain[block_index]

            if current_block['previous_hash'] != self.hash(previous_block):
                return False

            previous_proof = previous_block['proof']
            current_proof = current_block['proof']

            hash_operation = hashlib \
                .sha256(str(current_proof ** 2 - previous_proof ** 2)
                        .encode()) \
                .hexdigest()

            if hash_operation[:4] != '0000':
                return False

            previous_block = current_block
            block_index += 1

        return True


app = Flask(__name__)

blockchain = Blockchain()


@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']

    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)

    block = blockchain.create_block(proof, previous_hash)
    response = {
        'message': 'Congratulations, you just mined a block!',
        'block': block
    }
    return jsonify(response), HTTPStatus.OK


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'length': len(blockchain.get_chain()),
        'chain': blockchain.get_chain()
    }
    return jsonify(response), HTTPStatus.OK


@app.route('/is_valid', methods=['GET'])
def is_valid():
    response = {
        'valid': blockchain.is_chain_valid()
    }
    return jsonify(response), HTTPStatus.OK


app.run(host='127.0.0.1', port=5000)
