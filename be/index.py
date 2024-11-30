from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from dotenv import load_dotenv
from config import system
from routers import router
import os

# Khởi tạo Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Tải biến môi trường
load_dotenv()

# Cấu hình JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "Tc_0Z62MHdAvPgDO")
jwt = JWTManager(app)

# Kiểm tra cấu hình JWT
print(f"JWTManager initialized: {jwt is not None}")
print(f"JWT_SECRET_KEY: {app.config['JWT_SECRET_KEY']}")

# Đăng ký các route
for blueprint in router.get_all_routes():
    print(f"Registering blueprint: {blueprint.name}")
    app.register_blueprint(blueprint)

# Route kiểm tra
@app.route('/test-jwt', methods=['GET'])
def test_jwt():
    token = create_access_token(identity="test_user")
    return jsonify({"token": token}), 200

# Khởi chạy ứng dụng
if __name__ == "__main__":
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    app.run(host=host, port=port, debug=True)



#./venv/Scripts/activate