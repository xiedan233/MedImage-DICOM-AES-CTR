# server/network.py
import socket
import threading
import logging
import config

logger = logging.getLogger(__name__)

def start_server(handle_client_func, shared_keys):
    """启动服务器，监听客户端连接"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((config.SERVER_HOST, config.SERVER_PORT))
            s.listen(5)
            
            logger.info(f"服务器监听在 {config.SERVER_HOST}:{config.SERVER_PORT}")
            
            while True:
                client_socket, client_address = s.accept()
                client_thread = threading.Thread(
                    target=handle_client_func,
                    args=(client_socket, client_address, shared_keys),
                    daemon=True
                )
                client_thread.start()
    
    except Exception as e:
        logger.error(f"服务器错误: {str(e)}", exc_info=True)
        raise