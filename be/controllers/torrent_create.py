import bencodepy
import hashlib
import urllib.parse
from controllers import torrent_controller
from werkzeug.datastructures import FileStorage
# Chia file thành các piece
def generate_pieces(file_path: FileStorage, piece_length):
    pieces = []
    pieces_arr = []
    pieces_idx = []
    i = 0
    try:
        # with open(file_path, 'rb') as file:
            while True:
                piece = file_path.stream.read(piece_length)  # Read a chunk of `piece_length`
                if not piece:
                    break
                piece_hash = hashlib.sha1(piece).digest()  # Compute SHA-1 hash
                pieces.append(piece_hash)  # Append hash to the binary string
                pieces_arr.append((piece, i))  # Save the actual piece and index
                pieces_idx.append(i)  # Save only the index
                i += 1
            file_path.stream.seek(0)
    except Exception as e:
        print(f"Error reading file: {e}")

    return b''.join(pieces), pieces_arr, pieces_idx

    # # Nếu cần, có thể quay lại đầu file (nếu file_path là một file thật)
    # file_path.seek(0)

    # # Nối tất cả các hash lại thành một chuỗi duy nhất
    # return b''.join(pieces), pieces_arr, pieces_idx

# Cấu trúc info chứa thông tin về file
def generate_info_hash(file_name, piece_length, pieces, file_length):
    info = {
        "name": file_name,
        "piece length": piece_length,
        "pieces": pieces,
        "length": file_length  # Nếu chỉ có một file
    }
    
    # Bencode thông tin
    bencoded_info = bencodepy.encode(info)
    
    # Tạo SHA-1 hash từ bencoded info
    info_hash = hashlib.sha1(bencoded_info).hexdigest()
    
    return info_hash

# Function to parse a magnet URI
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

def create_torrent_file(file_storage: FileStorage, file_name, piece_length, pieces, file_length, output_file):
    torrent_data = {
        "info": {
            "name": file_name,
            "piece length": piece_length,
            "pieces": pieces,
            "length": file_length
        }
    }
    try:
        # Bencode dữ liệu và ghi vào tệp đầu ra
        encoded_data = bencodepy.encode(torrent_data)
        with open(output_file, "wb") as f:
            f.write(encoded_data)
        print(f"Torrent file created: {output_file}")
    except Exception as e:
        print(f"Error creating torrent file: {e}")



