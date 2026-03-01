%% 1. 用switch语句实现一个简单的四则运算计算器。循环10个题目，输出做对多少题。
clear
clc
disp('--- 第1题：运行中 ---')
a = zeros(1,10);
n_correct = 0; % 更改了变量名，避免与题目混淆
first_number = [3,4,5,6,7,8,9,10,11,12];
second_number = [1,2,3,4,5,6,7,8,9,10];
signs = ['+','-','+','/','*','+','-','*','+','-'];
result = [4,2,8,1.5,35,14,2,80,20,2];

disp('请按照内置题库进行输入测试：')
for i = 1:10
    fprintf('\n第 %d 题录入:\n', i);
    number1 = input('  输入第一个数: ');
    number2 = input('  输入第二个数: ');
    sign = input('  输入运算符(+,-,*,/): ', 's');
    
    % 优化了 switch 的标准写法
    switch sign
        case '+'
            a(i) = number1 + number2;
        case '-'
            a(i) = number1 - number2;
        case '*'
            a(i) = number1 * number2;
        case '/'
            a(i) = number1 / number2;
        otherwise
            disp('  运算符输入错误！')
    end
    
    % 判断是否与内置答案一致
    if a(i) == result(i)
        n_correct = n_correct + 1;
    end
end
fprintf('\n测试结束，一共做对了%d题\n', n_correct)


%% 2. 百钱买百鸡问题
% 公鸡5文钱一只，母鸡3文钱一只，小鸡3只一文钱，用100文钱买一百只鸡
clear
clc
disp('--- 第2题：运行中 ---')
a = 5;
b = 3;
c = 1/3;
disp('百钱买百鸡的方案有：')
for i = 1:20
    for j = 1:33
        if a*i + b*j + c*(100-i-j) == 100
            fprintf('公鸡%d只, 母鸡%d只, 小鸡%d只\n', i, j, 100-i-j);
        end
    end
end


%% 3. 验证哥德巴赫猜想：任何一个大于4的偶数都可以表示为两个素数的和。
clear
clc
disp('--- 第3题：运行中 ---')
n = input('输入一个大于4的偶数 n=');
for j = 2:floor(n/2)
    % 调用底部定义的 issushu 函数
    if issushu(j) && issushu(n-j)
        fprintf('%d = %d + %d\n', n, j, n-j)
        break
    end
end


%% 4. 输入一个10进制整数，转换为二进制输出。
clear
clc
disp('--- 第4题：运行中 ---')
a = input('输入一个10进制整数=');
b = dec2bin(a);
fprintf('转换为二进制为: %s\n', b)


%% 5. 斐波那契数列：求前30项
clear
clc
disp('--- 第5题：运行中 ---')
fprintf('Fibonacci sequence 前30项:\n');
for i = 1:30
    % 调用底部定义的 fibo 函数
    fprintf('%d ', fibo(i));
end
fprintf('\n');



%% ========================================================================
%  以下为脚本中调用的本地函数 (Local Functions)
%  注意：MATLAB 规定脚本中的自定义函数必须放置在整个文件的最底端
% =========================================================================

% 第3题调用的素数判断函数
function [flag] = issushu(n)
    flag = 1;
    % 优化：只需判断到 sqrt(n) 即可，提高运行效率
    for j = 2:floor(sqrt(n))
        if mod(n, j) == 0
            flag = 0;
            break
        end
    end
end

% 第5题调用的斐波那契数列计算函数
function fibo_n = fibo(n)
    if n == 1 || n == 2
        fibo_n = 1;
    else
        fibo_n = fibo(n-1) + fibo(n-2);
    end
end