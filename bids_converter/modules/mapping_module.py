import os
import pandas as pd
from typing import Dict
import re

def generate_mapping(raw_data_dir: str, mapping_config: Dict, folder_mappings: Dict) -> pd.DataFrame:
    """
    遍历原始数据目录，根据 mapping_config 生成映射信息 DataFrame。
    提取受试者、日期（session）和 scan 文件夹，并根据 valid_folder_prefixes 过滤。
    同时从文件名中提取简单的时间信息（例如从文件名中用正则查找14位数字）。
    """
    data = []
    valid_prefixes = mapping_config.get("valid_folder_prefixes", [])
    subject_mapping = mapping_config.get("subject_mapping", {})
    task_mapping = mapping_config.get("task_mapping", {})

    for subject in os.listdir(raw_data_dir):
        subject_path = os.path.join(raw_data_dir, subject)
        if os.path.isdir(subject_path):
            # 日期文件夹作为 session，这里假设文件夹名代表日期
            for date_folder in os.listdir(subject_path):
                date_folder_path = os.path.join(subject_path, date_folder)
                if os.path.isdir(date_folder_path):
                    for scan_folder in os.listdir(date_folder_path):
                        scan_folder_path = os.path.join(date_folder_path, scan_folder)
                        if os.path.isdir(scan_folder_path):
                            # 只处理 valid_prefixes 开头的文件夹
                            if not any(scan_folder.startswith(prefix) for prefix in valid_prefixes):
                                continue
                            # 尝试在该文件夹下寻找一个 dicom 文件，并提取时间信息
                            time_info = extract_time_info_from_folder(scan_folder_path)
                            
                            # 根据 subject_mapping 获取 BIDS id 和实验编号
                            if subject in subject_mapping:
                                bids_id = subject_mapping[subject]["bids_id"]
                                experiment_id = subject_mapping[subject]["experiment_id"]
                            else:
                                bids_id = ""
                                experiment_id = ""

                            # 构造映射记录
                            data.append({
                                "Subject_ID": subject,
                                "Date_Folder_Name": date_folder,
                                "Scan_Folder_Name": scan_folder,
                                "Time_Info": time_info,
                                "BIDS_Subject_ID": bids_id,
                                "Experiment_ID": experiment_id,
                            })
    df = pd.DataFrame(data)
    return df

def extract_time_info_from_folder(folder: str) -> str:
    """
    在 folder 中查找文件名中匹配 14 位连续数字的字符串，作为时间信息返回。
    若未找到，返回空字符串。
    """
    for fname in os.listdir(folder):
        match = re.search(r'\d{14}', fname)
        if match:
            return match.group(0)
    return ""
    
def export_mapping(mapping_df: pd.DataFrame, output_file: str) -> None:
    """将 mapping_df 导出为 Excel 文件"""
    mapping_df.to_excel(output_file, index=False)
