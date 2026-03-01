%% 1. SVM分类鸢尾花数据集，绘制ROC曲线并计算AUC
clear
clc
close all
disp('--- 综合题：SVM分类与ROC曲线运行中 ---')

% 1. 加载并准备数据
load fisheriris
% 取前两类数据 (1:100行), 提取前两个特征做演示
X = meas(1:100, 1:2);
% 生成标签：前50个为0，后50个为1
Y = [zeros(50, 1); ones(50, 1)];
r = size(X, 1);

% 2. 随机划分数据集 (80% 训练，20% 测试)
% 🚀 优化：使用 randperm 两行代码实现随机抽取
tr = floor(r * 0.8);
idx = randperm(r);
train_idx = idx(1:tr);
test_idx = idx(tr+1:end);

train_x = X(train_idx, :);
train_y = Y(train_idx);
test_x = X(test_idx, :);
test_y = Y(test_idx);

% 3. 训练 SVM 分类器
% 🚀 优化：使用现代的 fitcsvm 替代已被淘汰的 svmtrain
% 'Standardize', true 建议开启，有利于 SVM 寻找最佳超平面
svmmodel = fitcsvm(train_x, train_y, 'Standardize', true);

% 4. 预测并获取打分 (用于绘制真正意义上的 ROC 曲线)
% 🚀 优化：predict 替代 svmclassify。
% 获取分数(y_predict_score 的第二列，即预测为正类的得分)，这是画 ROC 的关键！
[y_predict_label, y_predict_score] = predict(svmmodel, test_x);
scores = y_predict_score(:, 2); 

% 输出简单的预测结果对比
disp('部分测试集预测结果 vs 真实标签 [预测值, 真实值]:')
disp([y_predict_label(1:5), test_y(1:5)]) % 仅展示前5个防止刷屏

% 5. 绘制 ROC 曲线并计算 AUC
figure('Name', 'SVM - ROC曲线');
hold on;
% 调用底部自定义函数 (传入连续的得分 scores 而不是离散的 label 0/1)
auc = plot_roc(scores, test_y);
fprintf('计算得到的 AUC 值为: %.4f\n', auc);


%% ========================================================================
%  以下为脚本中调用的本地函数
% =========================================================================

function auc = plot_roc(predict_scores, truth)
    % 修正后的自定义 ROC 绘制函数
    x = 1.0;
    y = 1.0;
    pos_num = sum(truth == 1);
    neg_num = sum(truth == 0);
    x_step = 1.0 / neg_num;
    y_step = 1.0 / pos_num;
    
    % 按照预测得分进行排序
    [~, index] = sort(predict_scores);
    truth = truth(index);
    
    % 初始化绘图数组，多留一个起始点 (1,1)
    X_roc = zeros(1, length(truth) + 1);
    Y_roc = zeros(1, length(truth) + 1);
    X_roc(1) = x;
    Y_roc(1) = y;
    
    for i = 1:length(truth)
        if truth(i) == 1
            y = y - y_step;
        else
            x = x - x_step;
        end
        X_roc(i+1) = x;
        Y_roc(i+1) = y;
    end
    
    % 绘图优化
    plot(X_roc, Y_roc, '-ro', 'LineWidth', 2, 'MarkerSize', 4);
    xlabel('假阳性率 (FPR / 虚报概率)');
    ylabel('真阳性率 (TPR / 击中概率)');
    title('SVM 分类器 ROC 曲线');
    grid on;
    
    % 计算 AUC (梯形法则)
    auc = -trapz(X_roc, Y_roc);
end