# server/server.py
import socket
import threading
import logging
import json
import config
from .network import start_server
from .dicom_processor import save_dicom_data
from security.dh_key_exchange import ServerDH

logger = logging.getLogger(__name__)

def handle_client(client_socket, client_address, shared_keys):
    """处理客户端连接（增强版）"""
    try:
        logger.info(f"接受来自 {client_address} 的连接")
        
        # 1. 接收并验证DH随机数
        try:
            dh_nonce = client_socket.recv(16)
            if not dh_nonce:
                logger.warning(f"收到空的DH随机数 from {client_address}")
                client_socket.sendall(b'NONCE_EMPTY')
                return
                
            if dh_nonce not in shared_keys:
                logger.warning(f"无效的DH随机数 from {client_address}, 现有keys: {list(shared_keys.keys())}")
                client_socket.sendall(b'NONCE_INVALID')
                return
                
            shared_key = shared_keys.pop(dh_nonce)
            logger.info(f"验证成功，使用nonce: {dh_nonce.hex()}")
            client_socket.sendall(b'NONCE_OK')
            
        except socket.timeout:
            logger.error(f"接收DH随机数超时 from {client_address}")
            return
        except Exception as e:
            logger.error(f"验证DH随机数失败: {str(e)}")
            client_socket.sendall(b'NONCE_ERROR')
            return

        # 2. 接收元数据
        try:
            metadata_length = int.from_bytes(client_socket.recv(4), 'big')
            metadata_json = client_socket.recv(metadata_length).decode('utf-8')
            metadata = json.loads(metadata_json)
        except Exception as e:
            logger.error(f"元数据解析失败: {str(e)}")
            client_socket.sendall(b'METADATA_ERROR')
            return

        # 3. 接收加密数据
        try:
            data_length = int.from_bytes(client_socket.recv(8), 'big')
            received = 0
            encrypted_data = bytearray()
            while received < data_length:
                chunk = client_socket.recv(min(4096, data_length - received))
                if not chunk:
                    break
                encrypted_data.extend(chunk)
                received += len(chunk)
        except Exception as e:
            logger.error(f"数据接收失败: {str(e)}")
            client_socket.sendall(b'DATA_ERROR')
            return

        # 4. 处理数据
        try:
            output_dir = save_dicom_data(metadata, bytes(encrypted_data), shared_key)
            logger.info(f"成功保存到 {output_dir}")
            client_socket.sendall(b'RECEIVED_OK')
        except Exception as e:
            logger.error(f"数据处理失败: {str(e)}", exc_info=True)
            client_socket.sendall(b'PROCESS_ERROR')

    except Exception as e:
        logger.error(f"客户端处理异常: {str(e)}", exc_info=True)
    finally:
        try:
            client_socket.close()
        except:
            pass
        logger.info(f"关闭 {client_address} 的连接")

def run_server():
    """启动服务器（增强版）"""
    try:
        shared_keys = {}
        
        # 启动DH密钥交换服务器
        dh_thread = threading.Thread(
            target=ServerDH().start,
            args=(shared_keys,),
            daemon=True
        )
        dh_thread.start()

        # 启动主服务
        logger.info(f"主服务启动，监听 {config.SERVER_HOST}:{config.SERVER_PORT}")
        logger.info(f"DH服务端口: {config.SERVER_PORT + 1}")
        start_server(handle_client, shared_keys)

    except KeyboardInterrupt:
        logger.info("服务器正常关闭")
    except Exception as e:
        logger.error(f"服务器启动失败: {str(e)}", exc_info=True)
        raise