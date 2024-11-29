from config import database
import os
from dotenv import load_dotenv
from config import system
from routers import router
from flask import Flask


if __name__ == "__main__":
    # Load các biến môi trường từ file .env
    load_dotenv()
    host = os.getenv('HOST')
    port = os.getenv('PORT')

    system.start_server(router.get_all_routes(), host, port)

