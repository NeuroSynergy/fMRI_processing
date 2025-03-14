import os
from typing import List

def list_subjects(raw_data_dir: str) -> List[str]:
    """返回 raw_data_dir 下所有的受试者目录"""
    return [d for d in os.listdir(raw_data_dir) if os.path.isdir(os.path.join(raw_data_dir, d))]

def list_sessions(subject_dir: str) -> List[str]:
    """返回指定 subject_dir 下的所有 session 目录"""
    return [d for d in os.listdir(subject_dir) if os.path.isdir(os.path.join(subject_dir, d))]

def list_scans(session_dir: str) -> List[str]:
    """返回指定 session_dir 下的所有 scan 目录"""
    return [d for d in os.listdir(session_dir) if os.path.isdir(os.path.join(session_dir, d))]

def find_files(folder: str, extension: str) -> List[str]:
    """在 folder 中查找以 extension 结尾的文件"""
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(extension)]
