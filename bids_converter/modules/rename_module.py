import os
import shutil
from typing import Tuple, Dict

def split_nii_gz(filename: str) -> Tuple[str, str]:
    """
    正确拆分 .nii.gz 或 .json 文件名，返回（base, ext）。
    """
    if filename.endswith(".nii.gz"):
        return filename[:-7], ".nii.gz"
    elif filename.endswith(".nii.json"):
        return filename[:-9], ".json"
    else:
        base, ext = os.path.splitext(filename)
        return base, ext

def move_and_rename_files(temp_dir: str, bids_dir: str, prefix: str) -> Tuple[str, str]:
    """
    从 temp_dir 中查找 .nii.gz 和 .json 文件，重命名后移动到 bids_dir，
    新文件名为 <prefix> + 扩展名。
    返回 (nii_path, json_path)。
    """
    os.makedirs(bids_dir, exist_ok=True)
    nii_path_final = None
    json_path_final = None

    for fname in os.listdir(temp_dir):
        fpath = os.path.join(temp_dir, fname)
        if not os.path.isfile(fpath):
            continue
        if fname.endswith(".nii.gz") or fname.endswith(".json"):
            base, ext = split_nii_gz(fname)
            new_fname = prefix + ext
            dest_path = os.path.join(bids_dir, new_fname)
            shutil.move(fpath, dest_path)
            if ext == ".nii.gz":
                nii_path_final = dest_path
            elif ext == ".json":
                json_path_final = dest_path
    return nii_path_final, json_path_final

def rename_fieldmap_files(temp_dir: str, bids_dir: str, prefix: str) -> Dict:
    """
    针对 Fieldmap，将 temp_dir 中的文件重命名并移动到 bids_dir，
    根据文件名中的关键词判断不同的映射类型（phasediff, magnitude1, magnitude2）。
    返回一个字典，记录各类型文件的 nii 和 json 路径。
    """
    os.makedirs(bids_dir, exist_ok=True)
    results = {}
    for fname in os.listdir(temp_dir):
        fpath = os.path.join(temp_dir, fname)
        if not os.path.isfile(fpath):
            continue
        if fname.endswith(".nii.gz") or fname.endswith(".json"):
            base, ext = split_nii_gz(fname)
            lname = base.lower()
            if "ph" in lname or "phase" in lname:
                key = "phasediff"
                new_stem = prefix.replace("_fieldmap", "_phasediff")
            elif "e1" in lname:
                key = "magnitude1"
                new_stem = prefix.replace("_fieldmap", "_magnitude1")
            elif "e2" in lname:
                key = "magnitude2"
                new_stem = prefix.replace("_fieldmap", "_magnitude2")
            else:
                key = "fieldmap"
                new_stem = prefix
            new_fname = new_stem + ext
            dst = os.path.join(bids_dir, new_fname)
            shutil.move(fpath, dst)
            if key not in results:
                results[key] = {}
            if ext == ".nii.gz":
                results[key]["nii"] = dst
            elif ext == ".json":
                results[key]["json"] = dst
    return results
