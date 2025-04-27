import pandas as pd
import numpy as np

def clean_data(file_path, output_path):
    print(f"开始清洗数据文件: {file_path}")
    
    # 读取CSV文件，不设置表头
    data = pd.read_csv(file_path, header=None)
    original_rows = len(data)
    print(f"原始数据行数: {original_rows}")
    
    # 获取数据中特征的列数（不包括标签列）
    feature_count = data.shape[1] - 1
    print(f"特征总数: {feature_count}")
    
    # 分离特征和标签
    features = data.iloc[:, :-1]
    labels = data.iloc[:, -1]
    
    # 检查最后一行是否满足条件
    last_row_features = features.iloc[-1].values
    last_row_valid = True
    
    # 检查最后一行28列和62列是否大于6
    if abs(last_row_features[27]) > 6 or abs(last_row_features[61]) > 6:
        last_row_valid = False
        print("警告: 最后一行的28列或62列数据大于6")
    
    # 检查最后一行是否有任何3位数
    if np.any(np.abs(last_row_features) >= 100):
        last_row_valid = False
        print("警告: 最后一行包含3位数")
    
    if not last_row_valid:
        print("错误: 最后一行不满足清洗条件，无法用于替换")
        return
    
    # 保存最后一行用于替换
    last_row = data.iloc[-1].copy()
    
    # 创建过滤条件
    rows_to_remove = []
    
    # 检查每一行
    for i in range(len(features)):
        row = features.iloc[i].values
        
        # 检查28列和62列是否大于6
        if abs(row[27]) > 6 or abs(row[61]) > 6:
            rows_to_remove.append(i)
            continue
        
        # 检查是否有任何3位数
        if np.any(np.abs(row) >= 100):
            rows_to_remove.append(i)
    
    print(f"发现需要删除的行数: {len(rows_to_remove)}")
    
    # 创建新的数据框
    cleaned_data = data.drop(rows_to_remove).reset_index(drop=True)
    
    # 如果删除了最后一行，则不需要保留副本
    if len(data) - 1 in rows_to_remove:
        print("最后一行被删除，不需要特别处理")
    else:
        # 删除最后一行（因为我们有副本）
        cleaned_data = cleaned_data.iloc[:-1]
    
    # 添加替换行
    replacement_count = len(rows_to_remove)
    for _ in range(replacement_count):
        cleaned_data = pd.concat([cleaned_data, pd.DataFrame([last_row])], ignore_index=True)
    
    print(f"清洗后的数据行数: {len(cleaned_data)}")
    print(f"替换了 {replacement_count} 行数据")
    
    # 去重操作
    duplicated_count_before = cleaned_data.duplicated().sum()
    print(f"去重前的重复行数: {duplicated_count_before}")
    
    # 对特征列进行去重，保留标签
    features_only = cleaned_data.iloc[:, :-1]
    labels_only = cleaned_data.iloc[:, -1]
    
    # 找出重复的特征行
    duplicate_indices = features_only.duplicated(keep='first')
    duplicate_count = duplicate_indices.sum()
    
    # 如果有重复行，去除重复行
    if duplicate_count > 0:
        print(f"发现 {duplicate_count} 行特征重复")
        cleaned_data = cleaned_data[~duplicate_indices].reset_index(drop=True)
        print(f"去重后的数据行数: {len(cleaned_data)}")
    else:
        print("没有发现重复的特征")

    # 保存清洗后的数据，设置表头为1到69
    header = [str(i) for i in range(1, 70)]  # 生成表头1到69
    cleaned_data.to_csv(output_path, index=False, header=header)
    print(f"清洗后的数据已保存到: {output_path}")
    
    # 输出标签分布
    label_counts = cleaned_data.iloc[:, -1].value_counts()
    print("标签分布:")
    for label, count in label_counts.items():
        print(f"  {label}: {count} 行")

if __name__ == "__main__":
    input_file = "arknights.csv"
    output_file = "arknights_cleaned.csv"
    clean_data(input_file, output_file)
