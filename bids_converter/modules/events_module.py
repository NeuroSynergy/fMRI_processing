import os
import shutil
import re
import glob

def assign_events_to_bids(events_dir, bids_output_dir):
    """
    将 events 文件根据命名规则自动分配到 BIDS 结构中。
    """
    if not os.path.exists(events_dir):
        print(f"⚠️ 事件目录不存在: {events_dir}")
        return
    
    # 正则表达式匹配文件名 (支持更灵活的命名)
    pattern = re.compile(r'sub-(\d+)_ses-(\d+)_task-(\w+)_run-(\d+)_events\.tsv')

    event_files = glob.glob(os.path.join(events_dir, '*.tsv'))
    if not event_files:
        print(f"⚠️ 未在 {events_dir} 中找到 events 文件")
        return
    
    for file in event_files:
        filename = os.path.basename(file)
        match = pattern.match(filename)

        if not match:
            print(f"⚠️ 文件名不符合 BIDS 格式: {filename}")
            continue
        
        # 提取 BIDS 命名规则中的关键信息
        subject = f"sub-{match.group(1)}"
        session = f"ses-{match.group(2)}"
        task = match.group(3)
        run = f"run-{int(match.group(4)):02d}"
        
        # 目标路径：BIDS 结构中的 func 文件夹
        target_dir = os.path.join(bids_output_dir, subject, session, 'func')
        os.makedirs(target_dir, exist_ok=True)  # 确保路径存在
        
        target_file = os.path.join(target_dir, filename)

        try:
            shutil.move(file, target_file)
            print(f"✅ 文件已移动到: {target_file}")
        except Exception as e:
            print(f"❌ 文件移动失败: {file} -> {target_file}, 错误: {e}")

    print("🚀 所有 events 文件已成功移动到 BIDS 结构中！")

# 示例调用
if __name__ == "__main__":
    events_dir = "./events_new"
    bids_output_dir = "./BIDS_data_test"
    assign_events_to_bids(events_dir, bids_output_dir)
