# config.py
import os

# 服务器配置
SERVER_HOST = 'localhost'
SERVER_PORT = 9999

# 加密配置
AES_KEY_SIZE = 256  # 位
CHUNK_SIZE = 64 * 1024  # 64KB，加密块大小
DH_KEY_LENGTH = 2048  # DH密钥长度

# 文件路径配置
CLIENT_OUTPUT_DIR = os.path.join(os.getcwd(), 'client_outputs')
SERVER_OUTPUT_DIR = os.path.join(os.getcwd(), 'server_outputs')
os.makedirs(CLIENT_OUTPUT_DIR, exist_ok=True)
os.makedirs(SERVER_OUTPUT_DIR, exist_ok=True)

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FILE = 'medical_image_encryption.log'