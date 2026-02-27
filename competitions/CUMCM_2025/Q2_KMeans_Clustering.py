import os
os.environ.setdefault("OMP_NUM_THREADS", "4")

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.pipeline import make_pipeline

# 参数
path = "男胎预处理后数据.xlsx"
K = 5
T_GRID = np.arange(10.0, 28.01, 0.1)
GROUP_MODEL = "gbdt"          # 'logit' / 'gbdt'
POLY_DEGREE = 3
L_FAIL, L_EARLY, L_LATE = 3.0, 1.0, 5.0
MC_RUNS, NOISE_STD = 200, 0.05
SEED = 42

def pick(df, keys):
    for c in df.columns:
        s = str(c)
        if any(k in s for k in keys):
            return c
    return None

def load_data(p):
    df = pd.read_excel(p)
    y_c   = pick(df, ['Y浓度','Y染色体浓度','浓度'])
    w_c   = pick(df, ['孕周','检测孕周','孕周数'])
    b_c   = pick(df, ['BMI','孕妇BMI'])
    sex_c = pick(df, ['胎儿性别','性别'])
    keep = [c for c in [y_c, w_c, b_c, sex_c] if c]
    d = df[keep].copy()

    if sex_c:
        m = d[sex_c].astype(str).str.contains('男|XY|male', case=False, na=False)
    else:
        m = d[y_c].notna()
    d = d[m]

    d = d[[y_c, w_c, b_c]].rename(columns={y_c:'Y', w_c:'Week', b_c:'BMI'})
    d = d.replace([np.inf, -np.inf], np.nan).dropna().astype(float)
    d = d[(d['Week']>=8) & (d['Week']<=35)]
    d = d[(d['BMI']>=12) & (d['BMI']<=60)]

    d['Reach'] = (d['Y'] >= 0.04).astype(int)
    d['t_star_obs'] = np.where(d['Reach']==1, d['Week'], np.nan)
    d['t_star'] = d['t_star_obs'].fillna(20.0)
    return d.reset_index(drop=True)

class GModel:
    def __init__(self, kind='gbdt'):
        if kind == 'logit':
            self.m = make_pipeline(
                PolynomialFeatures(POLY_DEGREE, include_bias=False),
                StandardScaler(),
                LogisticRegression(max_iter=300, solver='lbfgs', random_state=SEED)
            )
        elif kind == 'gbdt':
            self.m = GradientBoostingClassifier(random_state=SEED)
        else:
            raise ValueError("kind 应为 'logit' 或 'gbdt'")

    def fit(self, week, y):
        self.m.fit(week.reshape(-1,1), y)

    def p(self, t):
        t = np.array(t).reshape(-1,1)
        return self.m.predict_proba(t)[:,1]

def risk_one(p_hat, t, t_star):
    if MC_RUNS and MC_RUNS > 0:
        eps = np.random.normal(0.0, NOISE_STD, size=MC_RUNS)
        p_s = np.clip(p_hat + eps, 0.0, 1.0)
        fail = L_FAIL * np.mean(1.0 - p_s)
    else:
        fail = L_FAIL * (1.0 - p_hat)
    early = L_EARLY * (1.0 if t < 12.0 else 0.0)
    late  = L_LATE  * max(0.0, t - float(t_star))
    return fail + early + late

def search_t(seg, clf, grid=T_GRID):
    clf.fit(seg['Week'].values, seg['Reach'].values)
    rs = []
    for t in grid:
        pv = clf.p([t]*len(seg))
        r = 0.0
        for p_i, ts in zip(pv, seg['t_star'].values):
            r += risk_one(p_i, t, ts)
        rs.append(r)
    i = int(np.argmin(rs))
    return float(grid[i]), {'risk_min': float(rs[i]), 't_argmin': float(grid[i])}

def kmeans_baseline(data, K=5):
    d = data.copy()
    km = KMeans(n_clusters=K, random_state=SEED, n_init=10).fit(d[['BMI']].values)
    lab = pd.Series(km.labels_, index=d.index)
    order = np.argsort(km.cluster_centers_.ravel())
    mp = {int(o): int(r) for r, o in enumerate(order)}
    d['grp'] = lab.map(mp).astype(int)

    rows, total = [], 0.0
    for g in range(K):
        seg = d[d['grp']==g]
        if len(seg) < 10:
            rows.append({'组': g+1, '样本量': len(seg), 'BMI区间': 'NA',
                         '最佳孕周(t*_g)': np.nan, '组内风险': np.nan})
            continue
        clf = GModel(GROUP_MODEL)
        t_g, info = search_t(seg, clf)
        total += info['risk_min']
        bmi_min, bmi_max = float(seg['BMI'].min()), float(seg['BMI'].max())
        rows.append({'组': g+1, '样本量': len(seg), 'BMI区间': f"{bmi_min:.1f} ~ {bmi_max:.1f}",
                     '最佳孕周(t*_g)': t_g, '组内风险': info['risk_min']})
    tab = pd.DataFrame(rows).sort_values('组')
    return tab, total, d

def fast_eval(data, K=5, grid=None, R=200, noise_std=0.05, ci_tol_rel=0.01, min_runs=40, report_every=20):
    if grid is None:
        grid = np.arange(10.0, 28.01, 0.2)

    tab, _, assign = kmeans_baseline(data, K=K)

    P_by_g, tstar_by_g, size_by_g, bmi_rng_by_g = {}, {}, {}, {}
    for _, r in tab.iterrows():
        g = int(r['组'])
        seg = assign[assign['grp']==(g-1)][['Week','Reach','t_star','BMI']].copy().reset_index(drop=True)
        n = len(seg)
        size_by_g[g] = n
        if n < 10:
            P_by_g[g] = None
            tstar_by_g[g] = None
            bmi_rng_by_g[g] = "NA"
            continue
        bmi_rng_by_g[g] = f"{float(seg['BMI'].min()):.1f} ~ {float(seg['BMI'].max()):.1f}"
        clf = GModel(GROUP_MODEL)
        clf.fit(seg['Week'].values, seg['Reach'].values)
        P = np.stack([clf.p([t]*n) for t in grid], axis=0)
        P_by_g[g] = P
        tstar_by_g[g] = seg['t_star'].values.astype(float)

    def group_risk(P, t_star_vec, grid, noise_std, M=200):
        T, n = P.shape
        eps = np.random.normal(0.0, noise_std, size=(M, T, n))
        Ps = np.clip(P[None, :, :] + eps, 0.0, 1.0)
        fail = L_FAIL * np.mean(1.0 - Ps, axis=(0, 2))
        early = np.where(grid < 12.0, L_EARLY, 0.0)
        late = L_LATE * np.mean(np.maximum(grid[:, None] - t_star_vec[None, :], 0.0), axis=1)
        r = fail + early + late
        i = int(np.argmin(r))
        return r, i

    G = []
    Tm = {g: [] for g in range(1, K+1)}
    Rm = {g: [] for g in range(1, K+1)}

    runs = 0
    for r in range(1, R+1):
        runs += 1
        tot = 0.0
        for g in range(1, K+1):
            if P_by_g[g] is None:
                Tm[g].append(np.nan); Rm[g].append(np.nan)
                continue
            r_t, i = group_risk(P_by_g[g], tstar_by_g[g], grid, noise_std, M=200)
            Tm[g].append(float(grid[i]))
            Rm[g].append(float(r_t[i]))
            tot += float(r_t[i])
        G.append(tot)

        if (r % report_every == 0) or (r == 1):
            a = np.asarray(G, dtype=float)
            m = np.mean(a); lo, hi = np.percentile(a, [2.5, 97.5])
            rel = ((hi - lo) / 2) / (m + 1e-12)
            print(f"[MC {r}] risk mean={m:.3f}, 95%CI≈[{lo:.3f},{hi:.3f}], rel half={rel*100:.2f}%")
            if (r >= min_runs) and (rel < ci_tol_rel):
                print(f"早停: R={r} (相对半宽 < {ci_tol_rel*100:.1f}%).")
                break

    def stat(a, alpha=0.05):
        a = np.asarray(a, dtype=float)
        m = np.nanmean(a); s = np.nanstd(a, ddof=1)
        lo, hi = np.nanpercentile(a, [100*alpha/2, 100*(1-alpha/2)])
        return m, s, lo, hi

    gm, gs, glo, ghi = stat(G)
    print("\n=== 极速误差分析-全局总风险 ===")
    print(f"mean={gm:.3f}, std={gs:.3f}, 95%CI≈[{glo:.3f},{ghi:.3f}]  (runs={runs})")

    rows = []
    for g in range(1, K+1):
        tm, ts, tlo, thi = stat(Tm[g])
        rm, rs, rlo, rhi = stat(Rm[g])
        rows.append({
            '组': g, '样本量': size_by_g.get(g, np.nan), 'BMI区间': bmi_rng_by_g.get(g, "NA"),
            't*_g mean': tm, 't*_g std': ts, 't*_g 95%CI低': tlo, 't*_g 95%CI高': thi,
            '风险 mean': rm, '风险 std': rs, '风险 95%CI低': rlo, '风险 95%CI高': rhi
        })
    summ = pd.DataFrame(rows).sort_values('组')
    print("\n=== 极速误差分析-各组 ===")
    print(summ.to_string(index=False))
    return summ, (gm, gs, glo, ghi), runs

if __name__ == "__main__":
    data = load_data(path)
    print(f"加载男胎: n={len(data)}")

    tab, tot, assign = kmeans_baseline(data, K=K)
    print("\n=== KMeans 基线（单次） ===")
    print(tab.to_string(index=False))
    print(f"\n全局总风险(单次) ≈ {tot:.3f}")

    summ, gstats, runs = fast_eval(
        data, K=K,
        grid=np.arange(10.0, 28.01, 0.2),
        R=300,
        noise_std=NOISE_STD,
        ci_tol_rel=0.01,
        min_runs=40,
        report_every=20
    )
