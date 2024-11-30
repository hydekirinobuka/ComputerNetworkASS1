from flask import Blueprint, request, jsonify, make_response
from controllers import peer_controller as peer
import threading
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

peer_router = Blueprint('peer_router', __name__)


@peer_router.route('/peer/sign_up', methods=['POST'])
def peer_sign_up():
    # Lấy dữ liệu từ request JSON
    data = request.json
    
    if not data or 'name' not in data or 'password' not in data:
        return jsonify({"error": "Invalid input, name and password are required"}), 400

    
    # name = data['name']
    # password = data['password']
    name = data.get('name')
    password = data.get('password')
    
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400
    if not name.isalnum():
        return jsonify({"error": "Name must be alphanumeric"}), 400
    
    ip, port = peer.sign_up(name, password)

    if ip is None and port is None:
        return jsonify({"error": "Name already exists"}), 400
    
    return jsonify({
        "message": "Peer signed up successfully",
        "ip_address": ip,
        "port": port,
    }), 201

@peer_router.route('/peer/login', methods=['POST'])
def peer_login():
    print("Accessing /peer/login route")
    data = request.json

    if not data or 'name' not in data or 'password' not in data:
        return jsonify({"error": "Invalid input, name and password are required"}), 400
    
    name = data['name']
    password = data['password']

    valid, peer_id, ip, port = peer.login(name, password)

    if valid:
        access_token = create_access_token(identity=peer_id)
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "ip_address": ip,
            "port": port
        }), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401


@peer_router.route('/peer/protected', methods=['GET'])
@jwt_required()
def protected():
    # Lấy thông tin từ JWT
    peer_id = get_jwt_identity()
    return jsonify({"message": "Protected route accessed!", "peer_id": peer_id}), 200


@peer_router.route('/peer/start_peer', methods=['POST'])
@jwt_required()
def start_peer():
    # Lấy thông tin từ request JSON
    peer_id = get_jwt_identity()
    data = request.json
    ip = data.get('ip_address')
    port = data.get('port')

    if not peer.get_peer_info(ip, port):
        return jsonify({"error": "Invalid IP or port"}), 400

    thread = threading.Thread(target=peer.run_peer_server, args=(ip, port, peer_id))
    thread.start()

    return jsonify({"status": f"Peer server started on port {port}"}), 200

@peer_router.route('/peer/info', methods=['GET'])
@jwt_required() #HÀm này đã Kiểm tra peer rồi
def get_peer_info_by_id():
    # Lấy peer_id 
    peer_id = get_jwt_identity()
    try:
        # Lấy thông tin peer từ controller
        peer_info = peer.get_peer_by_id(peer_id)
        
        if peer_info:
            return jsonify({
                "ip_address": peer_info['ip_address'],
                "port": peer_info['port']
            }), 200
        else:
            return jsonify({"error": "Peer not found"}), 404
    except Exception as e:
        print(f"Error occurred while fetching peer info: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
