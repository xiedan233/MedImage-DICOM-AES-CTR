from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import logging

logger = logging.getLogger(__name__)

def encrypt_file(data, key):
    """使用AES-CTR模式加密文件数据"""
    try:
        # 生成随机nonce (16字节，因为AES-CTR在cryptography中通常用16字节nonce)
        nonce = os.urandom(16)
        
        # 创建加密器
        cipher = Cipher(
            algorithms.AES(key),
            modes.CTR(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # 加密数据
        encrypted_data = encryptor.update(data) + encryptor.finalize()
        
        # 返回nonce和加密数据
        return nonce + encrypted_data
    
    except Exception as e:
        logger.error(f"加密失败: {str(e)}")
        raise