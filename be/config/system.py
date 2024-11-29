from flask import Flask, request
from flask_cors import CORS
from controllers import tracker_controller
import sys
import signal

app = Flask(__name__)
CORS(app, supports_credentials=True)   #Cho phép chia sẻ tài nguyên giữa các miền (CORS)

def start_server(routers, my_host, my_port):
    """
    Hàm khởi chạy server Flask và đăng ký các tuyến đường (routes).
    """
    for route in routers:
        app.register_blueprint(route)  # Đăng ký từng blueprint

    try:
        app.run(host=my_host, port=my_port, debug=True)
    except Exception as e:
        print(f"Error when starting the server: {e}")
        sys.exit(1)

def signal_handler(sig, frame):
    """
    Trình xử lý tắt ứng dụng một cách an toàn.
    """
    print("\nShutting down the server...")
    try:
        tracker_controller.set_all_peer_inactive() # Đặt trạng thái của tất cả các peer thành không hoạt động
        print("All peers have been set to inactive.")
    except Exception as e:
        print(f"Error when shutting down the server: {e}")
    finally:
        sys.exit(0)

# Đăng ký các tín hiệu để xử lý tắt server an toàn
signal.signal(signal.SIGINT, signal_handler)  # Xử lý khi nhấn Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Xử lý khi nhận tín hiệu ngừng
