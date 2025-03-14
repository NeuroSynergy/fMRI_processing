import zipfile
import os
import shutil

def unzip_file(zip_path: str, dest_folder: str, temp_folder: str) -> bool:
    """
    将 zip_path 解压到临时目录 temp_folder，
    然后将其中的所有文件移动到 dest_folder，并删除 temp_folder
    """
    os.makedirs(temp_folder, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_folder)
        os.makedirs(dest_folder, exist_ok=True)
        # 移动所有文件
        for root, _, files in os.walk(temp_folder):
            for file in files:
                src = os.path.join(root, file)
                dst = os.path.join(dest_folder, file)
                shutil.move(src, dst)
        shutil.rmtree(temp_folder)
        return True
    except Exception as e:
        print(f"解压文件 {zip_path} 时发生错误：{e}")
        return False
