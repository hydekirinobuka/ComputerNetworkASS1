from flask import Blueprint, request, jsonify, make_response
from controllers import peer_controller as peer
import threading

peer_router = Blueprint('peer_router', __name__)


@peer_router.route('/peer/sign_up', methods=['POST'])
def peer_sign_up():
    # Lấy dữ liệu từ request JSON
    data = request.json

    if not data or 'name' not in data or 'password' not in data:
        return jsonify({"error": "Invalid input, name and password are required"}), 400
    
    name = data['name']
    password = data['password']

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
    # Lấy dữ liệu từ request JSON
    data = request.json

    if not data or 'name' not in data or 'password' not in data:
        return jsonify({"error": "Invalid input, name and password are required"}), 400
    
    name = data['name']
    password = data['password']

    valid, peer_id, ip, port = peer.login(name, password)

    if valid:
        # Nếu peer tồn tại, trả về thông tin và đặt cookie
        response = make_response(
            jsonify({ 
                "message": "Peer found",
                "peer_id": peer_id,  # Đảm bảo peer_id thực tế
                "ip_address": ip,
                "port": port,
            }), 201
        )
        # Thiết lập peer_id trong cookie bảo mật
        response.set_cookie('peer_id', peer_id, httponly=True, samesite='None', secure=True)

        return response
    else:
        # Nếu không tìm thấy peer
        return jsonify({"error": "Peer not found or invalid credentials!"}), 404

@peer_router.route('/peer/protected', methods=['GET'])
def protected():
    peer_id = request.cookies.get('peer_id')

    if not peer_id:
        return jsonify({"error": "Peer ID is missing!"}), 403

    return jsonify({"message": "Protected route accessed!", "peer_id": peer_id}), 200

@peer_router.route('/peer/start_peer', methods=['POST'])
def start_peer():
    # Lấy thông tin từ request JSON
    data = request.json
    ip = data.get('ip_address')
    port = data.get('port')

    # Lấy thông tin peer từ IP và port
    peer_id = peer.get_peer_info(ip, port)
    
    if not peer_id:
        return jsonify({"error": "You need to log in before starting the peer server"}), 401

    # Khởi tạo và chạy peer server trên thread riêng
    thread = threading.Thread(target=peer.run_peer_server, args=(str(ip), int(port), str(peer_id)))
    thread.start()
    
    return jsonify({"status": f"Peer server started on port {port}"}), 200

@peer_router.route('/peer/info', methods=['GET'])
def get_peer_info_by_id():
    # Lấy peer_id từ cookie
    peer_id = request.cookies.get('peer_id')

    if not peer_id:
        return jsonify({"error": "Peer ID is required to access this route"}), 400

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
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
