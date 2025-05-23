from flask import Blueprint, request, jsonify
from urllib.parse import unquote
from controllers import tracker_controller as tracker, torrent_controller as torrent
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS
import logging
from werkzeug.datastructures import FileStorage
logging.basicConfig(level=logging.DEBUG)

tracker_router = Blueprint('tracker_route', __name__)
CORS(tracker_router, supports_credentials=True, origins=["http://localhost:3000"])

@tracker_router.route('/tracker/all_file', methods=['GET'])
def get_all_file_info():
    file_list = tracker.get_all_file_info()
    return jsonify(file_list), 200

@tracker_router.route('/tracker/all_peer', methods=['GET'])
def get_all_peers():
    peer_list = tracker.get_all_peer_info()
    total_count = len(peer_list)  # Calculate total peers
    return jsonify({
        "peers": peer_list,
        "total_count": total_count
    }), 200

@tracker_router.route('/tracker/peer/<name>', methods=['GET'])
def get_peer(name):
    peer = tracker.get_peer(name)
    if peer:
        return jsonify(peer), 200
    else:
        return jsonify({"error": "Peer not found"}), 404

@tracker_router.route("/tracker/peer/set_inactive", methods=["POST"])
@jwt_required()
def set_peer_inactive():
    peer_id = get_jwt_identity()  # Retrieve peer_id from JWT token
    if not peer_id:
        return jsonify({"error": "Missing peer_id"}), 400

    result = tracker.set_peer_inactive(peer_id)

    if result.modified_count == 1:
        return jsonify({"message": "Peer status changed to inactive"}), 200
    else:
        return jsonify({"error": "Peer not found or status not updated"}), 404

@tracker_router.route('/tracker/uploading', methods=['POST'])
@jwt_required()
def upload_data():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    # file = request.files['file']
    file: FileStorage = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    peer_id = get_jwt_identity()  # Retrieve peer_id from JWT token
    if peer_id is None:
        return jsonify({"error": "You need to log in before uploading"}), 401

    try:
        result = tracker.upload_file(file, peer_id)

        if result:
            return jsonify({"message": "File uploaded successfully"}), 201
        else:
            return jsonify({"error": "File upload failed"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred during upload: {str(e)}"}), 500

@tracker_router.route('/tracker/downloading/<encoded_magnet>', methods=['POST'])
@jwt_required()
def download_data(encoded_magnet):
    magnet_link = unquote(encoded_magnet)
    logging.debug(f"Received magnet link: {magnet_link}")
    # Validate magnet link format
    if magnet_link[:20] != "magnet:?xt=urn:btih:":
        logging.error("Invalid magnet link format")
        return jsonify({"error": "Invalid magnet link format"}), 400

    peer_id = get_jwt_identity()  # Retrieve peer_id from JWT token
    logging.debug(f"Retrieved peer_id: {peer_id}")
    if not peer_id:
        logging.error("Peer ID not found in JWT token")
        return jsonify({"error": "You need to log in before connecting to a peer"}), 401

    try:
        pieces, output_file = tracker.get_new_piece(magnet_link, peer_id)
        logging.debug(f"Pieces retrieved: {pieces}, Output file: {output_file}")
        if pieces is None:
            return jsonify({"error": "File does not exist"}), 404
        if not pieces:
            return jsonify({"error": "No data downloaded"}), 404
        else:
            torrent.combine_pieces(pieces, output_file)
            return jsonify({
                "message": "File downloaded successfully",
                "pieces": pieces,
                "file_name": output_file
            }), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred during download: {str(e)}"}), 500
