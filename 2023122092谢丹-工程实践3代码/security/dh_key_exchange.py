# security/dh_key_exchange.py
import socket
import threading
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
import os
import logging
import config
import time
import hashlib

logger = logging.getLogger(__name__)

# 协议版本控制
PROTOCOL_HEADER = b"DH_INIT_v2.0"
PROTOCOL_REPLY = b"DH_REPLY_v2"

# RFC3526 2048-bit MODP Group
PRIME_2048 = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
    "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
    "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
    "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
    "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
    "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
    "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9"
    "DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
    "15728E5A8AACAA68FFFFFFFFFFFFFFFF", 16
)

def generate_dh_parameters():
    """生成DH参数（使用标准RFC3526 2048-bit MODP Group）"""
    from cryptography.hazmat.primitives.asymmetric.dh import DHParameterNumbers
    return DHParameterNumbers(p=PRIME_2048, g=2).parameters(default_backend())

DH_PARAMETERS = generate_dh_parameters()

class ClientDH:
    def __init__(self):
        self.parameters = DH_PARAMETERS
        self.private_key = self.parameters.generate_private_key()
        self.public_key = self.private_key.public_key()
        self.nonce = None  # 将由服务器生成
        self.shared_key = None
    
    def _validate_public_key(self, public_key):
        """增强的公钥验证"""
        if not isinstance(public_key, dh.DHPublicKey):
            raise ValueError("Invalid public key type")
        pub_num = public_key.public_numbers()
        p = self.parameters.parameter_numbers().p
        if not (0 <= pub_num.y <= p):
            raise ValueError(f"Public key value out of range (0 <= y <= {p})")

    def perform_key_exchange(self, host, port, max_retries=3):
        """带重试机制的密钥交换（增强版）"""
        for attempt in range(max_retries):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(15)
                    logger.info(f"尝试连接到 {host}:{port+1}")
                    s.connect((host, port + 1))
                    
                    # 发送协议头
                    s.sendall(PROTOCOL_HEADER)
                    
                    # 发送公钥
                    pub_key = self.public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                    if not pub_key.startswith(b'-----BEGIN'):
                        pub_key = b'-----BEGIN PUBLIC KEY-----\n' + pub_key + b'\n-----END PUBLIC KEY-----\n'
                    
                    # 发送长度和校验和
                    key_len = len(pub_key)
                    checksum = hashlib.sha256(pub_key).digest()[:2]
                    s.sendall(key_len.to_bytes(4, 'big'))
                    s.sendall(checksum)
                    s.sendall(pub_key)
                    
                    # 接收响应
                    reply = s.recv(len(PROTOCOL_REPLY))
                    if reply != PROTOCOL_REPLY:
                        raise ValueError(f"Invalid reply header: {reply}")
                    
                    # 接收服务器公钥
                    key_len = int.from_bytes(s.recv(4), 'big')
                    checksum = s.recv(2)
                    server_key = s.recv(key_len)
                    
                    if hashlib.sha256(server_key).digest()[:2] != checksum:
                        raise ValueError("服务器公钥校验和错误")
                    
                    # 加载公钥
                    try:
                        server_pub_key = serialization.load_pem_public_key(
                            server_key,
                            backend=default_backend()
                        )
                    except ValueError:
                        server_key = server_key.replace(b'PUBLIC KEY', b'DH PUBLIC KEY')
                        server_pub_key = serialization.load_pem_public_key(
                            server_key,
                            backend=default_backend()
                        )
                    
                    self._validate_public_key(server_pub_key)
                    
                    # 计算共享密钥
                    shared_secret = self.private_key.exchange(server_pub_key)
                    self.shared_key = HKDF(
                        algorithm=hashes.SHA256(),
                        length=config.AES_KEY_SIZE // 8,
                        salt=None,
                        info=b'medical-image-exchange',
                        backend=default_backend()
                    ).derive(shared_secret)
                    
                    # 接收服务器生成的nonce
                    self.nonce = s.recv(16)
                    logger.info(f"DH密钥交换成功，获取nonce: {self.nonce.hex()}")
                    return self.shared_key
                    
            except Exception as e:
                logger.error(f"尝试 {attempt + 1} 失败: {str(e)}", exc_info=True)
                if attempt == max_retries - 1:
                    raise
                time.sleep(1)

class ServerDH:
    def __init__(self):
        self.parameters = DH_PARAMETERS
        self.shared_keys = {}
    
    def _validate_public_key(self, public_key):
        """增强的公钥验证"""
        if not isinstance(public_key, dh.DHPublicKey):
            raise ValueError("Invalid public key type")
        pub_num = public_key.public_numbers()
        p = self.parameters.parameter_numbers().p
        if not (0 <= pub_num.y <= p):
            raise ValueError(f"Public key value out of range (0 <= y <= {p})")

    def start(self, shared_keys_dict):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((config.SERVER_HOST, config.SERVER_PORT + 1))
                s.listen(5)
                logger.info(f"DH服务监听端口: {config.SERVER_PORT + 1}")
                
                while True:
                    client_socket, addr = s.accept()
                    threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, addr, shared_keys_dict),
                        daemon=True
                    ).start()
        except Exception as e:
            logger.error(f"DH服务器错误: {str(e)}", exc_info=True)
            raise
    
    def _handle_client(self, client_socket, client_address, shared_keys_dict):
        try:
            client_socket.settimeout(30)
            logger.info(f"处理来自 {client_address} 的DH请求")
            
            # 验证协议头
            init_msg = client_socket.recv(len(PROTOCOL_HEADER))
            if init_msg != PROTOCOL_HEADER:
                raise ValueError(f"协议不匹配，收到: {init_msg}，期望: {PROTOCOL_HEADER}")
            
            # 接收公钥
            key_len = int.from_bytes(client_socket.recv(4), 'big')
            checksum = client_socket.recv(2)
            client_key_bytes = client_socket.recv(key_len)
            
            if hashlib.sha256(client_key_bytes).digest()[:2] != checksum:
                raise ValueError("客户端公钥校验和错误")
            
            # 修复PEM格式
            if not client_key_bytes.startswith(b'-----BEGIN'):
                client_key_bytes = b'-----BEGIN PUBLIC KEY-----\n' + client_key_bytes
            if not client_key_bytes.endswith(b'-----END PUBLIC KEY-----'):
                if b'-----END' in client_key_bytes:
                    client_key_bytes = client_key_bytes.split(b'-----END')[0] + b'-----END PUBLIC KEY-----'
                else:
                    client_key_bytes = client_key_bytes + b'\n-----END PUBLIC KEY-----'
            
            # 加载公钥
            try:
                client_pub_key = serialization.load_pem_public_key(
                    client_key_bytes,
                    backend=default_backend()
                )
            except ValueError:
                client_key_bytes = client_key_bytes.replace(b'PUBLIC KEY', b'DH PUBLIC KEY')
                client_pub_key = serialization.load_pem_public_key(
                    client_key_bytes,
                    backend=default_backend()
                )
            
            self._validate_public_key(client_pub_key)
            
            # 生成服务器密钥
            server_priv_key = self.parameters.generate_private_key()
            server_pub_key = server_priv_key.public_key()
            server_key_bytes = server_pub_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # 发送响应
            logger.debug(f"服务器发送协议响应: {PROTOCOL_REPLY}")
            client_socket.sendall(PROTOCOL_REPLY)
            
            # 发送服务器公钥
            key_len = len(server_key_bytes)
            checksum = hashlib.sha256(server_key_bytes).digest()[:2]
            client_socket.sendall(key_len.to_bytes(4, 'big'))
            client_socket.sendall(checksum)
            client_socket.sendall(server_key_bytes)
            
            # 计算共享密钥
            shared_secret = server_priv_key.exchange(client_pub_key)
            derived_key = HKDF(
                algorithm=hashes.SHA256(),
                length=config.AES_KEY_SIZE // 8,
                salt=None,
                info=b'medical-image-exchange',
                backend=default_backend()
            ).derive(shared_secret)
            
            # 生成并存储nonce
            nonce = os.urandom(16)
            shared_keys_dict[nonce] = derived_key
            logger.info(f"与 {client_address} 建立密钥成功，nonce: {nonce.hex()}")
            
            # 发送nonce给客户端
            client_socket.sendall(nonce)
            
        except Exception as e:
            logger.error(f"处理客户端失败: {str(e)}", exc_info=True)
        finally:
            try:
                client_socket.close()
            except:
                pass