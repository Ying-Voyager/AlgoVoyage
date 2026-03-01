%% 1. miRNA-疾病关联预测
clear
clc
close all
disp('--- 关联预测模型运行中，请稍候... ---')

% 1. 读取数据 (使用相对路径，确保数据和代码在同一文件夹)
try

    [~, disname] = xlsread('disease_name.xlsx'); 
    [~, mrname]  = xlsread('miRNA_name.xlsx');
    dissim = load('diseasesim.txt');
    mrsim  = load('mirsim.txt');
    known  = load('Known miRNA-disease association number.txt');
catch
    disp('⚠️ 错误：找不到文件。请确保5个数据文件都在当前 MATLAB 工作路径下！')
    return
end

% 2. 获取维度信息
[~, n] = size(dissim); % 疾病数量
[~, m] = size(mrsim);  % miRNA数量
[k, ~] = size(known);

% 3. 构建已知的关联邻接矩阵 M0 (m x n)
M0 = zeros(m, n);
idx = sub2ind([m, n], known(:, 1), known(:, 2));
M0(idx) = 1;

% 4. 构建转移概率矩阵 RD
RD = zeros(m, n);
col_sums = sum(M0, 1);
col_sums(col_sums == 0) = 1; 

for i = 1:n
    RD(:, i) = M0(:, i) / col_sums(i);
end

% 5. 组装异构网络关联大矩阵 A
A = [mrsim, RD; RD', dissim];

% 6. 计算 Katz 指标
beta = 0.01; % 
katz1 = beta * A;
katz2 = (beta^2) * (A^2);
katz3 = (beta^3) * (A^3);
katz4 = (beta^4) * (A^4);

skatz = katz1 + katz2 + katz3 + katz4;

% 7. 提取右上角的预测矩阵，并展开为列向量
predict_matrix = skatz(1:m, m+1:end);
predict_scores = predict_matrix(:);
labels = M0(:);

% 8. 绘制 ROC 曲线并输出 AUC 分数
figure('Name', '关联预测模型评估');
hold on;
auc = plot_roc(predict_scores, labels);

fprintf('\n====== 模型评估完毕 ======\n');
fprintf('当前模型的 AUC 值为: %.4f\n', auc);
fprintf('👉 预计实验得分: %.2f 分\n\n', auc * 100);


%% ========================================================================
%  本地函数：绘制 ROC 曲线并计算 AUC
% =========================================================================
function auc = plot_roc(predict, truth)
    x = 1.0;
    y = 1.0;
    pos_num = sum(truth == 1);
    neg_num = sum(truth == 0);
    x_step = 1.0 / neg_num;
    y_step = 1.0 / pos_num;
    
    % 按预测得分升序排列
    [~, index] = sort(predict);
    truth = truth(index);
    
    len = length(truth);
    X_roc = zeros(1, len + 1);
    Y_roc = zeros(1, len + 1);
    X_roc(1) = x;
    Y_roc(1) = y;
    
    for i = 1:len
        if truth(i) == 1
            y = y - y_step;
        else
            x = x - x_step;
        end
        X_roc(i+1) = x;
        Y_roc(i+1) = y;
    end

    plot(X_roc, Y_roc, '-r', 'LineWidth', 2); 
    xlabel('假阳性率 (FPR / 虚报概率)');
    ylabel('真阳性率 (TPR / 击中概率)');
    title(['Katz 算法链路预测 ROC 曲线 (AUC=', num2str(-trapz(X_roc, Y_roc), '%.4f'), ')']);
    grid on;
    
    auc = -trapz(X_roc, Y_roc);
end