from flask import Blueprint, request, jsonify
from urllib.parse import unquote
from controllers import tracker_controller as tracker, torrent_controller as torrent
from flask_cors import CORS

tracker_router = Blueprint('tracker_route', __name__)
CORS(tracker_router, supports_credentials=True, origins=["http://localhost:3000"])

@tracker_router.route('/tracker/all_file', methods=['GET'])
def get_all_file_info():
    file_list = tracker.get_all_file_info()
    return jsonify(file_list), 200

@tracker_router.route('/tracker/all_peer', methods=['GET'])
def get_all_peers():
    peer_list = tracker.get_all_peer_info()
    total_count = len(peer_list)  # Tính tổng số peers
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

@tracker_router.route('/tracker/uploading', methods=['POST'])
def upload_data():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Nhận peer_id từ formData
    peer_id = request.form.get("peer_id")
    if peer_id is None:
        return jsonify({"error": "You need to log in before uploading"}), 401

    # Gọi hàm từ tracker_controller để xử lý dữ liệu tải lên
    result = tracker.upload_file(file, peer_id)

    if result:
        return jsonify({"message": "File uploaded successfully"}), 201
    else:
        return jsonify({"error": "File upload failed"}), 500

@tracker_router.route("/tracker/peer/set_inactive", methods=["POST"])
def set_peer_inactive():
    peer_id = request.cookies.get("peer_id")  # Lấy peer_id từ cookie
    if not peer_id:
        return jsonify({"error": "Missing peer_id"}), 400

    result = tracker.set_peer_inactive(peer_id)

    if result.modified_count == 1:
        return jsonify({"message": "Peer status changed to inactive"}), 200
    else:
        return jsonify({"error": "Peer not found or status not updated"}), 404

# @tracker_router.route("/tracker/peer/set_active", methods=["POST"])
# def set_peer_active():
#     peer_id = request.cookies.get("peer_id")  # Lấy peer_id từ cookie
#     if not peer_id:
#         return jsonify({"error": "Missing peer_id"}), 400

#     result = tracker.set_peer_active(peer_id)

#     if result.modified_count == 1:
#         return jsonify({"message": "Peer status changed to active"}), 200
#     else:
#         return jsonify({"error": "Peer not found or status not updated"}), 404

@tracker_router.route('/tracker/downloading/<encoded_magnet>', methods=['POST'])
def download_data(encoded_magnet):
    magnet_link = unquote(encoded_magnet)  # Giải mã magnet link
    if magnet_link[:20] != "magnet:?xt=urn:btih:":
        return jsonify({"error": "Invalid magnet link format"}), 400 
    # magnet_link = unquote(encoded_magnet)
    peer_id = request.cookies.get('peer_id')
    if not peer_id:
        return jsonify({"error": "You need to log in before connecting to a peer"}), 401

    pieces, output_file = tracker.get_new_piece(magnet_link, peer_id)
    
    # Kiểm tra kết quả tải xuống
    if pieces is None:
        return jsonify({"error": "File does not exist"}), 404
    # Nếu pieces là danh sách rỗng, có thể là không có dữ liệu được tải xuống
    if not pieces:
        return jsonify({"error": "No data downloaded"}), 404
    else:
        torrent.combine_pieces(pieces, output_file)
        return jsonify({
            "message": "File downloaded successfully",
            "pieces": pieces,
            "file_name": output_file
        }), 200

# @tracker_router.route('/tracker/downloading/<encoded_magnet>', methods=['POST'])
# def download_data(encoded_magnet):
#     # Giải mã magnet link
#     magnet_link = unquote(encoded_magnet)
#     if not magnet_link.startswith("magnet:?xt=urn:btih:"):
#         return jsonify({"error": "Invalid magnet link format"}), 400

#     # Giải mã info_hash từ magnet link
#     info_hash = torrent.decode_magnet_link(magnet_link)
#     if not info_hash:
#         return jsonify({"error": "Failed to decode magnet link"}), 400

#     # Kiểm tra cookie để lấy peer_id
#     peer_id = request.cookies.get('peer_id')
#     if not peer_id:
#         return jsonify({"error": "You need to log in before connecting to a peer"}), 401

#     # Lấy dữ liệu torrent từ cơ sở dữ liệu
#     torrent_data = torrent.get_torrent(magnet_link)
#     if not torrent_data:
#         return jsonify({"error": "Torrent not found for this magnet link"}), 404

#     # Lấy pieces và output file
#     pieces, output_file = tracker.get_new_piece(magnet_link, peer_id)
#     if pieces is None or not pieces:
#         return jsonify({"error": "No pieces available for download"}), 404

#     # Ghép nối các pieces thành file
#     try:
#         torrent.combine_pieces(pieces, output_file)
#         return jsonify({
#             "message": "File downloaded successfully",
#             "pieces": pieces,
#             "file_name": output_file
#         }), 200
#     except Exception as e:
#         return jsonify({"error": f"Failed to combine pieces: {str(e)}"}), 500