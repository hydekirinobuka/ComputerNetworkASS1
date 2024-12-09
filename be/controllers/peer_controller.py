import logging
from flask import Flask, request
from models import peer
from bson import ObjectId
import socket
import threading
from queue import Queue
import base64
from werkzeug.security import generate_password_hash, check_password_hash

logging.basicConfig(level=logging.DEBUG)

def get_ip_and_port():
    """
    Hàm lấy thông tin IP và Port của client kết nối.
    """
    peer_ip = request.remote_addr  # Địa chỉ IP của client
    peer_port = request.environ.get('REMOTE_PORT')  # Cổng của client
    return peer_ip, peer_port

def get_peer_info(ip, port):
    """
    Hàm lấy thông tin IP và Port của client kết nối.
    """
    collection = peer.peer_collection()
    peer_data = collection.find_one({
        "ip_address": ip,
        "port": port
    })

    return str(peer_data["_id"]) if peer_data else None

def check_name_exists(name):
    collection = peer.peer_collection()
    peer_data = collection.find_one({"name": name})
    return peer_data is not None

def sign_up(name, password):
    try:
        if check_name_exists(name):
            logging.error(f"Tên {name} đã tồn tại!")
            return None, None  # Trả về lỗi nếu tên đã tồn tại
        
        collection = peer.peer_collection()
        ip, port = get_ip_and_port()
        hashed_password = generate_password_hash(password)
        
        data = {
            "_id": ObjectId(),
            "name": name,
            "password": hashed_password,
            "ip_address": ip,
            "port": port,
            "piece_info": [],
            "status": "inactive"
        }

        # Thêm người dùng vào cơ sở dữ liệu
        result = collection.insert_one(data)
        logging.info(f"Peer {name} signed up successfully with IP: {ip} and port: {port}")
        return ip, port
    
    except Exception as e:
        logging.error(f"Error in sign_up: {str(e)}")
        return None, None

def login(name, password):
    collection = peer.peer_collection()
    ip, port = get_ip_and_port()
    # tim user
    user = collection.find_one({"name": name})

    if user and check_password_hash(user["password"], password):  # Kiểm tra mật khẩu
        # Cập nhật thông tin IP, cổng và trạng thái đăng nhập
        collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "ip_address": ip,  # IP mới khi đăng nhập
                    "port": port,
                    "status": "active"
                }
            }
        )
        return True, str(user["_id"]), ip, port
    
    return False, None, None, None





def request_piece(peer_id, piece_index, pieces, requested_pieces, queue_lock, metainfo_id):
    peer_ip = peer_id['ip_address']
    peer_port = peer_id['port']
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((peer_ip, peer_port))

            # Gửi yêu cầu lấy piece cụ thể
            request_message = f"REQUEST_PIECE|{piece_index, metainfo_id}"
            client_socket.send(request_message.encode())
            
            # Nhận dữ liệu piece từ peer
            data = b''
            while len(data) < 512000:
                piece_data = client_socket.recv(4096)  # Nhận dữ liệu tối đa 4096 bytes mỗi lần
                if not piece_data:  # Kiểm tra nếu không còn dữ liệu
                    break

                if len(piece_data) < 4096:
                    data += piece_data
                    break

                data += piece_data  # Nối dữ liệu vào biến data

            if data == "PIECE_NOT_FOUND":
                print(f"Piece {piece_index} not found on peer {peer_ip}:{peer_port}")
            else:
                print(f"Received piece data from {peer_ip}:{peer_port} for piece {piece_index}")
                # Lưu piece vào danh sách, cập nhật trạng thái
                with queue_lock:
                    pieces[piece_index] = data
                    requested_pieces.remove(piece_index)

    except ConnectionRefusedError:
        print(f"Không thể kết nối đến peer {peer_ip}:{peer_port}")
    except Exception as e:
        print(f"Đã xảy ra lỗi khi kết nối tới peer {peer_ip}:{peer_port}: {str(e)}")

def request_pieces_from_peers(peer_list, piece_indexes, torrent_data, available_pieces):
    # Kiểm tra nếu piece_indexes rỗng
    if not piece_indexes:
        pieces = [None] * (max(available_pieces) + 1) # Hoặc khởi tạo như một danh sách với các phần tử None
    elif not available_pieces:
        pieces = [None] * (max(piece_indexes) + 1)  # Danh sách lưu các pieces đã nhận
    else: 
        pieces = [None] * (max(max(available_pieces), max(piece_indexes)) + 1)

    print(peer_list, piece_indexes, available_pieces)
    print(len(pieces))
    requested_pieces = set()  # Set để lưu các pieces đang được yêu cầu
    queue_lock = threading.Lock()
    threads = []

    # Hàng đợi để quản lý các yêu cầu tải xuống
    piece_queue = Queue()
    metainfo_id = str(torrent_data["_id"])
    # Thêm các piece cần tải (dựa vào các chỉ số piece) vào hàng đợi
    for piece_index in piece_indexes:
        if piece_index not in available_pieces:  # Kiểm tra piece có sẵn
            piece_queue.put(piece_index)

    #print(peer_id, piece_index, pieces, requested_pieces, queue_lock, metainfo_id)
    while not piece_queue.empty():
        piece_index = piece_queue.get()

        # Chọn peer có piece đó theo vòng lặp danh sách
        peer_id = peer_list[piece_index % len(peer_list)]
        with queue_lock:
            if piece_index not in requested_pieces:
                requested_pieces.add(piece_index)
                
                # Tạo thread cho từng piece và peer
                thread = threading.Thread(target=request_piece, args=(peer_id, piece_index, pieces, requested_pieces, queue_lock, metainfo_id))
                threads.append(thread)
                thread.start()

    # Chờ cho tất cả các thread hoàn thành
    for thread in threads:
        thread.join()

    return pieces

def is_port_open(ip, port, timeout=1):
    """
    Kiểm tra xem IP và cổng có đang lắng nghe kết nối không.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.connect((ip, port))
            return True  # Kết nối thành công, nghĩa là cổng đang lắng nghe
        except (socket.timeout, ConnectionRefusedError):
            return False  # Kết nối thất bại, nghĩa là cổng không có ai lắng nghe

def run_peer_server(ip, port, peer_id):
    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if is_port_open(ip, port):
        print(f"Peer server đã chạy trên {ip}:{port}. Không cần khởi động lại.")
        return {"status": f"Peer server đã chạy trên {ip}:{port}"}
    
    peer_socket.bind((ip, port))
    peer_socket.listen(50)
    
    while True:
        client_socket, addr = peer_socket.accept()
        request = client_socket.recv(1024).decode()
        if(request.startswith("REQUEST_PIECE")):
             # Tách lấy piece_index và metainfo_id từ request
            try:
                _, params = request.split("|")
                piece_index, metainfo_id = eval(params)  # Lấy piece_index từ params
                # Gửi dữ liệu của piece về cho client
                send_piece_data(piece_index, client_socket, peer_id, metainfo_id)
            except Exception as e:
                print(f"Error processing request: {str(e)}")
                client_socket.send(b"ERROR")

def send_piece_data(piece_index, client_socket, peer_id, metainfo_id):
    """Hàm này gửi dữ liệu của piece được yêu cầu về cho client."""
    collection = peer.peer_collection()
    peer_data = collection.find_one({
        "_id": ObjectId(peer_id)
    })

    if peer_data and "piece_info" in peer_data:
        # Truy xuất mảng piece_info
        piece_info = peer_data["piece_info"]
        # print(piece_info, piece_index, metainfo_id)
        # Sử dụng vòng lặp for để tìm piece có index bằng piece_index
        piece_data = None
        for piece in piece_info:
            for p in piece:
                if p["index"] == piece_index and p["metainfo_id"] == ObjectId(metainfo_id):
                    piece_data = p["piece"]
                    break
            
        if piece_data:
            total_sent = 0  # Số bytes đã gửi
            piece_length = len(piece_data)
            while total_sent < piece_length:
                sent = client_socket.send(piece_data[total_sent:])  # Gửi dữ liệu từ vị trí hiện tại
                if sent == 0:
                    raise RuntimeError("Socket connection broken")
                total_sent += sent  # Cập nhật số bytes đã gửi

        else:
            client_socket.send(b"PIECE_NOT_FOUND")
            print("Không tìm thấy piece với piece_index yêu cầu.")
    else:
        # Nếu piece không tồn tại, trả về thông báo lỗi
        client_socket.send(b"PIECE_NOT_FOUND")
        print(f"Piece {piece_index} not found.")

def get_peer_by_id(peer_id):
    collection = peer.peer_collection()
    
    try:
        peer_data = collection.find_one({"_id": ObjectId(peer_id)})
        if peer_data:
            return {
                "ip_address": peer_data["ip_address"],
                "port": peer_data["port"]
            }
        else:
            return None
    except Exception as e:
        print(f"Error retrieving peer info: {str(e)}")
        return None

def get_available_piece(piece_index, peer_id, metainfo_id):
    """Hàm này gửi dữ liệu của piece được yêu cầu về cho client."""
    collection = peer.peer_collection()
    peer_data = collection.find_one({
        "_id": ObjectId(peer_id)
    })

    if peer_data and "piece_info" in peer_data:
        # Truy xuất mảng piece_info
        piece_info = peer_data["piece_info"]
        # print(piece_info, piece_index, metainfo_id)
        # Sử dụng vòng lặp for để tìm piece có index bằng piece_index
        for piece in piece_info:
            for p in piece:
                if p["index"] == piece_index and p["metainfo_id"] == ObjectId(metainfo_id):
                    return p["piece"]
                
    return None

def get_total_piece_available(pieces, peer_id, metainfo_id):
    for i in range(len(pieces)):
        if(pieces[i] is None):
            pieces[i] = get_available_piece(i, peer_id, metainfo_id)
            if(pieces[i] is None):
                print(f'Error getting piece: index {i}')

    return pieces