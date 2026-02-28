clc; clear; close all;

%% ========== 全局参数 ==========
h        = 15;
phi_push = pi/2;
N_theta  = 5000;

r0_vec    = 30:5:90;       % 基圆半径（粗扫，用于图2散点）
e_vec     = -15:1:15;      % 偏置量（图1、图3用，步长1mm）
e_vec_fine = -15:0.1:15;   % 细密偏置量（图2连续曲线用）

alpha_limit = 30;

%% ========== 核心计算函数（脚本内子函数放末尾） ==========

%% ========== 预计算1：图1、图3 用 (r0=30, e粗扫) ==========
r0_fix  = 30;
n_e     = length(e_vec);
amax_r0  = zeros(1, n_e);
amean_r0 = zeros(1, n_e);

fprintf('预计算图1/图3 (r0=%d, e步长1mm)...\n', r0_fix);
for ie = 1:n_e
    ad = push_alpha(r0_fix, e_vec(ie), h, phi_push, N_theta);
    ad = ad(isfinite(ad));
    if ~isempty(ad)
        amax_r0(ie)  = max(ad);
        amean_r0(ie) = mean(ad);
    else
        amax_r0(ie)  = NaN;
        amean_r0(ie) = NaN;
    end
end

%% ========== 预计算2：图2 用 (r0扫描，e细密扫描) ==========
e_opt_vec     = zeros(1, length(r0_vec));  % 连续最优e（细扫）
alpha_opt_vec = zeros(1, length(r0_vec));  % 对应αmax最小值
e_opt_coarse  = zeros(1, length(r0_vec));  % 粗扫最优e（供对比）

fprintf('预计算图2 (r0遍历, e细密步长0.1mm)...\n');
for ir = 1:length(r0_vec)
    r0 = r0_vec(ir);
    amax_tmp = zeros(1, length(e_vec_fine));
    for ie = 1:length(e_vec_fine)
        ad = push_alpha(r0, e_vec_fine(ie), h, phi_push, 2000);
        ad = ad(isfinite(ad));
        if ~isempty(ad)
            amax_tmp(ie) = max(ad);
        else
            amax_tmp(ie) = NaN;
        end
    end
    [v, id] = min(amax_tmp);
    e_opt_vec(ir)     = e_vec_fine(id);
    alpha_opt_vec(ir) = v;

    % 粗扫对比
    amax_c = zeros(1, length(e_vec));
    for ie = 1:length(e_vec)
        ad = push_alpha(r0, e_vec(ie), h, phi_push, 2000);
        ad = ad(isfinite(ad));
        if ~isempty(ad), amax_c(ie) = max(ad); else, amax_c(ie) = NaN; end
    end
    [~, idc] = min(amax_c);
    e_opt_coarse(ir) = e_vec(idc);
end
fprintf('计算完成！\n\n');

%% ========== 深色主题 ==========
C_bg  = [0.10 0.10 0.13];
C_ax  = [0.14 0.14 0.18];
C_txt = [0.93 0.93 0.93];
C_grd = [0.36 0.36 0.42];

%% ================================================================
%  图1：固定 r0=30，αmax 随 e 的变化
%% ================================================================
[min_val, idx_min] = min(amax_r0);
e_opt1 = e_vec(idx_min);

fig1 = figure('Color', C_bg, 'Position', [60, 60, 860, 560]);
ax1 = axes('Parent', fig1, 'Color', C_ax, 'Position', [0.11 0.12 0.82 0.78]);
hold(ax1, 'on');

% 许用压力角参考线
yline(ax1, alpha_limit, '--', 'Color', [0.95 0.35 0.30], 'LineWidth', 1.6);
text(ax1, e_vec(1)+0.5, alpha_limit+1.2, sprintf('허용선 %d°', alpha_limit), ...
     'Color', [1 0.5 0.5], 'FontSize', 10, 'FontWeight', 'bold');

% 渐变色曲线
cmap1 = cool(n_e);
for k = 1:n_e-1
    plot(ax1, e_vec(k:k+1), amax_r0(k:k+1), '-', ...
         'Color', cmap1(k,:), 'LineWidth', 2.4);
end
plot(ax1, e_vec, amax_r0, 'o', 'MarkerSize', 5, ...
     'MarkerFaceColor', [0.9 0.9 0.9], 'MarkerEdgeColor', [0.6 0.6 0.6], 'LineWidth', 0.8);

% 最小值标注
plot(ax1, e_opt1, min_val, 'p', 'MarkerSize', 15, ...
     'MarkerFaceColor', [1.0 0.85 0.20], 'MarkerEdgeColor', [0.8 0.6 0.0], 'LineWidth', 1.2);
text(ax1, e_opt1+0.6, min_val+1.8, ...
     sprintf('最优 e = %d mm\nalpha_max = %.1f°', e_opt1, min_val), ...
     'Color', [1.0 0.90 0.40], 'FontSize', 10, 'FontWeight', 'bold');

% 样式
ax1.Color = C_ax; ax1.XColor = C_txt; ax1.YColor = C_txt;
ax1.GridColor = C_grd; ax1.GridAlpha = 0.30; ax1.FontSize = 10.5;
grid(ax1, 'on'); box(ax1, 'on');
xlabel(ax1, '偏置量  e  (mm)', 'Color', C_txt, 'FontSize', 12, 'FontWeight', 'bold');
ylabel(ax1, '最大推程压力角 alpha_max (°)', 'Color', C_txt, 'FontSize', 12, 'FontWeight', 'bold');
title(ax1, sprintf('固定 r0 = %d mm: 最大推程压力角随偏置量 e 的变化', r0_fix), ...
     'Color', [1 1 1], 'FontSize', 13, 'FontWeight', 'bold');
xlim(ax1, [e_vec(1)-0.5, e_vec(end)+0.5]);

colormap(ax1, cool);
cb1 = colorbar(ax1, 'Color', C_txt);
cb1.Label.String = '偏置量 e (mm)';
cb1.Label.Color  = C_txt;
cb1.Label.FontSize = 10;
caxis(ax1, [e_vec(1), e_vec(end)]);

annotation(fig1, 'textbox', [0.005 0.005 0.16 0.11], ...
    'String', sprintf('r0 = %d mm\nh = %d mm\n最优 e = %d mm\nalpha_min = %.1f°', r0_fix, h, e_opt1, min_val), ...
    'Color', C_txt, 'BackgroundColor', [0.17 0.17 0.22], ...
    'EdgeColor', [0.48 0.48 0.58], 'FontSize', 9.5, 'LineWidth', 1.0, 'FitBoxToText', 'off');

%% ================================================================
%  图2：不同 r0 下的最优偏置量（细密扫描，连续曲线）
%% ================================================================
% 多项式拟合
p_coeff = polyfit(r0_vec, e_opt_vec, 2);
r0_fine = linspace(r0_vec(1), r0_vec(end), 500);
e_fit   = polyval(p_coeff, r0_fine);

fig2 = figure('Color', C_bg, 'Position', [110, 110, 1000, 580]);
ax2 = axes('Parent', fig2, 'Color', C_ax, 'Position', [0.09 0.12 0.84 0.78]);
hold(ax2, 'on');

% 粗扫阶梯线（对比用，浅色）
stairs(ax2, r0_vec, e_opt_coarse, '--', 'Color', [0.6 0.6 0.6], 'LineWidth', 1.2);

% 细扫连续曲线（渐变色）
n_r0 = length(r0_vec);
cmap2 = jet(n_r0);
for k = 1:n_r0-1
    plot(ax2, r0_vec(k:k+1), e_opt_vec(k:k+1), '-', ...
         'Color', cmap2(k,:), 'LineWidth', 2.5);
end

% 散点（按 alpha_opt 着色）
scatter(ax2, r0_vec, e_opt_vec, 90, alpha_opt_vec, 'filled', ...
        'MarkerEdgeColor', [1 1 1], 'LineWidth', 0.9);

% 拟合曲线
plot(ax2, r0_fine, e_fit, '--', 'Color', [1 1 1], 'LineWidth', 1.8);

% 每个点标注 alpha_min
for k = 1:n_r0
    text(ax2, r0_vec(k), e_opt_vec(k)+0.12, ...
         sprintf('%.1f°', alpha_opt_vec(k)), ...
         'Color', [0.95 0.95 0.65], 'FontSize', 8, 'HorizontalAlignment', 'center');
end

colormap(ax2, parula);
cb2 = colorbar(ax2, 'Color', C_txt);
cb2.Label.String = '对应最小 alpha_max (°)';
cb2.Label.Color  = C_txt;
cb2.Label.FontSize = 10;
cb2.FontSize = 10;

ax2.Color = C_ax; ax2.XColor = C_txt; ax2.YColor = C_txt;
ax2.GridColor = C_grd; ax2.GridAlpha = 0.30; ax2.FontSize = 10.5;
grid(ax2, 'on'); box(ax2, 'on');

xlabel(ax2, '基圆半径 r0 (mm)', 'Color', C_txt, 'FontSize', 12, 'FontWeight', 'bold');
ylabel(ax2, '最优偏置量 e_opt (mm)', 'Color', C_txt, 'FontSize', 12, 'FontWeight', 'bold');
title(ax2, {'不同基圆半径 r0 下使 alpha_max 最小的最优偏置量 e_opt', ...
            '(细线=连续扫描, 虚线=离散步长1mm对比, 白虚线=二次拟合)'}, ...
     'Color', [1 1 1], 'FontSize', 12, 'FontWeight', 'bold');
xlim(ax2, [r0_vec(1)-2, r0_vec(end)+2]);

annotation(fig2, 'textbox', [0.005 0.005 0.22 0.10], ...
    'String', sprintf('拟合: e = %.4fr0^2 + %.4fr0 + %.2f', p_coeff), ...
    'Color', C_txt, 'BackgroundColor', [0.17 0.17 0.22], ...
    'EdgeColor', [0.48 0.48 0.58], 'FontSize', 9, 'LineWidth', 1.0, 'FitBoxToText', 'off');

%% ================================================================
%  图3：r0=30，αmax 与 αmean 随 e 的变化（双纵轴，避免legend跨轴问题）
%% ================================================================
[max_min,  idx_maxmin]  = min(amax_r0);
[mean_min, idx_meanmin] = min(amean_r0);

fig3 = figure('Color', C_bg, 'Position', [160, 160, 1000, 580]);

% ---- 左轴：αmax ----
ax3L = axes('Parent', fig3, 'Color', C_ax, 'Position', [0.10 0.12 0.75 0.78]);
hold(ax3L, 'on');

cmap3 = cool(n_e);
for k = 1:n_e-1
    plot(ax3L, e_vec(k:k+1), amax_r0(k:k+1), '-', 'Color', cmap3(k,:), 'LineWidth', 2.5);
end
plot(ax3L, e_vec, amax_r0, 'o', 'MarkerSize', 5.5, ...
     'MarkerFaceColor', [0.55 0.80 1.0], 'MarkerEdgeColor', [0.3 0.6 0.9], 'LineWidth', 0.8);

% αmax最小值标注
plot(ax3L, e_vec(idx_maxmin), max_min, 'p', 'MarkerSize', 13, ...
     'MarkerFaceColor', [0.3 0.85 1.0], 'MarkerEdgeColor', [0.1 0.5 0.9], 'LineWidth', 1.2);
text(ax3L, e_vec(idx_maxmin)-1.2, max_min-2.2, ...
     sprintf('e=%d, alpha_max=%.1f°', e_vec(idx_maxmin), max_min), ...
     'Color', [0.5 0.9 1.0], 'FontSize', 9.5, 'FontWeight', 'bold', 'HorizontalAlignment', 'right');

% 许用线
yline(ax3L, alpha_limit, '-.', 'Color', [0.95 0.35 0.30], 'LineWidth', 1.5);
text(ax3L, e_vec(end)-0.5, alpha_limit+1.0, sprintf('%d°', alpha_limit), ...
     'Color', [1 0.5 0.5], 'FontSize', 10, 'FontWeight', 'bold', 'HorizontalAlignment', 'right');

ax3L.Color = C_ax; ax3L.XColor = C_txt; ax3L.YColor = [0.55 0.80 1.0];
ax3L.GridColor = C_grd; ax3L.GridAlpha = 0.30; ax3L.FontSize = 10.5;
grid(ax3L, 'on'); box(ax3L, 'on');
xlabel(ax3L, '偏置量 e (mm)', 'Color', C_txt, 'FontSize', 12, 'FontWeight', 'bold');
ylabel(ax3L, '最大推程压力角 alpha_max (°)', 'Color', [0.55 0.80 1.0], 'FontSize', 12, 'FontWeight', 'bold');
xlim(ax3L, [e_vec(1)-0.5, e_vec(end)+0.5]);

% ---- 右轴：αmean（新建，完全独立） ----
ax3R = axes('Parent', fig3, 'Color', 'none', ...
            'Position', ax3L.Position, ...
            'YAxisLocation', 'right', 'XTick', [], ...
            'XColor', 'none');
ax3R.YColor = [1.0 0.60 0.30];
ax3R.FontSize = 10.5;
hold(ax3R, 'on');

cmap4 = autumn(n_e);
for k = 1:n_e-1
    plot(ax3R, e_vec(k:k+1), amean_r0(k:k+1), '-', 'Color', cmap4(k,:), 'LineWidth', 2.5);
end
plot(ax3R, e_vec, amean_r0, 's', 'MarkerSize', 5.5, ...
     'MarkerFaceColor', [1.0 0.75 0.4], 'MarkerEdgeColor', [0.9 0.55 0.2], 'LineWidth', 0.8);

plot(ax3R, e_vec(idx_meanmin), mean_min, 'p', 'MarkerSize', 13, ...
     'MarkerFaceColor', [1.0 0.80 0.3], 'MarkerEdgeColor', [0.8 0.55 0.1], 'LineWidth', 1.2);
text(ax3R, e_vec(idx_meanmin)+0.6, mean_min+0.6, ...
     sprintf('e=%d, mean=%.1f°', e_vec(idx_meanmin), mean_min), ...
     'Color', [1.0 0.88 0.45], 'FontSize', 9.5, 'FontWeight', 'bold');

ylabel(ax3R, '平均推程压力角 alpha_mean (°)', 'Color', [1.0 0.60 0.30], 'FontSize', 12, 'FontWeight', 'bold');
xlim(ax3R, [e_vec(1)-0.5, e_vec(end)+0.5]);

% ---- 标题 ----
title(ax3L, {sprintf('固定 r0 = %d mm: 最大压力角与平均压力角随偏置量 e 的变化', r0_fix), ...
             '蓝色圆点 = alpha_max (左轴),  橙色方块 = alpha_mean (右轴)'}, ...
     'Color', [1 1 1], 'FontSize', 12, 'FontWeight', 'bold');

% ---- 手动图例（用 patch 画色块，避免跨轴问题） ----
patch(ax3L, [0 0 0 0], [0 0 0 0], [0.55 0.80 1.0], ...
      'DisplayName', '最大压力角 alpha\_max', 'EdgeColor', 'none');
patch(ax3L, [0 0 0 0], [0 0 0 0], [1.0 0.65 0.2], ...
      'DisplayName', '平均压力角 alpha\_mean', 'EdgeColor', 'none');
leg3 = legend(ax3L, 'Location', 'north', 'NumColumns', 2);
leg3.TextColor = C_txt;
leg3.Color     = [0.14 0.14 0.20];
leg3.EdgeColor = [0.5 0.5 0.6];
leg3.FontSize  = 10.5;

annotation(fig3, 'textbox', [0.005 0.005 0.21 0.12], ...
    'String', sprintf('r0 = %d mm\nalpha_max 最小: %.1f° (e=%d mm)\nalpha_mean 最小: %.1f° (e=%d mm)', ...
    r0_fix, max_min, e_vec(idx_maxmin), mean_min, e_vec(idx_meanmin)), ...
    'Color', C_txt, 'BackgroundColor', [0.17 0.17 0.22], ...
    'EdgeColor', [0.48 0.48 0.58], 'FontSize', 9.5, 'LineWidth', 1.0, 'FitBoxToText', 'off');

%% ========== 控制台汇总 ==========
fprintf('===== 图2: 各 r0 最优偏距（细扫 e 步长 0.1mm）=====\n');
fprintf('  r0    e_opt(细)   e_opt(粗)   alpha_max_min\n');
for ir = 1:length(r0_vec)
    fprintf('  %3d     %5.1f       %5.1f        %.2f°\n', ...
        r0_vec(ir), e_opt_vec(ir), e_opt_coarse(ir), alpha_opt_vec(ir));
end
fprintf('\n===== 图3: r0=%d 双指标最优偏距 =====\n', r0_fix);
fprintf('alpha_max  最小: %.2f°  (e = %d mm)\n', max_min,  e_vec(idx_maxmin));
fprintf('alpha_mean 最小: %.2f°  (e = %d mm)\n', mean_min, e_vec(idx_meanmin));

%% ================================================================
%  子函数：计算推程段压力角向量
%% ================================================================
function alpha_deg = push_alpha(r0, e, h, phi_push, N)
    if r0 <= abs(e)
        alpha_deg = NaN(1, N);
        return;
    end
    theta = linspace(1e-6, phi_push - 1e-6, N);
    s     = h * (theta/phi_push - (1/(2*pi)) * sin(2*pi*theta/phi_push));
    rho   = sqrt(r0^2 - e^2) + s;
    x_p   = rho .* sin(theta) + e * cos(theta);
    y_p   = rho .* cos(theta) - e * sin(theta);
    dx    = gradient(x_p, theta);
    dy    = gradient(y_p, theta);
    nf    = sqrt(dx.^2 + dy.^2);
    Nx    = -dy ./ nf;
    Ny    =  dx ./ nf;
    numer = (Ny./Nx) - ((-e*sin(theta) - y_p) ./ (e*cos(theta) - x_p));
    denom =  1 + (Ny./Nx) .* ((-e*sin(theta) - y_p) ./ (e*cos(theta) - x_p));
    a     = atan(abs(numer ./ denom)) * 180/pi;
    alpha_deg = min(a, 180 - a);
    alpha_deg(~isfinite(alpha_deg)) = NaN;
end