# client/dicom_processor.py
import pydicom
import os
import logging
import config
from pydicom.pixel_data_handlers.util import apply_modality_lut  # 统一使用旧版导入方式
import warnings

logger = logging.getLogger(__name__)

def parse_dicom(filepath):
    """兼容新旧版pydicom的DICOM解析器"""
    try:
        ds = pydicom.dcmread(filepath, force=True)
        pixel_array = None

        if hasattr(ds, 'PixelData'):
            try:
                pixel_array = ds.pixel_array
                # 统一使用旧版处理方式
                if 'RescaleSlope' in ds or 'RescaleIntercept' in ds:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        pixel_array = apply_modality_lut(pixel_array, ds)
            except Exception as e:
                logger.warning(
                    f"像素处理失败 | 文件: {os.path.basename(filepath)}\n"
                    f"传输语法: {ds.get('TransferSyntaxUID', 'N/A')}\n"
                    f"错误详情: {str(e)}"
                )

        metadata = {
            "FileName": os.path.basename(filepath),
            "PatientName": str(ds.get("PatientName", "N/A")),
            "PatientID": str(ds.get("PatientID", "N/A")),
            "StudyDate": str(ds.get("StudyDate", "N/A")),
            "Modality": str(ds.get("Modality", "N/A")),
            "Rows": int(ds.get("Rows", 0)),
            "Columns": int(ds.get("Columns", 0)),
            "BitsStored": int(ds.get("BitsStored", 0)),
            "TransferSyntaxUID": str(ds.get("TransferSyntaxUID", "N/A")),
            "SOPInstanceUID": str(ds.get("SOPInstanceUID", "N/A"))
        }

        return metadata, pixel_array, ds

    except Exception as e:
        logger.error(f"DICOM解析严重错误: {str(e)}", exc_info=True)
        raise

def process_dicom_file(filepath):
    """处理流程保持不变"""
    try:
        metadata, pixel_array, ds = parse_dicom(filepath)
        with open(filepath, 'rb') as f:
            dicom_binary = f.read()
        return metadata, pixel_array, dicom_binary
    except Exception as e:
        logger.error(f"文件处理失败: {str(e)}", exc_info=True)
        raise