import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from pygam import LinearGAM, s, te
from sklearn.metrics import r2_score
import warnings

warnings.filterwarnings("ignore", category=UserWarning, message=r".*Glyph .* missing from font\(s\).*")

plt.rcParams['font.size'] = 20
plt.rcParams['axes.titlesize'] = 22
plt.rcParams['axes.labelsize'] = 20
plt.rcParams['xtick.labelsize'] = 18
plt.rcParams['ytick.labelsize'] = 18
plt.rcParams['legend.fontsize'] = 18

path ="男胎预处理后数据.xlsx"
df = pd.read_excel(path)
window = 1.0
ngrid  = 200
alpha  = 0.05


def pick(keys):
    for c in df.columns:
        s = str(c)
        if any(k in s for k in keys):
            return c
    return None

y_c   = pick(['Y浓度','Y染色体浓度','浓度'])
bmi_c = pick(['BMI','孕妇BMI'])
wk_c  = pick(['孕周','检测孕周','孕周数'])
if not all([y_c, bmi_c, wk_c]):
    raise ValueError("列名不匹配")

d = df[[y_c, bmi_c, wk_c]].dropna().astype(float)
d.columns = ['Y','BMI','Week']
d['BW'] = d['BMI'] * d['Week']

y = d['Y'].values
X_lm  = sm.add_constant(d[['Week','BMI','BW']])
X_gam = d[['Week','BMI']].values

ols = sm.OLS(y, X_lm).fit()
gam = LinearGAM(s(0) + s(1) + te(0,1)).fit(X_gam, y)

r2_ols = r2_score(y, ols.predict(X_lm))
r2_gam = r2_score(y, gam.predict(X_gam))

w_med = float(np.median(d['Week']))
b_med = float(np.median(d['BMI']))
xw = np.linspace(d['Week'].min(), d['Week'].max(), ngrid)
xb = np.linspace(d['BMI'].min(),  d['BMI'].max(),  ngrid)

Xw = pd.DataFrame({'const':1.0, 'Week':xw, 'BMI':b_med, 'BW':b_med * xw})
Sf_w = ols.get_prediction(Xw).summary_frame(alpha=alpha)

Xb = pd.DataFrame({'const':1.0, 'Week':w_med, 'BMI':xb, 'BW':w_med * xb})
Sf_b = ols.get_prediction(Xb).summary_frame(alpha=alpha)

Gw = np.column_stack([xw, np.full_like(xw, b_med)])
gw_mean = gam.predict(Gw)
gw_lo, gw_hi = gam.prediction_intervals(Gw, width=1-alpha).T

Gb = np.column_stack([np.full_like(xb, w_med), xb])
gb_mean = gam.predict(Gb)
gb_lo, gb_hi = gam.prediction_intervals(Gb, width=1-alpha).T

def take(df_, key, c, w):
    sub = df_[(df_[key] >= c - w) & (df_[key] <= c + w)]
    if len(sub) < 20:
        sub = df_[(df_[key] >= c - 2*w) & (df_[key] <= c + 2*w)]
    return sub

def cover_ols(model, sub):
    Xs = sm.add_constant(sub[['Week','BMI','BW']])
    sf = model.get_prediction(Xs).summary_frame(alpha=alpha)
    lo, hi = sf['obs_ci_lower'].values, sf['obs_ci_upper'].values
    yv = sub['Y'].values
    return np.mean((yv >= lo) & (yv <= hi)), np.mean(hi - lo)

def cover_gam(model, sub):
    Xs = sub[['Week','BMI']].values
    pi = model.prediction_intervals(Xs, width=1-alpha)
    lo, hi = pi[:,0], pi[:,1]
    yv = sub['Y'].values
    return np.mean((yv >= lo) & (yv <= hi)), np.mean(hi - lo)

sub_w = take(d, 'BMI',  b_med, window)
c_ow, w_ow = cover_ols(ols, sub_w)
c_gw, w_gw = cover_gam(gam, sub_w)

sub_b = take(d, 'Week', w_med, window)
c_ob, w_ob = cover_ols(ols, sub_b)
c_gb, w_gb = cover_gam(gam, sub_b)

fig, ax = plt.subplots(2, 2, figsize=(14, 9), sharey=True)

ax[0,0].scatter(d['Week'], d['Y'], s=15, alpha=0.3)
ax[0,0].plot(xw, Sf_w['mean'], color='black')
ax[0,0].fill_between(xw, Sf_w['obs_ci_lower'], Sf_w['obs_ci_upper'], color='gray', alpha=0.3)
ax[0,0].set_title(f"OLS：孕周→Y | R²={r2_ols:.2f} 覆盖率={c_ow:.2%} 宽度={w_ow:.3f}")
ax[0,0].set_xlabel("孕周")
ax[0,0].set_ylabel("Y")

ax[0,1].scatter(d['Week'], d['Y'], s=15, alpha=0.3)
ax[0,1].plot(xw, gw_mean, color='orange')
ax[0,1].fill_between(xw, gw_lo, gw_hi, color='gray', alpha=0.3)
ax[0,1].set_title(f"GAM：孕周→Y | R²={r2_gam:.2f} 覆盖率={c_gw:.2%} 宽度={w_gw:.3f}")
ax[0,1].set_xlabel("孕周")

ax[1,0].scatter(d['BMI'], d['Y'], s=15, alpha=0.3)
ax[1,0].plot(xb, Sf_b['mean'], color='black')
ax[1,0].fill_between(xb, Sf_b['obs_ci_lower'], Sf_b['obs_ci_upper'], color='gray', alpha=0.3)
ax[1,0].set_title(f"OLS：BMI→Y | R²={r2_ols:.2f} 覆盖率={c_ob:.2%} 宽度={w_ob:.3f}")
ax[1,0].set_xlabel("BMI")
ax[1,0].set_ylabel("Y")

ax[1,1].scatter(d['BMI'], d['Y'], s=15, alpha=0.3)
ax[1,1].plot(xb, gb_mean, color='orange')
ax[1,1].fill_between(xb, gb_lo, gb_hi, color='gray', alpha=0.3)
ax[1,1].set_title(f"GAM：BMI→Y | R²={r2_gam:.2f} 覆盖率={c_gb:.2%} 宽度={w_gb:.3f}")
ax[1,1].set_xlabel("BMI")

plt.tight_layout()
plt.show()
