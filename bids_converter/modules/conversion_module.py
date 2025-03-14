import subprocess
import os

def convert_dicom(dicom_path: str, output_folder: str, dcm2niix_path: str, dcm2niix_options: list) -> bool:
    """
    调用 dcm2niix 工具，将 dicom_path 下的 DICOM 转换为 NIfTI 格式，
    输出到 output_folder。返回转换成功(True)或失败(False)的标志。
    """
    cmd = [dcm2niix_path] + dcm2niix_options + ["-o", output_folder, dicom_path]
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"DICOM 转换失败：{dicom_path} 错误：{e}")
        return False
