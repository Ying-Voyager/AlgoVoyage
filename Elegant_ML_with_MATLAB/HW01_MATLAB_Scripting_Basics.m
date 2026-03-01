%% 1. 输入长方形的长和宽，计算长方形的周长和面积并输出
clear
clc
disp('--- 第1题：运行中 ---')
length = input('length=');
width = input('width=');
perimeter = 2*(length+width);
area = width*length;
disp('长方形的周长为:')
disp(perimeter)
disp('长方形的面积为:')
disp(area)


%% 2. 输入三角形的三条边（要满足构成三角形的条件），求三角形的周长和面积
clear
clc
disp('--- 第2题：运行中 ---')
a = input('请输入边长 a: ');
b = input('请输入边长 b: ');
c = input('请输入边长 c: ');


if a+b>c && a+c>b && b+c>a
    p = a+b+c;
    area = sqrt(p/2*(p/2-a)*(p/2-b)*(p/2-c));
    disp('三角形的周长为:')
    disp(p)
    disp('三角形的面积为:')
    disp(area)
else 
    fprintf('三角形不存在\n')
end


%% 3. 输入一元二次方程的三个系数，求一元二次方程的根
clear
clc
disp('--- 第3题：运行中 ---')
a = input('请输入二次项系数 a: ');
b = input('请输入一次项系数 b: ');
c = input('请输入常数项 c: ');

if b*b-4*a*c < 0
    fprintf('方程无实数解\n')
elseif b*b-4*a*c == 0
    root = -b/2/a;
    disp('方程有两个相等的实数根:')
    disp(root)
else
    root1 = (-b+sqrt(b*b-4*a*c))/2/a;
    root2 = (-b-sqrt(b*b-4*a*c))/2/a;
    disp('方程有两个不相等的实数根:')
    disp(root1)
    disp(root2)
end


%% 4. 给定半径，求球的体积和表面积
clear
clc
disp('--- 第4题：运行中 ---')
r = input('半径=');
V = 4/3*pi*r*r*r;
S = 4*pi*r*r;
disp('球的体积为:')
disp(V)
disp('球的表面积为:')
disp(S)


%% 5. 输入三个数，将其按照从小到大的顺序排列
clear
clc
disp('--- 第5题：运行中 ---')
a = input('请输入第1个数: ');
b = input('请输入第2个数: ');
c = input('请输入第3个数: ');
numbers = [a, b, c];
sorted = sort(numbers);
disp('从小到大排列的结果为:')
disp(sorted)