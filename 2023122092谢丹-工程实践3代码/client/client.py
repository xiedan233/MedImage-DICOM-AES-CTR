# client/client.py
import os
import time
import logging
from client.dicom_processor import process_dicom_file
from client.crypto import encrypt_file
from client.network import send_data_to_server
from security.dh_key_exchange import ClientDH
import config

logger = logging.getLogger(__name__)

def run_client(dicom_file_path, max_retries=3):
    """带重试机制的DICOM文件加密传输客户端
    
    Args:
        dicom_file_path (str): DICOM文件路径
        max_retries (int): 最大重试次数，默认为3
        
    Returns:
        tuple: (success: bool, message: str) 传输状态和消息
    """
    try:
        # 1. 验证文件
        logger.info(f"开始处理DICOM文件: {dicom_file_path}")
        if not os.path.isfile(dicom_file_path):
            raise FileNotFoundError(f"文件不存在: {dicom_file_path}")
        
        # 2. 处理DICOM文件
        metadata, _, dicom_binary = process_dicom_file(dicom_file_path)
        
        # 3. DH密钥交换（带重试机制）
        shared_key, dh_nonce = perform_dh_key_exchange(max_retries)
        if not shared_key:
            raise RuntimeError("DH密钥交换失败")
        
        logger.info(f"DH密钥交换成功，nonce: {dh_nonce.hex()}")

        # 4. 加密数据
        logger.info("开始加密数据")
        encrypted_data = encrypt_file(dicom_binary, shared_key)
        logger.info(f"加密完成，数据大小: {len(encrypted_data)} bytes")

        # 5. 发送数据
        logger.info("开始发送数据到服务器")
        response = send_data_to_server(
            host=config.SERVER_HOST,
            port=config.SERVER_PORT,
            metadata=metadata,
            encrypted_data=encrypted_data,
            dh_nonce=dh_nonce
        )
        
        if response != 'RECEIVED_OK':
            raise RuntimeError(f"服务器响应异常: {response}")
            
        logger.info("文件传输成功")
        return True, "DICOM文件已成功发送到服务器"

    except Exception as e:
        logger.error(f"客户端运行失败: {str(e)}", exc_info=True)
        return False, f"传输失败: {str(e)}"

def perform_dh_key_exchange(max_retries):
    """执行DH密钥交换（带重试机制）"""
    last_error = None
    for attempt in range(max_retries):
        try:
            logger.info(f"尝试DH密钥交换 ({attempt + 1}/{max_retries})")
            client_dh = ClientDH()
            shared_key = client_dh.perform_key_exchange(
                config.SERVER_HOST,
                config.SERVER_PORT
            )
            return shared_key, client_dh.nonce
            
        except ConnectionResetError as e:
            last_error = e
            logger.error(f"连接被重置: {str(e)}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # 指数退避
            
        except Exception as e:
            last_error = e
            logger.error(f"DH交换失败: {str(e)}", exc_info=True)
            if attempt == max_retries - 1:
                raise
            time.sleep(1)
    
    return None, None

# 兼容原有直接执行方式
if __name__ == "__main__":
    import sys
    from utils.logging import setup_logging
    
    if len(sys.argv) != 2:
        print("用法: python client.py <DICOM文件路径>")
        sys.exit(1)
        
    setup_logging()
    success, message = run_client(sys.argv[1])
    print(message)
    sys.exit(0 if success else 1)