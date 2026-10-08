# main.py
import os
import argparse
from client.client import run_client
from server.server import run_server
from client.gui import run_gui  # 新增导入
from utils.logging import setup_logging

def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(description='医学影像加密传输系统')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # 客户端命令
    client_parser = subparsers.add_parser('client', help='运行客户端')
    client_parser.add_argument('--gui', action='store_true', help='启用图形界面')
    client_parser.add_argument('dicom_file', nargs='?', help='DICOM文件路径')
    
    # 服务器命令
    server_parser = subparsers.add_parser('server', help='运行服务器')
    
    args = parser.parse_args()
    
    if args.command == 'client':
        if args.gui:
            run_gui()  # 启动GUI模式
        else:
            if not args.dicom_file:
                print("错误: 需要指定DICOM文件路径")
                return
            run_client(args.dicom_file)
    elif args.command == 'server':
        run_server()

if __name__ == "__main__":
    main()