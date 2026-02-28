clc; clear; close all;

%% ========== 参数设置 ==========
h          = 15;        % 行程 (mm)
phi_push   = pi/2;      % 推程角 90°

r0_vec = 30:5:90;       % 基圆半径 [30:5:90] mm
e_vec  = -15:3:15;      % 偏置量  [-15:3:15] mm
alpha_limit = 30;       % 许用推程压力角 (°)

N_theta = 4000;         % 每组计算点数

%% ========== 遍历计算最大推程压力角 ==========
[R0_grid, E_grid] = meshgrid(r0_vec, e_vec);
Alpha_max = zeros(size(R0_grid));

fprintf('正在遍历 %d 组参数，请稍候...\n', numel(R0_grid));

for ir = 1:length(r0_vec)
    for ie = 1:length(e_vec)
        r0 = r0_vec(ir);
        e  = e_vec(ie);

        if r0 <= abs(e)
            Alpha_max(ie, ir) = NaN;
            continue;
        end

        theta = linspace(1e-6, phi_push - 1e-6, N_theta);
        s = h * (theta/phi_push - (1/(2*pi)) * sin(2*pi*theta/phi_push));

        rho = sqrt(r0^2 - e^2) + s;
        x_p = rho .* sin(theta) + e * cos(theta);
        y_p = rho .* cos(theta) - e * sin(theta);

        dx = gradient(x_p, theta);
        dy = gradient(y_p, theta);
        nf = sqrt(dx.^2 + dy.^2);
        Nx = -dy ./ nf;
        Ny =  dx ./ nf;

        numer = (Ny./Nx) - ((-e*sin(theta)-y_p)./(e*cos(theta)-x_p));
        denom = 1 + (Ny./Nx) .* ((-e*sin(theta)-y_p)./(e*cos(theta)-x_p));
        alpha_deg = atan(abs(numer ./ denom)) * 180/pi;
        alpha_deg = min(alpha_deg, 180 - alpha_deg);

        Alpha_max(ie, ir) = max(alpha_deg(isfinite(alpha_deg)));
    end
end

fprintf('计算完成！\n');

%% ========== 统计 ==========
valid_mask = ~isnan(Alpha_max);
pass_mask  = valid_mask & (Alpha_max <= alpha_limit);
[~, idx_min] = min(Alpha_max(:));

fprintf('\n========== 统计结果 ==========\n');
fprintf('有效参数组合总数       : %d\n',   sum(valid_mask(:)));
fprintf('满足 α_max ≤ %d° 的组合: %d\n',  alpha_limit, sum(pass_mask(:)));
fprintf('覆盖率                 : %.1f%%\n', 100*sum(pass_mask(:))/sum(valid_mask(:)));
fprintf('α_max 最小值           : %.2f° (r0=%.0f mm, e=%.0f mm)\n', ...
        Alpha_max(idx_min), R0_grid(idx_min), E_grid(idx_min));
fprintf('α_max 最大值           : %.2f°\n', max(Alpha_max(valid_mask)));

%% ========== 深色主题配置 ==========
C_bg   = [0.10 0.10 0.13];
C_ax   = [0.14 0.14 0.18];
C_txt  = [0.93 0.93 0.93];
C_grid = [0.38 0.38 0.44];

%% ================================================================
%  图1：全部有效数据三维曲面 + 许用压力角参考面
%% ================================================================
fig1 = figure('Color', C_bg, 'Position', [60, 60, 1160, 740], ...
              'Name', '图1：最大推程压力角三维分布（全数据）');

ax1 = axes('Parent', fig1, 'Color', C_ax, 'Position', [0.07 0.09 0.80 0.82]);
hold(ax1, 'on');

%-- 主曲面
surf(ax1, R0_grid, E_grid, Alpha_max, Alpha_max, ...
     'EdgeColor', [1 1 1], 'EdgeAlpha', 0.18, 'FaceAlpha', 0.94, 'LineWidth', 0.35);

%-- 许用压力角半透明参考平面
r0_flat = [r0_vec(1), r0_vec(end); r0_vec(1), r0_vec(end)];
e_flat  = [e_vec(1),  e_vec(1);  e_vec(end), e_vec(end)];
surf(ax1, r0_flat, e_flat, ones(2)*alpha_limit, ...
     'FaceColor', [0.95 0.22 0.18], 'FaceAlpha', 0.20, ...
     'EdgeColor', [1.0 0.42 0.38],  'EdgeAlpha', 0.65, 'LineWidth', 0.9);

%-- 底部等高线投影
z_bot1 = min(Alpha_max(valid_mask)) * 0.94;
[C1, h1] = contourf(ax1, R0_grid, E_grid, Alpha_max, 12);
% 把等高线拍到底面（z轴统一设置后再移动）
contour3(ax1, R0_grid, E_grid, Alpha_max, 12, 'LineWidth', 0.9);

%-- 颜色 & 色条
colormap(ax1, parula);
cb1 = colorbar(ax1, 'Color', C_txt);
cb1.Label.String   = 'α_{max}  (°)';
cb1.Label.Color    = C_txt;
cb1.Label.FontSize = 11;
cb1.FontSize = 10;

%-- 坐标轴样式
ax1.XColor = C_txt; ax1.YColor = C_txt; ax1.ZColor = C_txt;
ax1.GridColor = C_grid; ax1.GridAlpha = 0.32;
ax1.MinorGridAlpha = 0.14; ax1.FontSize = 10;
grid(ax1, 'on');

%-- 标签
xlabel(ax1, '基圆半径  r_0  (mm)',          'Color', C_txt, 'FontSize', 12, 'FontWeight', 'bold');
ylabel(ax1, '偏置量  e  (mm)',               'Color', C_txt, 'FontSize', 12, 'FontWeight', 'bold');
zlabel(ax1, 'α_{max}  (°)',                 'Color', C_txt, 'FontSize', 12, 'FontWeight', 'bold');
title(ax1, {'最大推程压力角  α_{max}  随  r_0  与  e  的三维分布', ...
            '正弦加速度运动规律 ｜ 推程角 90° ｜ 行程 h = 15 mm'}, ...
     'Color', [1 1 1], 'FontSize', 13, 'FontWeight', 'bold');

%-- 许用线文本
text(ax1, r0_vec(end)-2, e_vec(end)*0.7, alpha_limit+0.8, ...
     sprintf('许用压力角  α = %d°', alpha_limit), ...
     'Color', [1.0 0.55 0.52], 'FontSize', 10, 'FontWeight', 'bold', ...
     'HorizontalAlignment', 'right');

view(ax1, -42, 26);

%-- 信息标注
info1 = sprintf('有效组合:  %d\nα_{max} 最小: %.1f°\nα_{max} 最大: %.1f°\n许用线: %d°', ...
                sum(valid_mask(:)), min(Alpha_max(valid_mask)), ...
                max(Alpha_max(valid_mask)), alpha_limit);
annotation(fig1, 'textbox', [0.005, 0.005, 0.155, 0.130], ...
           'String', info1, 'Color', C_txt, ...
           'BackgroundColor', [0.17 0.17 0.22], ...
           'EdgeColor', [0.48 0.48 0.58], 'FontSize', 9.5, ...
           'LineWidth', 1.0, 'FitBoxToText', 'off');

%% ================================================================
%  图2：过滤后 — 仅保留 α_max ≤ 30° 的可用区域
%% ================================================================
Alpha_filt = Alpha_max;
Alpha_filt(Alpha_max > alpha_limit) = NaN;

fig2 = figure('Color', C_bg, 'Position', [120, 120, 1160, 740], ...
              'Name', '图2：可用参数区域（α_max ≤ 30°）');

ax2 = axes('Parent', fig2, 'Color', C_ax, 'Position', [0.07 0.09 0.80 0.82]);
hold(ax2, 'on');

%-- 可用区域曲面
surf(ax2, R0_grid, E_grid, Alpha_filt, Alpha_filt, ...
     'EdgeColor', [1 1 1], 'EdgeAlpha', 0.22, 'FaceAlpha', 0.95, 'LineWidth', 0.35);

%-- 底部等高线
contour3(ax2, R0_grid, E_grid, Alpha_filt, 10, 'LineWidth', 0.9);

%-- 在底面绘制 α_max = 30° 的边界轮廓
z_floor = min(Alpha_filt(~isnan(Alpha_filt))) * 0.93;
C_bnd = contourc(r0_vec, e_vec, Alpha_max, [alpha_limit alpha_limit]);
idx_c = 1;
first_seg = true;
while idx_c < length(C_bnd)
    n_pts = C_bnd(2, idx_c);
    xc = C_bnd(1, idx_c+1 : idx_c+n_pts);
    yc = C_bnd(2, idx_c+1 : idx_c+n_pts);
    if first_seg
        plot3(ax2, xc, yc, ones(1,n_pts)*z_floor, '-', ...
              'Color', [1.0 0.32 0.28], 'LineWidth', 2.2, ...
              'DisplayName', sprintf('边界线  α_{max} = %d°', alpha_limit));
        first_seg = false;
    else
        plot3(ax2, xc, yc, ones(1,n_pts)*z_floor, '-', ...
              'Color', [1.0 0.32 0.28], 'LineWidth', 2.2, 'HandleVisibility', 'off');
    end
    idx_c = idx_c + n_pts + 1;
end

%-- 颜色 & 色条
colormap(ax2, cool);
cb2 = colorbar(ax2, 'Color', C_txt);
cb2.Label.String   = 'α_{max}  (°)';
cb2.Label.Color    = C_txt;
cb2.Label.FontSize = 11;
cb2.FontSize = 10;

%-- 坐标轴样式
ax2.XColor = C_txt; ax2.YColor = C_txt; ax2.ZColor = C_txt;
ax2.GridColor = C_grid; ax2.GridAlpha = 0.32;
ax2.MinorGridAlpha = 0.14; ax2.FontSize = 10;
grid(ax2, 'on');

%-- 标签
xlabel(ax2, '基圆半径  r_0  (mm)',          'Color', C_txt, 'FontSize', 12, 'FontWeight', 'bold');
ylabel(ax2, '偏置量  e  (mm)',               'Color', C_txt, 'FontSize', 12, 'FontWeight', 'bold');
zlabel(ax2, 'α_{max}  (°)',                 'Color', C_txt, 'FontSize', 12, 'FontWeight', 'bold');
title(ax2, {sprintf('可用参数区域  ( α_{max} \\leq %d° )', alpha_limit), ...
            sprintf('满足条件: %d / %d 组  |  覆盖率 %.1f%%', ...
            sum(pass_mask(:)), sum(valid_mask(:)), ...
            100*sum(pass_mask(:))/sum(valid_mask(:)))}, ...
     'Color', [1 1 1], 'FontSize', 13, 'FontWeight', 'bold');

view(ax2, -42, 26);

%-- 图例
legend(ax2, 'Location', 'northeast', 'TextColor', C_txt, ...
       'Color', [0.16 0.16 0.21], 'EdgeColor', [0.5 0.5 0.6], 'FontSize', 10);

%-- 信息标注
info2 = sprintf('可用组合: %d / %d\n覆盖率: %.1f%%\nα_{max} 范围:\n  %.1f° ~ %.1f°', ...
                sum(pass_mask(:)), sum(valid_mask(:)), ...
                100*sum(pass_mask(:))/sum(valid_mask(:)), ...
                min(Alpha_filt(~isnan(Alpha_filt))), alpha_limit);
annotation(fig2, 'textbox', [0.005, 0.005, 0.155, 0.140], ...
           'String', info2, 'Color', C_txt, ...
           'BackgroundColor', [0.17 0.17 0.22], ...
           'EdgeColor', [0.48 0.48 0.58], 'FontSize', 9.5, ...
           'LineWidth', 1.0, 'FitBoxToText', 'off');

fprintf('\n两张图已生成完毕。\n');