import json
import os

def update_json(json_path: str, extra_fields: dict) -> None:
    """
    更新 json 文件，将 extra_fields 中的键值对写入 json 文件中
    """
    if not os.path.isfile(json_path):
        return
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取 {json_path} 失败：{e}")
        data = {}
    data.update(extra_fields)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
