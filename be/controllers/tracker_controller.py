from models import peer, file, torrent
from controllers import torrent_create , torrent_controller, peer_controller
from bson import ObjectId
import bencodepy
import hashlib
from werkzeug.datastructures import FileStorage
from io import BytesIO

def get_num_peer_active(peer_list):
    num = 0
    collection = peer.peer_collection()
    for p in peer_list:
        peer_info = collection.find_one({
            "_id": p['peer_id'] 
        })

        if peer_info is None:
            continue

        if peer_info['status'] == "active":
            num += 1

    return num

def get_all_file_info():
    file_collection = file.file_collection()
    torrent_collection = torrent.torrent_collection()
    file_list = []
    
    for f in file_collection.find():
        torrent_info = torrent_collection.find_one({
            '_id': f['metainfo_id']
        })

        seeder = get_num_peer_active(f['peers_info'])

        data = {
            'file_name': f['file_name'],
            'length': torrent_info['info']['length'],
            'seeder': seeder,
            'magnet_link': torrent_create.create_encode_magnet_link(torrent_info['info_hash'])
        }
        file_list.append(data)

    return file_list

def get_all_peer_info():
    collection = peer.peer_collection()
    peer_list = []
    for p in collection.find() :
        data = {
            "name": p["name"],  
            "ip_address": p["ip_address"],
            "port": p["port"],
            "status": p["status"]
        }
        peer_list.append(data)

    return peer_list

def get_peer(name):
    collection = peer.peer_collection()
    peer_data = collection.find_one({"name": name})
    data = None
    if peer_data:
        # Chuyển đổi đối tượng MongoDB về định dạng JSON
        data = {
            "name": peer_data['name'],
            "ip_address": peer_data['ip_address'],
            "port": peer_data['port'],
        }

    return data

def add_peer_to_file(torrent, peer_id, pieces_idx):
    metainfo_id = str(torrent["_id"])
    collection = file.file_collection()

    file_data = collection.find_one({
        "metainfo_id": ObjectId(metainfo_id)
    })

    if file_data:
        # Thêm peer mới vào mảng `peers_info`
        collection.update_one(
            {"metainfo_id": ObjectId(metainfo_id)},
            {"$push": {
                "peers_info": {"peer_id": ObjectId(peer_id), 
                               "pieces": pieces_idx}
            }}
        )
        print("Peer added successfully.")
    else:
        print("File with the given metainfo_id not found.")

# def upload_file(file_path, peer_id):
#     try:
#         pieces, pieces_arr, pieces_idx = torrent_create.generate_pieces(file_path, 512000)
#         # Các bước hình thành magnetext và metainfo của files
#         file_path.seek(0)
#         file_path.seek(0, 2) # seeks the end of the file
#         file_length = file_path.tell() # tell at which byte we are
#         file_path.seek(0, 0) # go back to the beginning of the file

#         output_file = f"{file_path.filename}.torrent"

#         # optional
#         info_hash = torrent_create.generate_info_hash(file_path.filename, 512000, pieces, file_length)
#         magnet_link = torrent_create.create_magnet_link(info_hash)
#         torrent_create.create_encode_magnet_link_file(magnet_link)

#         torrent_create.create_torrent_file(file_path.filename, 512000, pieces, file_length, output_file)
#         metainfo_id = add_torrent_to_db(output_file)

#         file_collection = file.file_collection()
#         file_data = {
#             "file_name": file_path.filename,
#             "metainfo_id": metainfo_id,
#             "peers_info": []
#         }

#         # Thêm peer_id vào mảng peer_ids
#         peer_info = {
#             "peer_id": ObjectId(peer_id),
#             "pieces": pieces_idx
#         }
#         file_data["peers_info"].append(peer_info)
#         # Thên file vào collection file
#         file_collection.insert_one(file_data)

#         # Thêm file vào field shared_files của peer
#         update_peer_shared_files(peer_id, metainfo_id, pieces_arr)

#         return True
#     except Exception as e:
#         print(f"Error uploading file: {e}")
#         return False
def upload_file(file_storage: FileStorage, peer_id: str):
    try:
        piece_length = 512000
        pieces, pieces_arr, pieces_idx = torrent_create.generate_pieces(file_storage, piece_length)
        file_storage.seek(0, 2) 
        file_length = file_storage.tell()  
        file_storage.seek(0, 0) 

        # Tên tệp torrent đầu ra
        output_file = f"{file_storage.filename}.torrent"

        # Tạo info_hash, liên kết magnet và tạo tệp torrent
        info_hash = torrent_create.generate_info_hash(file_storage.filename, piece_length, pieces, file_length)
        magnet_link = torrent_create.create_magnet_link(info_hash)

        # Lưu liên kết magnet vào một tệp (tuỳ chọn)
        torrent_create.create_encode_magnet_link_file(magnet_link)

        # Tạo tệp torrent
        torrent_create.create_torrent_file(file_storage, file_storage.filename, piece_length, pieces, file_length, output_file)

        # Thêm metadata torrent vào cơ sở dữ liệu
        metainfo_id = add_torrent_to_db(output_file)

        # Thêm dữ liệu tệp vào bộ sưu tập
        file_data = {
            "file_name": file_storage.filename,
            "metainfo_id": metainfo_id,
            "peers_info": [],
        }
        # Thêm peer_id vào mảng peer_ids
        peer_info = {
            "peer_id": ObjectId(peer_id),
            "pieces": pieces_idx
        }
        file_data["peers_info"].append(peer_info)
        # Thên file vào collection file
        file_collection = file.file_collection()  
        file_collection.insert_one(file_data)

        update_peer_shared_files(peer_id, metainfo_id, pieces_arr)
        return True

    except Exception as e:
        print(f"Error uploading file: {e}")
        return False

    except Exception as e:
        print(f"Error uploading file: {e}")
        return False

def update_peer_shared_files(peer_id, metainfo_id, pieces_arr):
    collection = peer.peer_collection()
    piece_data = []

    for piece_info in pieces_arr:
        data = {
            "metainfo_id": ObjectId(metainfo_id),
            "index": piece_info[1],
            "piece": piece_info[0]
        }
        piece_data.append(data)

    collection.update_one(
        {"_id": ObjectId(peer_id)}, 
        {
            "$addToSet": {"piece_info": piece_data}, # Thêm file_name vào mảng shared_files
        }
    )

def add_torrent_to_db(output_file):
    collection = torrent.torrent_collection()
    # Đọc tệp torrent
    with open(output_file, 'rb') as f:
        torrent_data = bencodepy.decode(f.read())

    # Chuẩn bị dữ liệu để thêm vào DB
    info = torrent_data[b'info']
    
    # Bencode thông tin để tạo info_hash
    bencoded_info = bencodepy.encode(info)
    info_hash = hashlib.sha1(bencoded_info).hexdigest()
    
    # Chuẩn bị dữ liệu để thêm vào DB
    torrent_info = {
        "info_hash": info_hash,
        "info": {
            "name": info[b'name'].decode('utf-8'),
            "piece length": info[b'piece length'],
            "length": info[b'length'],
            "pieces": info[b'pieces'],
        }
    }
    
    # Thêm dữ liệu vào collection torrents
    result = collection.insert_one(torrent_info)
    print(f"Torrent '{torrent_info['info']['name']}' added to database successfully!")
    return result.inserted_id

def set_all_peer_inactive():
    collection = peer.peer_collection()
    result = collection.update_many(
        {},
        {"$set": 
            {"status": "inactive"}
        }
    )

def set_peer_inactive(peer_id):
    collection = peer.peer_collection()

    result = collection.update_one(
        {"_id": ObjectId(peer_id)},
        {"$set": {
            "status": "inactive"
        }}
    )
    return result

def get_peer_from_file(magnet_link):
    torrent_data = torrent_controller.get_torrent(magnet_link)
    peer_list = torrent_controller.get_peer_list(torrent_data)
    return peer_list

def get_new_piece(magnet_link, peer_id):
    torrent_data = torrent_controller.get_torrent(magnet_link)
    peer_list = torrent_controller.get_peer_list(torrent_data)
    pieces_index = torrent_controller.get_pieces_idx(torrent_data)
    available_pieces = torrent_controller.get_available_pieces(peer_id, torrent_data)
    
    if not available_pieces:
        add_peer_to_file(torrent_data, peer_id, pieces_index)

    pieces = peer_controller.request_pieces_from_peers(peer_list, pieces_index, torrent_data, available_pieces)

    pieces_arr = []

    for i in range(len(pieces)):
        pieces_arr.append((pieces[i], i))

    pieces = peer_controller.get_total_piece_available(pieces, peer_id, str(torrent_data["_id"]))

    if not available_pieces:
        update_peer_shared_files(peer_id, str(torrent_data["_id"]), pieces_arr)
        
    output_file = torrent_data['info']['name']

    if pieces:
        pieces = torrent_controller.encode_list_to_base64(pieces)

    return pieces, output_file


