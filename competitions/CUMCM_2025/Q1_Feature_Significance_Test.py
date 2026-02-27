import pandas as pd
from pygam import LinearGAM, s, te
import io, contextlib, warnings

path ="男胎预处理后数据.xlsx"
df = pd.read_excel(path)

def pick(keys):
    for c in df.columns:
        s = str(c)
        if any(k in s for k in keys):
            return c
    return None

y_c   = pick(["Y浓度","Y染色体浓度","浓度"])
bmi_c = pick(["BMI","孕妇BMI"])
wk_c  = pick(["孕周","检测孕周","孕周数"])
if not all([y_c, bmi_c, wk_c]):
    raise ValueError("列名不匹配")

tmp = df[[y_c, bmi_c, wk_c]].dropna().astype(float)
tmp.columns = ["Y","BMI","Week"]

y = tmp["Y"].values
X = tmp[["Week","BMI"]].values

gam = LinearGAM(s(0) + s(1) + te(0,1)).fit(X, y)

print("\n=== GAM 显著性检验（含交互） ===")
buf = io.StringIO()
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=UserWarning, message=r".*KNOWN BUG: p-values.*")
    with contextlib.redirect_stdout(buf):
        gam.summary()

txt = buf.getvalue()
lines = []
for ln in txt.splitlines():
    s = ln.strip()
    if s.startswith("WARNING:"):
        continue
    if s.startswith("Significance codes:"):
        continue
    lines.append(ln)

print("\n".join(lines))
