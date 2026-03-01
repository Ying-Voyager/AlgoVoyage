%% 1. 波士顿房价数据集：构建多元线性回归模型（含L2正则化）
clear
clc
close all
disp('--- 综合题：波士顿房价预测运行中 ---')

% 1. 读取数据 (推荐使用 readmatrix 替代已淘汰的 textread)
% 注意：请确保 housing.data 文件与本代码在同一文件夹下
try
    boston = readmatrix('housing.data');
catch
    disp('⚠️ 错误：未找到 housing.data 文件，请确保它在当前工作目录下！')
    return
end

[r, c] = size(boston);

% 2. 划分数据集 (80% 训练集, 20% 测试集)
% 🚀 优化：抛弃繁琐的 for 循环，使用 randperm 随机打乱索引，2行代码搞定！
tr = floor(r * 0.8);
idx = randperm(r);         % 生成 1 到 r 的随机打乱序列
train_idx = idx(1:tr);     % 前 80% 作为训练集索引
test_idx = idx(tr+1:end);  % 剩下 20% 作为测试集索引

train_x = boston(train_idx, 1:c-1);
train_y = boston(train_idx, c);
test_x = boston(test_idx, 1:c-1);
test_y = boston(test_idx, c);

% 3. L2 正则化 (岭回归 Ridge Regression)
% 题干要求 L2 正则化，原代码使用的 fitlm 只是普通最小二乘。
% k 为岭参数（正则化惩罚系数 lambda），这里设为一个典型值 0.1 演示。
k = 0.1; 
% ridge 函数返回回归系数。最后一个参数 0 表示以原始截距形式返回。
b_ridge = ridge(train_y, train_x, k, 0);

% 对测试集进行预测 (计算 y_hat = X * b + 常数项)
test_x_with_intercept = [ones(size(test_x, 1), 1), test_x]; % 补充常数项列
test_y_hat_ridge = test_x_with_intercept * b_ridge;

% 计算测试集的均方误差 MSE 
% 🚀 优化：使用动态长度替代原代码写死的 (1/56)
test_error_ridge = sum((test_y - test_y_hat_ridge).^2) / length(test_y);
fprintf('L2正则化(岭回归)的测试集均方误差(MSE)为: %.4f\n', test_error_ridge);

% 4. 绘图对比真实值与预测值
figure('Name', '波士顿房价预测对比', 'Position', [100, 100, 800, 400]);
plot(test_y, 'b-', 'LineWidth', 1.5)
hold on
plot(test_y_hat_ridge, 'r--', 'LineWidth', 1.5)

xlabel('测试样本序号')
ylabel('房屋价格')
title('真实房价 vs L2正则化(岭回归)预测房价')
legend('真实值', '模型预测值', 'Location', 'best')
grid on