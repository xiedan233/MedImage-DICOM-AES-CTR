from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger(__name__)

def decrypt_data(encrypted_data, key):
    """使用AES-CTR模式解密数据"""
    try:
        # 分离nonce和加密数据 (注意nonce现在是16字节)
        nonce = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        # 创建解密器
        cipher = Cipher(
            algorithms.AES(key),
            modes.CTR(nonce),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # 解密数据
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        return decrypted_data
    
    except Exception as e:
        logger.error(f"解密失败: {str(e)}")
        raise