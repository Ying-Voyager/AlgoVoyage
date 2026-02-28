clc; clear;

%% ================================================
%  直动滚子推杆盘形凸轮 — 最优偏距求解器
%  运动规律：正弦加速度（推程）
%  优化目标：使推程段最大压力角最小
%% ================================================

function optimal_e = optimize_pressure_angle()
    r0 = input('请输入基圆半径 r0 (mm): ');

    % 约束：|e| < r0（几何有效性）
    lb = -(r0 - 0.01);
    ub =  (r0 - 0.01);

    initial_e = 0;
    options = optimoptions('fmincon', ...
        'Display',       'off', ...
        'Algorithm',     'interior-point', ...
        'TolX',          1e-8, ...
        'TolFun',        1e-8, ...
        'MaxIterations', 500);

    optimal_e = fmincon(@(e) target(e, r0), initial_e, ...
                        [], [], [], [], lb, ub, [], options);

    alpha_min = target(optimal_e, r0);
    fprintf('\n========== 优化结果 ==========\n');
    fprintf('基圆半径   r0      = %.4f mm\n', r0);
    fprintf('最优偏距   e_opt   = %.4f mm\n', optimal_e);
    fprintf('最小最大压力角     = %.4f °\n',  alpha_min);
    fprintf('==============================\n\n');
end

%% ---------- 目标函数：推程段最大压力角 ----------
function max_ang = target(e, r0)
    % 在推程段 [0, pi/2] 上密集采样
    deltas = linspace(1e-6, pi/2 - 1e-6, 2000);
    angles = arrayfun(@(d) pressure_angle(e, d, r0), deltas);
    max_ang = max(angles);
end

%% ---------- 解析压力角公式 ----------
% 正弦加速度推程：s(delta) = h*(delta/phi - 1/(2*pi)*sin(2*pi*delta/phi))
%   h = 15 mm, phi = pi/2
% ds/ddelta = h/phi * (1 - cos(2*pi*delta/phi))
%           = (15/(pi/2)) * (1 - cos(4*delta))
%           = (30/pi)     * (1 - cos(4*delta))
%
% 偏置直动推杆压力角公式：
%   tan(alpha) = (ds/ddelta - e) / (sqrt(r0^2 - e^2) + s)
function ang = pressure_angle(e, delta, r0)
    h   = 15;
    phi = pi/2;

    % 位移与速度（对凸轮转角的导数）
    s    = h * (delta/phi - (1/(2*pi)) * sin(2*pi*delta/phi));
    dsdd = (h/phi) * (1 - cos(2*pi*delta/phi));   % = (30/pi)*(1-cos(4*delta))

    numerator   = dsdd - e;
    denominator = sqrt(r0^2 - e^2) + s;

    if abs(denominator) < 1e-12
        ang = 90;   % 分母为零时压力角为 90°
    else
        ang = abs(atan(numerator / denominator)) * 180/pi;
    end
end

%% ---------- 主程序入口 ----------
optimal_e = optimize_pressure_angle();