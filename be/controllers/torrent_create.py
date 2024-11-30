import bencodepy
import hashlib
import urllib.parse
from controllers import torrent_controller
# Chia file thành các piece
def generate_pieces(file_path, piece_length):
    pieces = []
    pieces_arr = []
    pieces_idx = []
    i = 0
    try:
        # Open file in binary mode
        with open(file_path, 'rb') as file:
            while True:
                piece = file.read(piece_length)  # Read a chunk of `piece_length`
                if not piece:
                    break
                piece_hash = hashlib.sha1(piece).digest()  # Compute SHA-1 hash
                pieces += piece_hash  # Append hash to the binary string
                pieces_arr.append((piece, i))  # Optional: keep the piece data
                pieces_idx.append(i)
                i += 1

    except Exception as e:
        print(f"Error reading file: {e}")

    return pieces, pieces_arr, pieces_idx
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

def create_torrent_file(file_name, piece_length, pieces, file_length, output_file):
    # Torrent metadata for a single file
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
    
    # Write the encoded data to a .torrent file
    with open(output_file, "wb") as f:
        f.write(encoded_data)
    
    print(f"Torrent file '{output_file}' created successfully!")



