# client/gui.py
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                             QMessageBox, QProgressBar)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import pydicom
import numpy as np
from .client import run_client
import logging

logger = logging.getLogger(__name__)

class SendThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            for progress in range(0, 101, 10):
                self.progress_signal.emit(progress)
                self.msleep(100)
            
            success, message = run_client(self.file_path)
            self.finished_signal.emit(success, message)
        except Exception as e:
            logger.error(f"发送失败: {str(e)}")
            self.finished_signal.emit(False, f"错误: {str(e)}")

class DicomViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.current_file = None

    def setup_ui(self):
        self.setWindowTitle("DICOM加密传输系统")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 图像显示区域
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)
        
        # 文件信息
        self.info_label = QLabel("未选择文件")
        layout.addWidget(self.info_label)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        self.select_btn = QPushButton("选择DICOM文件")
        self.select_btn.clicked.connect(self.select_file)
        btn_layout.addWidget(self.select_btn)
        
        self.send_btn = QPushButton("发送文件")
        self.send_btn.setEnabled(False)
        self.send_btn.clicked.connect(self.send_file)
        btn_layout.addWidget(self.send_btn)
        layout.addLayout(btn_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择DICOM文件", "", "DICOM文件 (*.dcm)"
        )
        if file_path:
            self.current_file = file_path
            self.display_dicom(file_path)
            self.send_btn.setEnabled(True)

    def display_dicom(self, file_path):
        try:
            ds = pydicom.dcmread(file_path, force=True)
            if hasattr(ds, 'PixelData'):
                pixel_array = ds.pixel_array
                if 'RescaleSlope' in ds and 'RescaleIntercept' in ds:
                    pixel_array = pixel_array * ds.RescaleSlope + ds.RescaleIntercept
                
                # 转换为8位灰度（0-255）
                pixel_array = ((pixel_array - pixel_array.min()) / 
                              (pixel_array.max() - pixel_array.min()) * 255).astype(np.uint8)
                
                # 直接使用 QImage 转换和缩放
                height, width = pixel_array.shape
                
                # 计算缩放比例（限制最大尺寸为600x600）
                max_size = 600
                scale = min(max_size / width, max_size / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                
                # 创建 QImage 并缩放
                qimage = QImage(pixel_array.data, width, height, width, QImage.Format_Grayscale8)
                scaled_pixmap = QPixmap.fromImage(qimage).scaled(
                    new_width, new_height, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation  # 高质量缩放
                )
                
                # 显示图像
                self.image_label.setPixmap(scaled_pixmap)
                
                # 显示元数据
                info = f"患者: {ds.get('PatientName', 'N/A')}\n"
                info += f"模态: {ds.get('Modality', 'N/A')} 尺寸: {width}x{height} (缩放后: {new_width}x{new_height})"
                self.info_label.setText(info)
        except Exception as e:
            self.image_label.setText(f"无法显示图像: {str(e)}")

    def send_file(self):
        if not self.current_file:
            return
            
        self.select_btn.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        
        self.thread = SendThread(self.current_file)
        self.thread.progress_signal.connect(self.progress_bar.setValue)
        self.thread.finished_signal.connect(self.on_send_finished)
        self.thread.start()

    def on_send_finished(self, success, message):
        self.select_btn.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.information(self, "成功" if success else "错误", message)

def run_gui():
    app = QApplication(sys.argv)
    viewer = DicomViewer()
    viewer.show()
    sys.exit(app.exec_())