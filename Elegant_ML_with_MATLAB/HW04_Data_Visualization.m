%% 1. 在同一图中显示正弦函数y1=sin(x)与直线y2=-x+0.5
% 要求显示标题、横坐标标签、纵坐标标签、图例，对y1、y2做文本标注。
% x取值[-2*pi,2*pi],然后通过解方程组将解在图中用星号标注
clear
clc
close all % 关闭之前的图形窗口
disp('--- 第1题：作图运行中 ---')

h = figure;
set(h, 'Name', '两条曲线', 'NumberTitle', 'Off');
x = -2*pi:0.1:2*pi;
y1 = sin(x);
y2 = -x+0.5;

h1 = plot(x, y1, 'b--');
hold on;
h2 = plot(x, y2, 'r--');

xlabel('自变量 x');
ylabel('因变量 y');
title('y1=sin(x) 与 y2=-x+0.5 的交点图');

% 求解交点 (推荐使用匿名函数 @(x) 替代旧版的字符串传参)
x0 = fzero(@(x) sin(x)+x-0.5, 0);
y0 = -x0 + 0.5;

% 标记交点
h3 = scatter(x0, y0, 100, '*', 'r'); % 加大了星号尺寸使其更明显
set(h3, 'LineWidth', 2);
legend('y1 = sin(x)', 'y2 = -x+0.5', '交点');

% 对交点及曲线做文本标注
text(x0+0.5, y0, ['交点: (', num2str(x0, '%.2f'), ', ', num2str(y0, '%.2f'), ')']);
text(pi, 0, 'y1 = sin(x)', 'Color', 'b');
text(2, -1.5, 'y2 = -x+0.5', 'Color', 'r');


%% 2. 使用4个子窗口绘制极坐标图、填充图、双y轴图和相图
% 子图1: 极坐标 r=0.5(1+cos(θ)), θ∈[0,2π]
% 子图2: 填充图 X=[0 0.2 0.8 1 0.5 0], Y=[1 0 0 1 1.8 1], 蓝色
% 子图3: 双y轴图 y1=sin(t), y2=20*cos(t), t∈[0,4π]
% 子图4: 相图 x=sin(t), y=cos(t)
clear
clc
close all
disp('--- 第2题：作图运行中 ---')
figure('Name', '四种子图展示', 'Position', [100, 100, 800, 600]);

% 子图1：极坐标图
subplot(2, 2, 1);
theta = 0:0.01:2*pi;
polarplot(theta, 0.5*(1+cos(theta)));
title('极坐标图 r=0.5(1+cos(θ))');

% 子图2：填充图
subplot(2, 2, 2);
X = [0 0.2 0.8 1 0.5 0];
Y = [1 0 0 1 1.8 1];
fill(X, Y, 'b');
title('填充图');

% 子图3：双y轴图 (优化：使用现代的 yyaxis 替代已淘汰的 plotyy)
subplot(2, 2, 3);
t = 0:0.01:4*pi;
y1 = sin(t);
y2 = 20*cos(t);

yyaxis left
plot(t, y1);
ylabel('y1 = sin(t)');

yyaxis right
plot(t, y2);
ylabel('y2 = 20*cos(t)');
title('双y轴图');
xlabel('t');

% 子图4：相图
subplot(2, 2, 4);
t = 0:0.01:4*pi;
x = sin(t);
y = cos(t);
plot(x, y);
grid on; 
title('相图');
xlabel('x = sin(t)');
ylabel('y = cos(t)');
axis equal; % 加上此句可让圆看起来更圆


%% 3. 绘制快衰减与慢衰减曲线的双Y轴图 (根据代码补充的题目)
clear
clc
close all
disp('--- 第3题：作图运行中 ---')

% 补充了分号，避免在命令行输出一大串数据
x = 0:pi/100:2*pi;
y1 = 20*exp(-0.5*x).*cos(pi*x);
y2 = 0.2*exp(-0.5*x).*cos(8*pi*x);

figure('Name', '双Y轴快慢衰减图');
yyaxis left
h1 = plot(x, y1);
set(h1, 'LineWidth', 2)
ylabel('慢衰')
ylim([-20  20])

yyaxis right 
h2 = plot(x, y2, 'g');
ylabel('快衰')
ylim([-0.2  0.2])

title('快衰减与慢衰减曲线');
legend('慢衰', '快衰')


%% 4. 不同采样步长和线型的正弦波对比图 (根据代码补充的题目)
clear
clc
close all
disp('--- 第4题：作图运行中 ---')

t1 = 0:pi/11:pi;
t2 = 0:0.01*pi:pi;
y1 = sin(t1).*sin(9*t1);
y2 = sin(t2).*sin(9*t2);

figure('Name', '采样与线型对比图', 'Position', [150, 150, 800, 600]);

subplot(2,2,1)
plot(t1, y1, 'r.', 'linewidth', 2)
title('粗采样 (点)')
axis([0, pi, -1, 1])

subplot(2,2,2)
plot(t2, y2, 'r.', 'linewidth', 2)
title('密采样 (点)')
axis([0, pi, -1, 1])

subplot(2,2,3)
plot(t1, y1, 'b-', 'linewidth', 1)
hold on
plot(t1, y1, 'r.', 'linewidth', 4)
title('粗采样 (线+点)')
axis([0, pi, -1, 1])

subplot(2,2,4)
plot(t2, y2, 'b-', 'linewidth', 1)
title('密采样 (实线)')
axis([0, pi, -1, 1])