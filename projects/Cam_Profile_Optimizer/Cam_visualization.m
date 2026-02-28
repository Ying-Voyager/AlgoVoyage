clc; clear; close all;

%% ========== 参数设置 ==========
r_0 = 30;       % 基圆半径 (mm)
e = -5;         % 偏置量 (mm)
r_roller = 4.5; % 滚子半径 (mm)

% 凸轮参数
h = 15;          % 行程 (mm)
phi_push  = pi/2;        % 推程角 90°
phi_far   = pi/3;        % 远休角 60°
phi_return = pi/2;       % 回程角 90°
phi_near  = 2*pi/3;      % 近休角 120°

%% ========== 运动规律（正弦加速度） ==========
theta = linspace(0, 2*pi, 10000);
theta_deg = theta * (180/pi);
s = zeros(size(theta));

for i = 1:length(theta)
    t = theta(i);
    if t >= 0 && t < phi_push
        % 推程：正弦加速度（修正梯形）
        s(i) = h * (t/phi_push - (1/(2*pi)) * sin(2*pi*t/phi_push));
    elseif t >= phi_push && t < phi_push + phi_far
        % 远休
        s(i) = h;
    elseif t >= phi_push + phi_far && t < phi_push + phi_far + phi_return
        % 回程：正弦加速度
        t_r = t - phi_push - phi_far;
        s(i) = h * (1 - t_r/phi_return + (1/(2*pi)) * sin(2*pi*t_r/phi_return));
    else
        % 近休
        s(i) = 0;
    end
end

% 速度（数值微分）
ds = gradient(s, theta);

%% ========== 压力角计算 ==========
% 理论轮廓线
rho = sqrt(r_0^2 - e^2) + s;
x_pitch = rho .* sin(theta) + e * cos(theta);
y_pitch = rho .* cos(theta) - e * sin(theta);

% 法向量
dx = gradient(x_pitch, theta);
dy = gradient(y_pitch, theta);
norm_factor = sqrt(dx.^2 + dy.^2);
Nx = -dy ./ norm_factor;
Ny =  dx ./ norm_factor;

% 实际轮廓线（减去滚子半径）
x_actual = x_pitch - r_roller * Nx;
y_actual = y_pitch - r_roller * Ny;

% 压力角
m1 = Ny ./ Nx;
m2 = (-e * sin(theta) - y_pitch) ./ (e * cos(theta) - x_pitch);
angle_rad = atan(abs((m1 - m2) ./ (1 + m1 .* m2)));
angle_deg = angle_rad / pi * 180;
angle_deg = min(angle_deg, 180 - angle_deg);

max_angle = max(angle_deg);
fprintf('压力角最大值为: %.2f 度\n', max_angle);

%% ========== 可视化 ==========
% 配色方案
colors = struct(...
    'push',   [0.85, 0.33, 0.10], ...
    'far',    [0.47, 0.67, 0.19], ...
    'return', [0.00, 0.45, 0.74], ...
    'near',   [0.75, 0.75, 0.75], ...
    'limit',  [0.93, 0.17, 0.17], ...
    'pitch',  [0.00, 0.45, 0.74], ...
    'actual', [0.85, 0.33, 0.10]);

% 阶段分界角度
ang_p1 = phi_push * 180/pi;
ang_p2 = (phi_push + phi_far) * 180/pi;
ang_p3 = (phi_push + phi_far + phi_return) * 180/pi;

% --------------------------------------------------------
% 图1：从动件位移与压力角综合展示
% --------------------------------------------------------
figure('Name', '凸轮从动件运动与压力角分析', ...
       'Position', [50, 50, 1200, 700], ...
       'Color', [0.97 0.97 0.97]);

% --- 子图1：位移曲线 ---
ax1 = subplot(3,1,1);
hold on; box on;

% 阶段背景
fill([0 ang_p1 ang_p1 0], [-2 -2 18 18], colors.push, 'FaceAlpha', 0.07, 'EdgeColor', 'none');
fill([ang_p1 ang_p2 ang_p2 ang_p1], [-2 -2 18 18], colors.far, 'FaceAlpha', 0.07, 'EdgeColor', 'none');
fill([ang_p2 ang_p3 ang_p3 ang_p2], [-2 -2 18 18], colors.return, 'FaceAlpha', 0.07, 'EdgeColor', 'none');
fill([ang_p3 360 360 ang_p3], [-2 -2 18 18], colors.near, 'FaceAlpha', 0.07, 'EdgeColor', 'none');

% 阶段分界线
xline(ang_p1, '--', 'Color', [0.5 0.5 0.5], 'LineWidth', 0.8);
xline(ang_p2, '--', 'Color', [0.5 0.5 0.5], 'LineWidth', 0.8);
xline(ang_p3, '--', 'Color', [0.5 0.5 0.5], 'LineWidth', 0.8);

plot(theta_deg, s, 'Color', [0.2 0.2 0.8], 'LineWidth', 2.2);

% 阶段标注
text(ang_p1/2, 16.5, '推程', 'HorizontalAlignment', 'center', ...
     'FontSize', 10, 'Color', colors.push, 'FontWeight', 'bold');
text((ang_p1+ang_p2)/2, 16.5, '远休', 'HorizontalAlignment', 'center', ...
     'FontSize', 10, 'Color', colors.far, 'FontWeight', 'bold');
text((ang_p2+ang_p3)/2, 16.5, '回程', 'HorizontalAlignment', 'center', ...
     'FontSize', 10, 'Color', colors.return, 'FontWeight', 'bold');
text((ang_p3+360)/2, 16.5, '近休', 'HorizontalAlignment', 'center', ...
     'FontSize', 10, 'Color', [0.5 0.5 0.5], 'FontWeight', 'bold');

ylabel('位移 s (mm)', 'FontSize', 11);
title(sprintf('从动件运动规律（正弦加速度）  r_0=%d mm, e=%d mm', r_0, e), ...
      'FontSize', 12, 'FontWeight', 'bold');
xlim([0 360]); ylim([-2 19]);
set(ax1, 'XTick', 0:30:360, 'FontSize', 9);
grid on; grid minor;

% --- 子图2：速度曲线 ---
ax2 = subplot(3,1,2);
hold on; box on;

fill([0 ang_p1 ang_p1 0], [-60 -60 60 60], colors.push, 'FaceAlpha', 0.07, 'EdgeColor', 'none');
fill([ang_p1 ang_p2 ang_p2 ang_p1], [-60 -60 60 60], colors.far, 'FaceAlpha', 0.07, 'EdgeColor', 'none');
fill([ang_p2 ang_p3 ang_p3 ang_p2], [-60 -60 60 60], colors.return, 'FaceAlpha', 0.07, 'EdgeColor', 'none');
fill([ang_p3 360 360 ang_p3], [-60 -60 60 60], colors.near, 'FaceAlpha', 0.07, 'EdgeColor', 'none');

xline(ang_p1, '--', 'Color', [0.5 0.5 0.5], 'LineWidth', 0.8);
xline(ang_p2, '--', 'Color', [0.5 0.5 0.5], 'LineWidth', 0.8);
xline(ang_p3, '--', 'Color', [0.5 0.5 0.5], 'LineWidth', 0.8);
yline(0, '-', 'Color', [0.6 0.6 0.6], 'LineWidth', 0.8);

plot(theta_deg, ds, 'Color', [0.2 0.7 0.3], 'LineWidth', 2.2);

ylabel('速度 ds/dθ (mm/rad)', 'FontSize', 11);
title('从动件速度（角速度归一化）', 'FontSize', 11);
xlim([0 360]);
set(ax2, 'XTick', 0:30:360, 'FontSize', 9);
grid on; grid minor;

% --- 子图3：压力角曲线 ---
ax3 = subplot(3,1,3);
hold on; box on;

y_max_plot = 50;
fill([0 ang_p1 ang_p1 0], [0 0 y_max_plot y_max_plot], colors.push, 'FaceAlpha', 0.07, 'EdgeColor', 'none');
fill([ang_p1 ang_p2 ang_p2 ang_p1], [0 0 y_max_plot y_max_plot], colors.far, 'FaceAlpha', 0.07, 'EdgeColor', 'none');
fill([ang_p2 ang_p3 ang_p3 ang_p2], [0 0 y_max_plot y_max_plot], colors.return, 'FaceAlpha', 0.07, 'EdgeColor', 'none');
fill([ang_p3 360 360 ang_p3], [0 0 y_max_plot y_max_plot], colors.near, 'FaceAlpha', 0.07, 'EdgeColor', 'none');

xline(ang_p1, '--', 'Color', [0.5 0.5 0.5], 'LineWidth', 0.8);
xline(ang_p2, '--', 'Color', [0.5 0.5 0.5], 'LineWidth', 0.8);
xline(ang_p3, '--', 'Color', [0.5 0.5 0.5], 'LineWidth', 0.8);

% 许用压力角参考线
yline(30, '--', '许用压力角 30°', 'Color', colors.limit, 'LineWidth', 1.5, ...
      'FontSize', 9, 'LabelVerticalAlignment', 'bottom');

% 压力角曲线（按阶段分色）
idx_push   = theta_deg >= 0    & theta_deg < ang_p1;
idx_far    = theta_deg >= ang_p1 & theta_deg < ang_p2;
idx_return = theta_deg >= ang_p2 & theta_deg < ang_p3;
idx_near   = theta_deg >= ang_p3;

plot(theta_deg(idx_push),   angle_deg(idx_push),   'Color', colors.push,   'LineWidth', 2.5);
plot(theta_deg(idx_far),    angle_deg(idx_far),    'Color', colors.far,    'LineWidth', 2.5);
plot(theta_deg(idx_return), angle_deg(idx_return), 'Color', colors.return, 'LineWidth', 2.5);
plot(theta_deg(idx_near),   angle_deg(idx_near),   'Color', colors.near,   'LineWidth', 2.5);

% 标注最大压力角
[~, idx_max] = max(angle_deg);
plot(theta_deg(idx_max), angle_deg(idx_max), 'v', ...
     'MarkerFaceColor', colors.limit, 'MarkerEdgeColor', 'none', 'MarkerSize', 9);
text(theta_deg(idx_max)+5, angle_deg(idx_max)+1.5, ...
     sprintf('最大 %.1f°', max_angle), ...
     'FontSize', 9, 'Color', colors.limit, 'FontWeight', 'bold');

xlabel('凸轮转角 θ (°)', 'FontSize', 11);
ylabel('压力角 α (°)', 'FontSize', 11);
title('压力角变化规律', 'FontSize', 11);
xlim([0 360]); ylim([0 y_max_plot]);
set(ax3, 'XTick', 0:30:360, 'FontSize', 9);

legend({'推程', '远休', '回程', '近休'}, ...
       'Location', 'northeast', 'FontSize', 9, 'NumColumns', 2);
grid on; grid minor;

% 统一X轴外观
linkaxes([ax1 ax2 ax3], 'x');

% --------------------------------------------------------
% 图2：凸轮轮廓线（美化版）
% --------------------------------------------------------
figure('Name', '凸轮轮廓线', 'Position', [1280, 50, 680, 650], ...
       'Color', [0.97 0.97 0.97]);
hold on; box on; axis equal;

% 基圆
th_circ = linspace(0, 2*pi, 500);
x_base = r_0 * cos(th_circ);
y_base = r_0 * sin(th_circ);
plot(x_base, y_base, '--', 'Color', [0.6 0.6 0.6], 'LineWidth', 1.0, 'DisplayName', '基圆');

% 偏置圆
r_off = abs(e);
x_off = r_off * cos(th_circ);
y_off = r_off * sin(th_circ);
plot(x_off, y_off, ':', 'Color', [0.8 0.6 0.2], 'LineWidth', 1.0, 'DisplayName', sprintf('偏置圆 e=%d', e));

% 理论轮廓（分阶段着色）
plot(x_pitch(idx_push),   y_pitch(idx_push),   'Color', colors.push,   'LineWidth', 2.2, 'DisplayName', '推程理论廓线');
plot(x_pitch(idx_far),    y_pitch(idx_far),    'Color', colors.far,    'LineWidth', 2.2, 'DisplayName', '远休理论廓线');
plot(x_pitch(idx_return), y_pitch(idx_return), 'Color', colors.return, 'LineWidth', 2.2, 'DisplayName', '回程理论廓线');
plot(x_pitch(idx_near),   y_pitch(idx_near),   'Color', colors.near,   'LineWidth', 2.2, 'DisplayName', '近休理论廓线');

% 实际轮廓
plot(x_actual, y_actual, 'k-', 'LineWidth', 1.2, 'DisplayName', '实际廓线（含滚子）');

% 滚子示意（初始位置）
theta0 = 0;
rho0 = sqrt(r_0^2 - e^2) + s(1);
xp0 = rho0 * sin(theta0) + e * cos(theta0);
yp0 = rho0 * cos(theta0) - e * sin(theta0);
th_r = linspace(0, 2*pi, 100);
plot(xp0 + r_roller*cos(th_r), yp0 + r_roller*sin(th_r), ...
     '-', 'Color', [0.4 0.4 0.4], 'LineWidth', 1.0, 'DisplayName', '滚子（θ=0）');
plot(xp0, yp0, '+', 'Color', [0.4 0.4 0.4], 'MarkerSize', 6, 'LineWidth', 1.2, 'HandleVisibility', 'off');

% 凸轮中心
plot(0, 0, 'k+', 'MarkerSize', 10, 'LineWidth', 2, 'DisplayName', '凸轮中心');

% 偏置线
plot([0, e], [0, 0], 'Color', [0.8 0.6 0.2], 'LineWidth', 1.5, 'HandleVisibility', 'off');
text(e/2, 1.5, sprintf('e=%d', e), 'HorizontalAlignment', 'center', ...
     'FontSize', 9, 'Color', [0.8 0.6 0.2]);

xlabel('X (mm)', 'FontSize', 11);
ylabel('Y (mm)', 'FontSize', 11);
title(sprintf('凸轮轮廓线  r_0=%d mm, e=%d mm, r_{roller}=%.1f mm', r_0, e, r_roller), ...
      'FontSize', 12, 'FontWeight', 'bold');
legend('Location', 'northeast', 'FontSize', 9);
grid on; grid minor;

% 坐标轴对称美化
ax = gca;
lim_val = max(max(abs(x_pitch)), max(abs(y_pitch))) * 1.15;
xlim([-lim_val lim_val]); ylim([-lim_val lim_val]);
set(ax, 'FontSize', 10);

% 添加信息文本框
info_str = sprintf('最大压力角: %.2f°\nr_0=%d mm  e=%d mm\nh=%d mm  r_r=%.1f mm', ...
                   max_angle, r_0, e, h, r_roller);
annotation('textbox', [0.72, 0.03, 0.25, 0.12], ...
           'String', info_str, 'FitBoxToText', 'on', ...
           'BackgroundColor', [1 1 0.9], 'EdgeColor', [0.6 0.6 0.3], ...
           'FontSize', 9, 'LineWidth', 1);