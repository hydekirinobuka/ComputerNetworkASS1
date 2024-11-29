import bencodepy
import hashlib
import urllib.parse
from controllers import torrent_controller

# Chia file thành các piece
def create_pieces(file_path, piece_length):
    pieces = []
    pieces_arr = []
    pieces_idx = []
    i = 0
    try:
        with open(file_path, "rb") as file:
            # Sử dụng stream của FileStorage để đọc nội dung
            while True:
                # Đọc một đoạn với độ dài = piece_length
                piece = file.read(piece_length)
                if not piece:
                    break
                # Tạo SHA-1 hash cho piece
                piece_hash = hashlib.sha1(piece).digest()
                pieces.append(piece_hash)
                pieces_arr.append((piece, i))  # Lưu phần thực tế của file và chỉ số của nó
                pieces_idx.append(i)
                i += 1
            file_path.seek(0)
    except Exception as e:
        print(f"Error reading file: {e}")

    # Nối tất cả các hash lại thành một chuỗi duy nhất
    return b''.join(pieces), pieces_arr, pieces_idx


# Cấu trúc info chứa thông tin về file
def create_info_hash(file_name, piece_length, pieces, file_length):
    if not isinstance(file_name, str):
        raise ValueError(f"file_name phải là kiểu str, nhưng hiện tại là {type(file_name)}")
    info = {
        "name": file_name,   # Đảm bảo tên file được mã hóa thành dạng byte
        "piece length": piece_length,
        "pieces": b''.join(pieces),  # Nối các hash của các phần lại với nhau
        "length": file_length  # Nếu chỉ có một file
    }

    # Bencode thông tin
    bencoded_info = bencodepy.encode(info)

    # Tạo SHA-1 hash từ bencoded info
    info_hash = hashlib.sha1(bencoded_info).hexdigest()

    return info_hash


# Hàm tạo một liên kết magnet từ info_hash
# "magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678&dn=examplefile.txt"
def create_magnet_link(info_hash):
    # Tạo magnet link chỉ với info_hash
    magnet_link = f"magnet:?xt=urn:btih:{info_hash}"
    return magnet_link


def create_encode_magnet_link(info_hash):
    magnet_link = create_magnet_link(info_hash)
    return urllib.parse.quote(magnet_link)


def create_encode_magnet_link_file(magnet_link):
    encoded_magnet = urllib.parse.quote(magnet_link)
    file_path = f"magnet_link.txt"
    try:
        with open(file_path, "w") as file:
            file.write(encoded_magnet)
        print(f"Magnet link saved to {file_path}")
    except Exception as e:
        print(f"Error saving magnet link to file: {e}")


def create_torrent_file(file_name, piece_length, pieces, file_length, output_file):
    if not isinstance(file_name, str):
        raise ValueError(f"file_name phải là kiểu str, nhưng hiện tại là {type(file_name)}")
    # Dữ liệu torrent cho một file duy nhất
    torrent_data = {
        "info": {
            "name": file_name.encode(),  # Tên của file
            "piece length": piece_length,  # Độ dài từng piece
            "pieces": pieces,  # Các piece đã được tạo SHA-1 hash
            "length": file_length  # Độ dài file (bytes)
        }
    }

    # Bencode the data
    encoded_data = bencodepy.encode(torrent_data)

    # Ghi dữ liệu đã bencode vào file torrent
    with open(output_file, "wb") as f:
        f.write(encoded_data)

    print(f"Torrent file '{output_file}' created successfully!")
