# client/network.py
import socket
import json
import logging
import config

logger = logging.getLogger(__name__)

def send_data_to_server(host, port, metadata, encrypted_data, dh_nonce):
    """发送加密数据和元数据到服务器"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(30)
            logger.info(f"连接到主服务 {host}:{port}")
            s.connect((host, port))
            
            # 1. 发送DH随机数
            logger.info(f"发送DH nonce: {dh_nonce.hex()}")
            s.sendall(dh_nonce)
            
            # 2. 接收服务器确认
            response = s.recv(10)
            if response != b'NONCE_OK':
                if response == b'NONCE_INVALID':
                    raise Exception("服务器报告无效的DH随机数")
                elif response == b'NONCE_EMPTY':
                    raise Exception("服务器报告收到空的DH随机数")
                else:
                    raise Exception(f"服务器拒绝DH随机数验证: {response}")
            
            # 3. 发送元数据
            metadata_json = json.dumps(metadata).encode('utf-8')
            s.sendall(len(metadata_json).to_bytes(4, 'big'))
            s.sendall(metadata_json)
            
            # 4. 发送加密数据
            s.sendall(len(encrypted_data).to_bytes(8, 'big'))
            
            # 分块发送数据
            total_sent = 0
            chunk_size = 4096
            while total_sent < len(encrypted_data):
                chunk = encrypted_data[total_sent:total_sent + chunk_size]
                s.sendall(chunk)
                total_sent += len(chunk)
            
            # 接收服务器响应
            response = s.recv(1024).decode('utf-8')
            return response
    
    except Exception as e:
        logger.error(f"发送数据失败: {str(e)}")
        raise