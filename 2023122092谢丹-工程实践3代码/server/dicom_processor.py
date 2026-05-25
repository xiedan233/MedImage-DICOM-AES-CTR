# server/dicom_processor.py
import pydicom
import os
import pandas as pd
import matplotlib.pyplot as plt
import logging
from .crypto import decrypt_data
import config

logger = logging.getLogger(__name__)

def save_dicom_data(metadata, encrypted_data, key):
    """解密并保存DICOM数据"""
    try:
        # 解密数据
        dicom_binary = decrypt_data(encrypted_data, key)
        
        # 创建输出目录
        patient_id = metadata.get('PatientID', 'unknown_patient')
        study_date = metadata.get('StudyDate', 'unknown_date')
        output_dir = os.path.join(
            config.SERVER_OUTPUT_DIR, 
            f"{patient_id}_{study_date}"
        )
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存原始DICOM文件
        filename = metadata.get('FileName', 'decrypted.dcm')
        dicom_path = os.path.join(output_dir, filename)
        with open(dicom_path, 'wb') as f:
            f.write(dicom_binary)
        
        # 解析并保存图像
        try:
            ds = pydicom.dcmread(dicom_path)
            if hasattr(ds, 'PixelData'):
                pixel_array = ds.pixel_array
                if hasattr(ds, 'RescaleSlope') and hasattr(ds, 'RescaleIntercept'):
                    pixel_array = pixel_array * ds.RescaleSlope + ds.RescaleIntercept
                
                image_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.png")
                plt.imsave(image_path, pixel_array, cmap='gray')
                logger.info(f"图像已保存至: {image_path}")
        except Exception as e:
            logger.warning(f"无法解析或保存图像: {str(e)}")
        
        # 保存元数据到CSV
        csv_path = os.path.join(output_dir, "metadata.csv")
        metadata_df = pd.DataFrame([metadata])
        if os.path.exists(csv_path):
            existing_df = pd.read_csv(csv_path)
            metadata_df = pd.concat([existing_df, metadata_df], ignore_index=True)
        
        metadata_df.to_csv(csv_path, index=False)
        logger.info(f"元数据已保存至: {csv_path}")
        
        logger.info(f"DICOM文件已成功保存至: {output_dir}")
        return output_dir
        
    except Exception as e:
        logger.error(f"保存DICOM数据失败: {str(e)}", exc_info=True)
        raise