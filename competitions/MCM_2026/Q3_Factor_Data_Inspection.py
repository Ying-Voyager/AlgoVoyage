import pandas as pd
import numpy as np

# 设置显示选项，确保长列表不被折叠
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)


def inspect_data():
    # 你的本地绝对路径 (使用 r'' 防止反斜杠转义)
    file_path = '2026_MCM_Problem_C_Data.csv'

    print(f"正在读取文件: {file_path} ...")

    try:
        # 优先尝试默认编码，如果报错则尝试 ISO-8859-1 (处理特殊字符)
        try:
            df = pd.read_csv(file_path)
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='ISO-8859-1')

        print("✅ 读取成功！")
        print(f"数据总行数: {len(df)}")
    except FileNotFoundError:
        print("❌ 错误: 找不到文件。请确认路径是否完全正确。")
        return
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")
        return

    # 1. 行业标签 (最重要，需要你看这个列表来决定怎么合并)
    print("\n" + "=" * 60)
    print("1. CELEBRITY INDUSTRY (原始标签列表)")
    print("=" * 60)
    if 'celebrity_industry' in df.columns:
        # 打印每一个出现的行业及其频次
        print(df['celebrity_industry'].value_counts())
    else:
        print("⚠️ 未找到列: celebrity_industry")

    # 2. 舞伴 (看看有没有带明星特别厉害的舞伴)
    print("\n" + "=" * 60)
    print("2. BALLROOM PARTNER (Top 20)")
    print("=" * 60)
    if 'ballroom_partner' in df.columns:
        print(df['ballroom_partner'].value_counts().head(20))

    # 3. 地理位置
    print("\n" + "=" * 60)
    print("3. GEOGRAPHY (家乡/国家)")
    print("=" * 60)
    # 注意：CSV表头可能是 "celebrity_homecountry/region"
    country_col = 'celebrity_homecountry/region'
    if country_col in df.columns:
        print("--- 国家/地区 (Top 10) ---")
        print(df[country_col].value_counts().head(10))

    if 'celebrity_homestate' in df.columns:
        print("\n--- 州/省份 (Top 15) ---")
        print(df['celebrity_homestate'].value_counts().head(15))

    # 4. 年龄分布
    print("\n" + "=" * 60)
    print("4. AGE STATISTICS (年龄统计)")
    print("=" * 60)
    if 'celebrity_age_during_season' in df.columns:
        print(df['celebrity_age_during_season'].describe())
        print(f"\n缺失年龄的选手数量: {df['celebrity_age_during_season'].isnull().sum()}")


if __name__ == "__main__":
    inspect_data()