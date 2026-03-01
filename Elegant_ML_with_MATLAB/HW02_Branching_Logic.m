%% 1. 输入一个四位整数，求出各位数字之和，如果该和能被3整除，输出“这个数可以被3整除”，否则输出“这个数不可以被3整除”。
clear
clc
disp('--- 第1题：运行中 ---')
n = input('输入一个四位整数=');
sum = 0;
while n ~= 0
    a = mod(n, 10);
    sum = sum + a;
    n = floor(n/10);
end
disp(['各位数字之和为: ', num2str(sum)])

if mod(sum, 3) == 0
    disp('这个数可以被3整除')
else
    disp('这个数不可以被3整除')
end


%% 2. 输入一个字符，如果是大写字母，输出其后继字符及其ASCII值，如果不是大写字母，原样输出。
% 例如，输入字符B，输出“字母B的后继字符为C，对应的ASCII码值为67”，注意字母Z的后继字符为A。
clear
clc
disp('--- 第2题：运行中 ---')
n = input('输入一个字符=','s');

% 使用 && 替代 & 更规范
if double(n) >= 65 && double(n) <= 90
    if double(n) ~= 90
        a = char(double(n) + 1);
    else
        a = 'A';
    end
    fprintf('字母%s的后继字符为%s，对应的ASCII码值为%d\n', n, a, double(a));
else
    fprintf('%s\n', n)
end


%% 3. 输入一个小于10000的整数，求出是几位数并且逆序输出。
% 例如，输入123，输出“该数为3位整数，其逆序数为321”。
clear
clc
disp('--- 第3题：运行中 ---')
n = input('输入一个小于10000的整数=');

% 优化方案：直接利用字符串处理，避免原数字在循环运算中被破坏
b = num2str(n);      % 将数字转换为字符串
a = length(b);       % 字符串的长度就是位数
c = fliplr(b);       % 翻转字符串
d = str2double(c);   % 转回数字（使用str2double比str2num更推荐）

fprintf('该数为%d位整数，其逆序数为%d\n', a, d)


%% 4. 输入学生成绩，输出该成绩的等级。
% 等级规定如下：[90，100]为A等，[80，90)为B等，[70，80)为C等，[60，70)为D等，[0，60)为E等。
clear
clc
disp('--- 第4题：运行中 ---')
n = input('输入学生成绩=');

if n < 60
    disp('成绩等级: E')
elseif n < 70
    disp('成绩等级: D')
elseif n < 80
    disp('成绩等级: C')
elseif n < 90
    disp('成绩等级: B')
else 
    disp('成绩等级: A')
end


%% 5. 商场购物打折计算。
% 100件以下不优惠，100~199件95折，200~399件90折，400~799件85折，800~1499件80折，1500件以上75折。
% 输入所购货物的单价、件数，求实际付款数目。
clear
clc
disp('--- 第5题：运行中 ---')
a = input('所购物品的单价=');
b = input('所购物品的件数=');

if b < 100
    c = 1;
elseif b < 200
    c = 0.95;
elseif b < 400
    c = 0.9;
elseif b < 800
    c = 0.85;
elseif b < 1500
    c = 0.8;
else
    c = 0.75;
end

d = a * b * c;
% 将 %d 改为 %.2f，以保留两位小数显示金额
fprintf('实际付款数目为: %.2f元\n', d)