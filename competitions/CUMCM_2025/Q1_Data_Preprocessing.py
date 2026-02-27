import pandas as pd
import re
import numpy as np

in_path  = "附件.xlsx"
out_path = "男胎预处理后数据1.xlsx"

WEEKS = "检测孕周"
RAW   = "原始读段数"
UNIQ  = "唯一比对的读段数  "
RATE  = "在参考基因组上比对的比例"
GC    = "GC含量"

def parse_weeks(x):
    if pd.isna(x): return None
    s = str(x).strip().replace("周", "w").replace("＋", "+").replace("W", "w")
    s = re.sub(r"\s+", "", s)
    m = re.match(r"^(\d+)w(?:\+(\d+))?$", s)
    if not m: return None
    w = int(m.group(1))
    d = int(m.group(2)) if m.group(2) else 0
    return round(w + d/7, 2)

def to_m(x):
    if pd.isna(x): return np.nan
    s = str(x).replace(",", "").strip()
    m = re.match(r"^([0-9]*\.?[0-9]+)\s*([Mm])?$", s)
    if not m: return np.nan
    v = float(m.group(1))
    return v if m.group(2) else (v/1e6 if v >= 1e6 else v)

def to_ratio(x):
    if pd.isna(x): return np.nan
    s = str(x).replace("%", "").strip()
    try:
        v = float(s)
    except:
        return np.nan
    return v/100 if v > 1 else v

def to_pct(x):
    if pd.isna(x): return np.nan
    s = str(x).replace("%", "").strip()
    try:
        v = float(s)
    except:
        return np.nan
    return v*100 if v <= 1 else v

df = pd.read_excel(in_path)

if WEEKS in df.columns:
    df[WEEKS] = df[WEEKS].apply(parse_weeks)

m_raw = pd.Series(np.nan, index=df.index)
m_uniq = pd.Series(np.nan, index=df.index)
r_map = pd.Series(np.nan, index=df.index)
gc_pct = pd.Series(np.nan, index=df.index)

if RAW in df.columns:
    m_raw = df[RAW].apply(to_m).astype(float)
if UNIQ in df.columns:
    m_uniq = df[UNIQ].apply(to_m).astype(float)
if RATE in df.columns:
    r_map = df[RATE].apply(to_ratio).astype(float)
if GC in df.columns:
    gc_pct = df[GC].apply(to_pct).astype(float)

mask = pd.Series(True, index=df.index)
if RAW in df.columns:
    mask &= (m_raw >= 3).fillna(False)
if UNIQ in df.columns:
    mask &= (m_uniq >= 2).fillna(False)
if RATE in df.columns:
    mask &= (r_map >= 0.75).fillna(False)
if GC in df.columns:
    mask &= (gc_pct >= 39).fillna(False)

before = len(df)
df_out = df[mask].copy()
after = len(df_out)

df_out.to_excel(out_path, index=False)

print("处理完成")
print("原始行数：", before)
print("筛选后行数：", after)
print("结果已保存到：", out_path)
