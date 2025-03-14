import os
import shutil
import yaml
import pandas as pd
from modules.file_manager import list_subjects, list_sessions, list_scans, find_files
from modules.unzip_module import unzip_file
from modules.mapping_module import generate_mapping, export_mapping
from modules.conversion_module import convert_dicom
from modules.rename_module import move_and_rename_files, rename_fieldmap_files
from modules.json_module import update_json
from modules.events_module import assign_events_to_bids
from modules.models import ConversionEntry

def load_config(config_file: str) -> dict:
    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def ensure_dir(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def clear_directory(directory: str):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory, exist_ok=True)

def main():
    # 加载配置文件
    config = load_config("config/config.yaml")
    global_conf = config["global"]
    raw_data_dir = global_conf["raw_data_dir"]
    dicom_dir = global_conf["dicom_dir"]
    bids_output_dir = global_conf["bids_output_dir"]
    events_from_dir = global_conf["events_from_dir"]
    mapping_file = global_conf["mapping_file"]

    # 确保全局目录存在
    ensure_dir(raw_data_dir)
    ensure_dir(dicom_dir)
    ensure_dir(bids_output_dir)

    # 解压配置
    unzip_conf = config.get("unzip", {"temp_folder": "temp_unzip", "file_extension": ".zip"})
    temp_unzip_folder = unzip_conf["temp_folder"]
    file_extension = unzip_conf["file_extension"]

    # 文件夹映射配置：用于将原始扫描文件夹名称映射到 BIDS 类型（func, fmap, anat）
    folder_mappings = config.get("folder_mappings", {})

    # 映射生成模块配置
    mapping_conf = config.get("mapping", {})

    # 工具配置：dcm2niix 相关参数
    dcm2niix_conf = config["tools"]["dcm2niix"]
    dcm2niix_path = dcm2niix_conf["path"]
    dcm2niix_options = []
    for k, v in dcm2niix_conf.get("options", {}).items():
        if k == "compress":
            dcm2niix_options.extend(["-z", v])
        elif k == "filename_format":
            dcm2niix_options.extend(["-f", v])

    # DICOM 转换模块配置
    conversion_conf = config.get("conversion", {})
    output_temp_dir = conversion_conf.get("output_temp_dir", "temp_nifti")
    ensure_dir(output_temp_dir)

    # -------------------------------
    # # Step 1：解压 raw 数据中的 ZIP 文件到 dicom 目录
    # print("【Step 1】开始解压 DICOM ZIP 文件...")
    # subjects = list_subjects(raw_data_dir)
    # for subject in subjects:
    #     subject_dir = os.path.join(raw_data_dir, subject)
    #     sessions = list_sessions(subject_dir)
    #     for session in sessions:
    #         session_dir = os.path.join(subject_dir, session)
    #         scans = list_scans(session_dir)
    #         for scan in scans:
    #             scan_dir = os.path.join(session_dir, scan)
    #             zip_files = find_files(scan_dir, file_extension)
    #             for zip_file in zip_files:
    #                 # 目标路径：dicom/subject/session/scan
    #                 target_scan_path = os.path.join(dicom_dir, subject, session, scan)
    #                 ensure_dir(target_scan_path)
    #                 temp_folder = os.path.join(target_scan_path, temp_unzip_folder)
    #                 ensure_dir(temp_folder)
    #                 success = unzip_file(zip_file, target_scan_path, temp_folder)
    #                 if success:
    #                     print(f"成功解压 {zip_file} 到 {target_scan_path}")
    #                 else:
    #                     print(f"解压失败：{zip_file}")

    # -------------------------------
    # Step 2：生成映射 Excel 文件
    print("【Step 2】生成映射文件...")
    mapping_df = generate_mapping(raw_data_dir, mapping_conf, folder_mappings)
    # 确保 mapping 文件所在的目录存在（修复保存时目录不存在的问题）
    mapping_output_dir = os.path.dirname(mapping_file)
    if mapping_output_dir and not os.path.exists(mapping_output_dir):
        os.makedirs(mapping_output_dir, exist_ok=True)
    export_mapping(mapping_df, mapping_file)
    print(f"映射文件已生成：{mapping_file}")

    # -------------------------------
    # Step 3：执行 DICOM 转换及文件重命名流程（针对所有扫描任务）
    print("【Step 3】开始对所有扫描任务执行 DICOM 转换流程...")
    # 遍历映射 DataFrame 中的每个扫描条目
    for idx, row in mapping_df.iterrows():
        subject = row["Subject_ID"]
        date_folder = row["Date_Folder_Name"]
        scan_folder = row["Scan_Folder_Name"]
        bids_subj = row["BIDS_Subject_ID"]
        # 此处示例中将 session label 简单定义为 "ses-" + 日期文件夹名，
        # 实际情况可根据排序或其他规则生成，例如：ses-01, ses-02 等。
        session_label = f"ses-{date_folder}"
        
        # 构造 DICOM 路径：dicom/subject/date_folder/scan_folder
        dicom_path = os.path.join(dicom_dir, subject, date_folder, scan_folder)
        if not os.path.exists(dicom_path):
            print(f"警告: DICOM 路径不存在 {dicom_path}")
            continue

        # 根据映射配置中的有效前缀判断扫描类型
        scan_prefix = None
        for prefix in mapping_conf.get("valid_folder_prefixes", []):
            if scan_folder.startswith(prefix):
                scan_prefix = prefix
                break
        if not scan_prefix:
            print(f"警告: 扫描文件夹 {scan_folder} 不符合有效前缀")
            continue

        # 根据 folder_mappings 得到 BIDS 类型（例如 func, fmap, anat）
        bids_type = folder_mappings.get(scan_prefix, "unknown")
        # 构造目标 BIDS 文件夹：BIDS 输出目录 / bids_subj / session_label / bids_type
        target_bids_folder = os.path.join(bids_output_dir, bids_subj, session_label, bids_type)
        ensure_dir(target_bids_folder)

        # 清空转换的临时目录（确保干净）
        clear_directory(output_temp_dir)

        # 调用 DICOM 转换工具，将 dicom_path 中的 DICOM 转换到 output_temp_dir 中
        conversion_success = convert_dicom(dicom_path, output_temp_dir, dcm2niix_path, dcm2niix_options)
        if not conversion_success:
            print(f"转换失败: {dicom_path}")
            continue

        # 根据扫描类型调用对应的文件重命名流程
        if bids_type == "func":
            # 构造功能性扫描的前缀，注意：实际应根据任务信息生成，此处用 unknown 和默认 run 号
            prefix = f"{bids_subj}_{session_label}_task-unknown_run-01_bold"
            nii_path, json_path = move_and_rename_files(output_temp_dir, target_bids_folder, prefix)
            print(f"【功能扫描】转换成功：NIfTI: {nii_path}, JSON: {json_path}")
        elif bids_type == "anat":
            prefix = f"{bids_subj}_{session_label}_T1w"
            nii_path, json_path = move_and_rename_files(output_temp_dir, target_bids_folder, prefix)
            print(f"【T1扫描】转换成功：NIfTI: {nii_path}, JSON: {json_path}")
        elif bids_type == "fmap":
            prefix = f"{bids_subj}_{session_label}_fieldmap"
            fmap_results = rename_fieldmap_files(output_temp_dir, target_bids_folder, prefix)
            print(f"【Fieldmap扫描】转换成功，重命名结果: {fmap_results}")
            # 若 phasediff 文件存在，则更新 JSON 文件（添加默认 EchoTime 等信息）
            if "phasediff" in fmap_results and "json" in fmap_results["phasediff"]:
                default_fields = config.get("json_update", {}).get("default_fields", {}).get("phasediff", {})
                update_json(fmap_results["phasediff"]["json"], default_fields)
                print(f"更新 phasediff JSON 文件：{fmap_results['phasediff']['json']}")
        else:
            print(f"未知扫描类型: {scan_folder}")

    # -------------------------------
    # Step 4：自动分配 events 文件到 BIDS 结构
    print("【Step 4】开始分配 events 文件到 BIDS 结构...")
    assign_events_to_bids(events_from_dir, bids_output_dir)

    print("🚀 所有流程已完成！")

if __name__ == "__main__":
    main()
