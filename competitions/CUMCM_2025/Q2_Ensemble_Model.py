import os
os.environ.setdefault("OMP_NUM_THREADS", "4")
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Tuple, Dict
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.pipeline import make_pipeline
import matplotlib.pyplot as plt

FONT_BASE   = 20
FONT_TITLE  = 28
FONT_LABEL  = 24
FONT_TICK   = 20
FONT_LEGEND = 20
FONT_ANNO   = 20

plt.rcParams.update({
    'font.sans-serif': ['SimHei','Microsoft YaHei','PingFang SC','WenQuanYi Micro Hei','DejaVu Sans'],
    'axes.unicode_minus': False,
    'font.size': FONT_BASE,
    'axes.titlesize': FONT_TITLE,
    'axes.labelsize': FONT_LABEL,
    'xtick.labelsize': FONT_TICK,
    'ytick.labelsize': FONT_TICK,
    'legend.fontsize': FONT_LEGEND,
})

file = "男胎预处理后数据.xlsx"
K = 5
MAX_ITERS = 3
T_GRID_FINE = np.arange(10.0, 28.01, 0.1)
T_GRID_FAST = np.arange(10.0, 28.01, 0.2)
NUM_CAND = 60
LAMBDA_FAIL  = 3.0
LAMBDA_EARLY = 1.0
LAMBDA_LATE  = 5.0
MC_RUNS   = 200
NOISE_STD = 0.05
R_MAX = 300
EARLYSTOP_MIN_RUNS = 40
EARLYSTOP_REL_HALF = 0.01
REPORT_EVERY = 20
GROUP_MODEL  = 'gbdt'
GLOBAL_MODEL = 'gbdt'
POLY_DEGREE  = 3
RANDOM_STATE = 42
SEG_MIN = 30
BIG_PENALTY = 1e12

def find_col(df: pd.DataFrame, candidates: List[str]):
    for cand in candidates:
        for col in df.columns:
            if cand in str(col):
                return col
    return None

def load_and_prepare(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    y_col    = find_col(df, ['Y浓度','Y染色体浓度','浓度'])
    week_col = find_col(df, ['孕周','检测孕周','孕周数'])
    bmi_col  = find_col(df, ['BMI','孕妇BMI'])
    sex_col  = find_col(df, ['胎儿性别','性别'])
    keep = [c for c in [y_col, week_col, bmi_col, sex_col] if c is not None]
    data = df[keep].copy()
    if sex_col is not None:
        male_mask = data[sex_col].astype(str).str.contains('男|XY|male|Male', case=False, na=False)
    else:
        male_mask = data[y_col].notna()
    data = data[male_mask]
    data = data[[y_col, week_col, bmi_col]].rename(columns={y_col:'Y', week_col:'Week', bmi_col:'BMI'})
    data = data.replace([np.inf, -np.inf], np.nan).dropna().astype(float)
    data = data[(data['Week']>=8) & (data['Week']<=35)]
    data = data[(data['BMI']>=12) & (data['BMI']<=60)]
    data['Reach'] = (data['Y'] >= 0.04).astype(int)
    data['t_star_obs'] = np.where(data['Reach']==1, data['Week'], np.nan)
    data['t_star'] = data['t_star_obs'].fillna(20.0)
    return data.reset_index(drop=True)

class GroupPModel:
    def __init__(self, model_type='gbdt'):
        if model_type == 'logit':
            self.model = make_pipeline(
                PolynomialFeatures(POLY_DEGREE, include_bias=False),
                StandardScaler(),
                LogisticRegression(max_iter=300, solver='lbfgs', random_state=RANDOM_STATE)
            )
        elif model_type == 'gbdt':
            self.model = GradientBoostingClassifier(random_state=RANDOM_STATE)
        else:
            raise ValueError("model_type must be 'logit' or 'gbdt'")
    def fit(self, week: np.ndarray, reach: np.ndarray):
        self.model.fit(week.reshape(-1,1), reach)
    def p_hat(self, t: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(np.array(t).reshape(-1,1))[:,1]

class GlobalPModel:
    def __init__(self, model_type='gbdt'):
        if model_type == 'logit':
            self.model = make_pipeline(
                PolynomialFeatures(POLY_DEGREE, include_bias=False),
                StandardScaler(),
                LogisticRegression(max_iter=400, solver='lbfgs', random_state=RANDOM_STATE)
            )
        elif model_type == 'gbdt':
            self.model = GradientBoostingClassifier(random_state=RANDOM_STATE)
        else:
            raise ValueError("model_type must be 'logit' or 'gbdt'")
    def fit(self, week: np.ndarray, bmi: np.ndarray, reach: np.ndarray):
        X = np.c_[week.reshape(-1,1), bmi.reshape(-1,1)]
        self.model.fit(X, reach)
    def p_hat_matrix(self, t_grid: np.ndarray, bmi_vec: np.ndarray) -> np.ndarray:
        T = len(t_grid); n = len(bmi_vec)
        T_rep = np.repeat(t_grid, n)
        BMI_rep = np.tile(bmi_vec, T)
        X = np.c_[T_rep.reshape(-1,1), BMI_rep.reshape(-1,1)]
        p = self.model.predict_proba(X)[:,1]
        return p.reshape(T, n)

def indiv_risk(p_hat: float, t: float, t_star_i: float,
               lambda_fail=LAMBDA_FAIL, lambda_early=LAMBDA_EARLY, lambda_late=LAMBDA_LATE,
               mc_runs=MC_RUNS, noise_std=NOISE_STD):
    if mc_runs and mc_runs > 0:
        eps = np.random.normal(0.0, noise_std, size=mc_runs)
        p_smpl = np.clip(p_hat + eps, 0.0, 1.0)
        fail = lambda_fail * np.mean(1.0 - p_smpl)
    else:
        fail = lambda_fail * (1.0 - p_hat)
    early = lambda_early * (1.0 if t < 12.0 else 0.0)
    late  = lambda_late  * max(0.0, t - float(t_star_i))
    return fail + early + late

def search_best_t_for_group(group_df: pd.DataFrame, clf: GroupPModel,
                            t_grid=T_GRID_FINE) -> Tuple[float, Dict[str, float]]:
    clf.fit(group_df['Week'].values, group_df['Reach'].values)
    risks = []
    for t in t_grid:
        p_hat_vec = clf.p_hat([t]*len(group_df))
        r = 0.0
        for p_i, t_star_i in zip(p_hat_vec, group_df['t_star'].values):
            r += indiv_risk(p_i, t, t_star_i)
        risks.append(r)
    idx = int(np.argmin(risks))
    return float(t_grid[idx]), {'risk_min': float(risks[idx]), 't_argmin': float(t_grid[idx])}

def build_candidates(n: int, m: int) -> List[int]:
    if m >= n:
        return list(range(n))
    cuts = sorted(set([int(round(q*(n-1))) for q in np.linspace(0,1,m)]))
    if cuts[-1] != n-1:
        cuts[-1] = n-1
    return cuts

def precompute_prefix_for_dp(sorted_df: pd.DataFrame, t_grid: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = len(sorted_df)
    gclf = GlobalPModel(GLOBAL_MODEL)
    gclf.fit(sorted_df['Week'].values, sorted_df['BMI'].values, sorted_df['Reach'].values)
    P = gclf.p_hat_matrix(t_grid, sorted_df['BMI'].values)
    fail = 1.0 - P
    S_fail = np.cumsum(fail, axis=1)
    t_star = sorted_df['t_star'].values.astype(float)
    mask = (t_star[None, :] <= t_grid[:, None]).astype(float)
    S_cnt  = np.cumsum(mask, axis=1)
    S_sumt = np.cumsum(mask * t_star[None, :], axis=1)
    return S_fail, S_cnt, S_sumt

def segment_cost_from_prefix(S_fail, S_cnt, S_sumt, t_grid, i, j,
                             lambda_fail=LAMBDA_FAIL, lambda_early=LAMBDA_EARLY, lambda_late=LAMBDA_LATE):
    fail_sum = S_fail[:, j] - (S_fail[:, i-1] if i>0 else 0.0)
    cnt_le   = S_cnt [:, j] - (S_cnt [:, i-1] if i>0 else 0.0)
    sum_le   = S_sumt[:, j] - (S_sumt[:, i-1] if i>0 else 0.0)
    n_seg = (j - i + 1)
    R_fail  = lambda_fail * fail_sum
    R_early = lambda_early * (t_grid < 12.0).astype(float) * n_seg
    R_late  = lambda_late  * (cnt_le * t_grid - sum_le)
    risk_t = R_fail + R_early + R_late
    idx = int(np.argmin(risk_t))
    return float(risk_t[idx]), float(t_grid[idx])

def precompute_cost_fast(sorted_df: pd.DataFrame, t_grid: np.ndarray, num_cand=NUM_CAND,
                         seg_min=SEG_MIN) -> Tuple[np.ndarray, np.ndarray, List[int]]:
    n = len(sorted_df)
    cand = build_candidates(n, num_cand)
    m = len(cand)
    Cost  = np.full((m, m), BIG_PENALTY, dtype=float)
    Tstar = np.full((m, m), np.nan, dtype=float)
    S_fail, S_cnt, S_sumt = precompute_prefix_for_dp(sorted_df, t_grid)
    for a, i_end in enumerate(cand):
        for b in range(a, m):
            j_end = cand[b]
            i_start = 0 if a==0 else cand[a-1]+1
            if j_end - i_start + 1 < seg_min:
                continue
            c, tstar = segment_cost_from_prefix(S_fail, S_cnt, S_sumt, t_grid, i_start, j_end)
            Cost[a, b]  = c
            Tstar[a, b] = tstar
    return Cost, Tstar, cand

def dp_optimal_cuts_candidates(Cost: np.ndarray, cand: List[int], K: int) -> Tuple[List[int], float]:
    m = len(cand)
    dp = np.full((K+1, m), np.inf)
    prev = np.full((K+1, m), -1, dtype=int)
    for j in range(m):
        dp[1, j] = Cost[0, j]
    for k in range(2, K+1):
        for j in range(k-1, m):
            best = np.inf; arg = -1
            for i in range(k-2, j):
                val = dp[k-1, i] + Cost[i+1, j]
                if val < best:
                    best = val; arg = i
            dp[k, j] = best
            prev[k, j] = arg
    j = m - 1
    total_cost = float(dp[K, j])
    if not np.isfinite(total_cost):
        raise ValueError("DP 无可行解：请降低 SEG_MIN 或增加 NUM_CAND。")
    cuts_cand_idx = []
    for k in range(K, 0, -1):
        cuts_cand_idx.append(j)
        j = prev[k, j]
    cuts_cand_idx = sorted(cuts_cand_idx)
    cuts = [cand[idx] for idx in cuts_cand_idx]
    return cuts, total_cost

@dataclass
class GroupResult:
    idx_range: Tuple[int, int]
    bmi_range: Tuple[float, float]
    t_star: float
    risk: float
    size: int

def alternating_optimization_fast(data: pd.DataFrame, K=K, max_iters=MAX_ITERS,
                                  num_cand=NUM_CAND, seg_min=SEG_MIN):
    df = data.sort_values('BMI').reset_index(drop=True)
    km = KMeans(n_clusters=K, random_state=RANDOM_STATE, n_init=10)
    km.fit(df[['BMI']].values)
    raw_labels = pd.Series(km.labels_, index=df.index)
    centers = km.cluster_centers_.ravel()
    order = np.argsort(centers)
    label_to_rank = {int(orig): int(rank) for rank, orig in enumerate(order)}
    df['grp'] = raw_labels.map(label_to_rank).astype(int)
    last_total = np.inf
    history = []
    for it in range(1, max_iters+1):
        group_results: List[GroupResult] = []
        for g in range(K):
            seg = df[df['grp']==g]
            if len(seg) < seg_min:
                group_results.append(GroupResult(
                    idx_range=(seg.index.min() if len(seg)>0 else -1,
                               seg.index.max() if len(seg)>0 else -1),
                    bmi_range=(float(seg['BMI'].min()) if len(seg)>0 else np.nan,
                               float(seg['BMI'].max()) if len(seg)>0 else np.nan),
                    t_star=np.nan, risk=BIG_PENALTY, size=len(seg)
                ))
                continue
            clf = GroupPModel(GROUP_MODEL)
            t_g, info = search_best_t_for_group(seg, clf, t_grid=T_GRID_FINE)
            group_results.append(GroupResult(
                idx_range=(seg.index.min(), seg.index.max()),
                bmi_range=(float(seg['BMI'].min()), float(seg['BMI'].max())),
                t_star=t_g, risk=info['risk_min'], size=len(seg)
            ))
        total_risk = sum(gr.risk for gr in group_results)
        history.append((it, total_risk))
        print(f"[Iter {it}] current total risk (point-estimate) = {total_risk:.3f}")
        print("    Building fast DP cost ...")
        Cost, Tstar, cand = precompute_cost_fast(df[['Week','Reach','t_star','BMI']], t_grid=T_GRID_FAST,
                                                 num_cand=num_cand, seg_min=seg_min)
        cuts, dp_cost = dp_optimal_cuts_candidates(Cost, cand, K)
        new_grp = np.zeros(len(df), dtype=int)
        start = 0
        for g, end in enumerate(cuts):
            new_grp[start:end + 1] = g
            start = end + 1
        if start < len(df):
            new_grp[start:] = K - 1
        df['grp'] = new_grp
        print(f"    DP total cost (fast) = {dp_cost:.3f}")
        if abs(last_total - dp_cost) < 1e-3:
            print(f"Converged at iter {it}.")
            break
        last_total = dp_cost
    final_groups = []
    for g in range(K):
        seg = df[df['grp']==g]
        if len(seg) < seg_min:
            final_groups.append({
                'Group': g+1, 'Size': len(seg),
                'BMI_range': (float(seg['BMI'].min()) if len(seg)>0 else np.nan,
                              float(seg['BMI'].max()) if len(seg)>0 else np.nan),
                't_star': np.nan, 'Risk': np.nan
            })
            continue
        clf = GroupPModel(GROUP_MODEL)
        t_g, info = search_best_t_for_group(seg, clf, t_grid=T_GRID_FINE)
        final_groups.append({
            'Group': g+1, 'Size': len(seg),
            'BMI_range': (float(seg['BMI'].min()), float(seg['BMI'].max())),
            't_star': t_g, 'Risk': info['risk_min']
        })
    final_df = pd.DataFrame(final_groups)
    return final_df.sort_values('Group'), history, df

def fast_error_analysis_noise_only_optimized(assign_df: pd.DataFrame, K=5,
                                             t_grid=T_GRID_FAST, R=R_MAX,
                                             noise_std=NOISE_STD,
                                             report_every=REPORT_EVERY,
                                             min_runs=EARLYSTOP_MIN_RUNS,
                                             ci_tol_rel=EARLYSTOP_REL_HALF):
    p_hat_by_group = {}
    tstar_by_group = {}
    sizes_by_group = {}
    bmi_rng_by_group = {}
    for g in range(K):
        seg = assign_df[assign_df['grp']==g][['Week','Reach','t_star','BMI']].copy().reset_index(drop=True)
        n_g = len(seg)
        sizes_by_group[g+1] = n_g
        if n_g < 10:
            p_hat_by_group[g+1] = None
            tstar_by_group[g+1] = None
            bmi_rng_by_group[g+1] = "NA"
            continue
        bmi_min, bmi_max = float(seg['BMI'].min()), float(seg['BMI'].max())
        bmi_rng_by_group[g+1] = f"{bmi_min:.1f} ~ {bmi_max:.1f}"
        clf = GroupPModel(GROUP_MODEL)
        clf.fit(seg['Week'].values, seg['Reach'].values)
        P = []
        for t in t_grid:
            P.append(clf.p_hat(np.array([t]*n_g)))
        P = np.stack(P, axis=0)
        p_hat_by_group[g+1] = P
        tstar_by_group[g+1] = seg['t_star'].values.astype(float)
    def group_risk_from_P(P, t_star_vec, t_grid, lambda_fail, lambda_early, lambda_late,
                          noise_std, M=200):
        T, n_g = P.shape
        eps = np.random.normal(0.0, noise_std, size=(M, T, n_g))
        P_smpl = np.clip(P[None, :, :] + eps, 0.0, 1.0)
        fail = lambda_fail * np.mean(1.0 - P_smpl, axis=(0,2))
        early = np.where(t_grid < 12.0, lambda_early, 0.0)
        late_all = np.maximum(t_grid[:, None] - t_star_vec[None, :], 0.0)
        late = lambda_late * np.mean(late_all, axis=1)
        risk_t = fail + early + late
        t_idx = int(np.argmin(risk_t))
        return risk_t, t_idx
    global_risks = []
    per_group_t  = {g: [] for g in range(1, K+1)}
    per_group_r  = {g: [] for g in range(1, K+1)}
    runs = 0
    for r in range(1, R+1):
        runs += 1
        total = 0.0
        for g in range(1, K+1):
            if p_hat_by_group[g] is None:
                per_group_t[g].append(np.nan)
                per_group_r[g].append(np.nan)
                continue
            P = p_hat_by_group[g]
            t_star_vec = tstar_by_group[g]
            risk_t, t_idx = group_risk_from_P(
                P, t_star_vec, t_grid,
                LAMBDA_FAIL, LAMBDA_EARLY, LAMBDA_LATE,
                noise_std=noise_std, M=200
            )
            per_group_t[g].append(float(t_grid[t_idx]))
            per_group_r[g].append(float(risk_t[t_idx]))
            total += float(risk_t[t_idx])
        global_risks.append(total)
        if (r % REPORT_EVERY == 0) or (r==1):
            arr = np.asarray(global_risks, dtype=float)
            mean = np.mean(arr); lo, hi = np.percentile(arr, [2.5, 97.5])
            rel_half = ((hi - lo)/2) / (mean + 1e-12)
            print(f"[MC {r}] total risk mean={mean:.3f}, 95%CI≈[{lo:.3f},{hi:.3f}], rel half-width={rel_half*100:.2f}%")
            if (r >= min_runs) and (rel_half < ci_tol_rel):
                print(f"Early stop at R={r} (relative CI half-width < {ci_tol_rel*100:.1f}%).")
                break
    def summarize_ci(arr, alpha=0.05):
        arr = np.asarray(arr, dtype=float)
        mean = np.nanmean(arr); std = np.nanstd(arr, ddof=1)
        lo, hi = np.nanpercentile(arr, [100*alpha/2, 100*(1-alpha/2)])
        return mean, std, lo, hi
    g_mean, g_std, g_lo, g_hi = summarize_ci(global_risks)
    print("\n=== 极速误差分析（测量噪声）- 全局总风险（优化版） ===")
    print(f"mean = {g_mean:.3f}, std = {g_std:.3f}, 95% CI ≈ [{g_lo:.3f}, {g_hi:.3f}]  (runs={runs})")
    rows = []
    for g in range(1, K+1):
        t_mean, t_std, t_lo, t_hi = summarize_ci(per_group_t[g])
        r_mean, r_std, r_lo, r_hi = summarize_ci(per_group_r[g])
        rows.append({
            '组': g,
            '样本量': (assign_df['grp']==(g-1)).sum(),
            'BMI区间': f"{assign_df.loc[assign_df['grp']==(g-1), 'BMI'].min():.1f} ~ "
                       f"{assign_df.loc[assign_df['grp']==(g-1), 'BMI'].max():.1f}" if (assign_df['grp']==(g-1)).sum()>0 else "NA",
            't*_g mean': t_mean, 't*_g std': t_std, 't*_g 95%CI低': t_lo, 't*_g 95%CI高': t_hi,
            '风险 mean': r_mean, '风险 std': r_std, '风险 95%CI低': r_lo, '风险 95%CI高': r_hi,
        })
    summary = pd.DataFrame(rows).sort_values('组')
    print("\n=== 极速误差分析（测量噪声）- 各组 t*_g 与组内风险（优化版） ===")
    print(summary.to_string(index=False))
    return summary, (g_mean, g_std, g_lo, g_hi), runs

if __name__ == "__main__":
    data = load_and_prepare(file)
    print(f"Loaded male cases: n={len(data)}")
    final_table, hist, assign_df = alternating_optimization_fast(
        data, K=K, max_iters=MAX_ITERS, num_cand=NUM_CAND, seg_min=SEG_MIN
    )
    print("\n=== 最终结果（按 BMI 组，优化版单次点估计）===")
    def fmt_rng(r):
        a,b = r
        if np.isnan(a) or np.isnan(b):
            return "NA"
        return f"{a:.1f} ~ {b:.1f}"
    final_table['BMI区间'] = final_table['BMI_range'].apply(fmt_rng)
    out = final_table[['Group','Size','BMI区间','t_star','Risk']].rename(
        columns={'Group':'组','Size':'样本量','t_star':'最佳孕周(t*_g)','Risk':'组内风险'}
    )
    print(out.to_string(index=False))
    if len(hist)>0:
        print("\n=== 迭代风险轨迹（点估计） ===")
        for it, val in hist:
            print(f"Iter {it}: total risk ≈ {val:.3f}")
    print("\n>>> 开始极速误差分析（固定优化后分组与模型，便于与KMeans极速版对比）")
    summary, global_stats, runs = fast_error_analysis_noise_only_optimized(
        assign_df, K=K, t_grid=T_GRID_FAST, R=R_MAX,
        noise_std=NOISE_STD, report_every=REPORT_EVERY,
        min_runs=EARLYSTOP_MIN_RUNS, ci_tol_rel=EARLYSTOP_REL_HALF
    )

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.sans-serif': ['SimHei','Microsoft YaHei','PingFang SC','WenQuanYi Micro Hei','DejaVu Sans'],
    'axes.unicode_minus': False,
})

LAMBDA_FAIL, LAMBDA_EARLY, LAMBDA_LATE = 3.0, 1.0, 5.0
T_GRID_PLOT = np.arange(10.0, 28.01, 0.1)
MC_NOISE_STD = 0.05
MC_RUNS = 150

class _GroupPModel:
    def __init__(self, typ='gbdt'):
        if typ == 'logit':
            from sklearn.pipeline import make_pipeline
            from sklearn.preprocessing import PolynomialFeatures, StandardScaler
            from sklearn.linear_model import LogisticRegression
            self.model = make_pipeline(
                PolynomialFeatures(3, include_bias=False),
                StandardScaler(),
                LogisticRegression(max_iter=300, solver='lbfgs', random_state=42)
            )
        else:
            from sklearn.ensemble import GradientBoostingClassifier
            self.model = GradientBoostingClassifier(random_state=42)
    def fit(self, week, reach):
        self.model.fit(week.reshape(-1,1), reach)
    def p_hat(self, t):
        return self.model.predict_proba(np.array(t).reshape(-1,1))[:,1]

def _train_models(assign_df, K):
    models = {}
    for g in range(K):
        seg = assign_df[assign_df['grp']==g]
        if len(seg) < 5:
            models[g] = None
            continue
        m = _GroupPModel('gbdt')
        m.fit(seg['Week'].values.astype(float), seg['Reach'].values.astype(int))
        models[g] = m
    return models

def risk_components_for_group(seg_df, model, t_grid,
                              mc_runs=MC_RUNS, noise_std=MC_NOISE_STD,
                              scale='per_capita'):
    n = len(seg_df)
    tstar = seg_df['t_star'].values.astype(float)
    p_t = model.p_hat(t_grid)
    eps = np.random.normal(0.0, noise_std, size=(mc_runs, len(t_grid)))
    p_smpl = np.clip(p_t[None, :] + eps, 0.0, 1.0)
    fail_pc  = LAMBDA_FAIL * np.mean(1.0 - p_smpl, axis=0)
    early_pc = LAMBDA_EARLY * (t_grid < 12.0).astype(float)
    late_pc  = LAMBDA_LATE * np.mean(np.maximum(t_grid[:,None] - tstar[None,:], 0.0), axis=1)
    if scale == 'sum':
        fail, early, late = fail_pc * n, early_pc * n, late_pc * n
    else:
        fail, early, late = fail_pc, early_pc, late_pc
    total = fail + early + late
    t_star = float(t_grid[int(np.argmin(total))])
    return fail, early, late, total, t_star

K_now = int(assign_df['grp'].max() + 1)
models = _train_models(assign_df, K_now)

weights = []
per_group = []
for g in range(K_now):
    seg = assign_df[assign_df['grp']==g]
    if len(seg) < 5 or models[g] is None:
        continue
    w = len(seg) / len(assign_df)
    fail, early, late, total, _ = risk_components_for_group(seg, models[g], T_GRID_PLOT, scale='per_capita')
    weights.append(w); per_group.append((fail, early, late, total))

if not per_group:
    fig, ax = plt.subplots(1,1, figsize=(11,4), dpi=140)
    ax.text(0.5, 0.5, "无可用数据绘制总体图", ha='center', va='center')
    ax.axis('off')
    plt.tight_layout()
    plt.show()
else:
    wf = np.zeros_like(T_GRID_PLOT, dtype=float)
    we = np.zeros_like(T_GRID_PLOT, dtype=float)
    wl = np.zeros_like(T_GRID_PLOT, dtype=float)
    wt = np.zeros_like(T_GRID_PLOT, dtype=float)
    for w, (f,e,l,t) in zip(weights, per_group):
        wf += w * f; we += w * e; wl += w * l; wt += w * t
    t_star_overall = float(T_GRID_PLOT[int(np.argmin(wt))])
    fig, ax = plt.subplots(1, 1, figsize=(15, 8), dpi=160, constrained_layout=True)
    polys = ax.stackplot(T_GRID_PLOT, wf, wl, we,
                         labels=['测序失败风险', '过晚检测风险', '过早检测风险'],
                         alpha=0.85)
    (line,) = ax.plot(T_GRID_PLOT, wt, lw=2.2, label='总风险')
    y_star = float(np.interp(t_star_overall, T_GRID_PLOT, wt))
    ax.axvline(t_star_overall, ls='--', lw=2)
    ax.annotate(f"最优≈{t_star_overall:.1f}周",
                (t_star_overall, min(y_star, wt.max() * 0.92)),
                xytext=(10, 10), textcoords='offset points')
    ax.set_xlabel("孕周  t")
    ax.set_ylabel("风险分量")
    ax.grid(True, alpha=0.25)
    ax.set_ylim(top=wt.max() * 1.10)
    legend_fs = max(8, plt.rcParams['legend.fontsize'] - 2)
    ax.legend(
        handles=[polys[0], polys[1], polys[2], line],
        labels=['测序失败风险', '过晚检测风险', '过早检测风险', '总风险'],
        loc='upper center',
        bbox_to_anchor=(0.5, 0.90),
        ncol=4,
        frameon=False,
        fontsize=legend_fs,
        columnspacing=1.2,
        handlelength=2.0,
        borderaxespad=0.2
    )
    plt.tight_layout()
    plt.show()
