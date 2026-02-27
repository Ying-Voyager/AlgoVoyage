# 四驱仿生蝴蝶 STM32 控制系统

> **作者：** Ying Qichi
> **版本：** v1.0
> **日期：** 2026-02-28
> **平台：** STM32G031G8Ux · Keil MDK-ARM · HAL 库

---

## 目录

1. [项目简介](#1-项目简介)
2. [硬件平台](#2-硬件平台)
3. [电机与编码器布局](#3-电机与编码器布局)
4. [引脚分配](#4-引脚分配)
5. [软件架构](#5-软件架构)
6. [控制模式说明](#6-控制模式说明)
7. [遥控器通道映射](#7-遥控器通道映射)
8. [飞行参数调试指南](#8-飞行参数调试指南)
9. [模块说明](#9-模块说明)
10. [注意事项](#10-注意事项)
11. [版本历史](#11-版本历史)

---

## 1. 项目简介

本项目是一套基于 **STM32G031G8Ux** 微控制器的 **四驱仿生蝴蝶** 飞行控制系统，实现了对四片翅膀的独立闭环位置控制。相比双驱版本，四驱方案为每片翅膀配备独立电机与磁编码器，大幅提升了左右前后翅的协调性与飞行稳定性。

<p align="center">
  <img src="https://github.com/user-attachments/assets/a1a48257-1a05-4f87-b83e-029d880d7a55" width="49%" />
  <img src="https://github.com/user-attachments/assets/9dc41d85-963c-4eae-aa8e-f227d0cc1621" width="49%" />
</p>

**核心特性：**

- 4 路电机独立位置闭环 PID 控制
- 4 路 AS5600 磁编码器角度反馈（软件模拟 I2C，4 路独立总线）
- ELRS/CRSF 遥控器接收（420000 baud，USART1 + DMA）
- 三种飞行模式：收翅（Mode0）、立翅（Mode1）、飞行（Mode2）
- 前后翼独立频率与相位差控制，支持俯仰姿态调节
- 左右幅度差速控制，支持转向
- HC05 蓝牙调试接口（预留）

---

## 2. 硬件平台

| 项目 | 规格 |
|------|------|
| 主控 | STM32G031G8Ux（UFQFPN28，64 MHz） |
| 电机 | 直流有刷电机 × 4 |
| 编码器 | AS5600 磁角度传感器 × 4（I2C，12位，0~4095） |
| 接收机 | ELRS 接收机（CRSF 协议，420000 baud） |
| 蓝牙模块 | HC-05（预留调试接口） |
| 开发工具 | Keil MDK-ARM v5 |
| HAL 库 | STM32G0xx HAL v1.x |

---

## 3. 电机与编码器布局

```
         机头方向 ↑
    ┌─────────────────────┐
    │  M1(左前)  M3(右前)  │
    │     [1]      [3]    │
    │                     │
    │  M2(左后)  M4(右后)  │
    │     [2]      [4]    │
    └─────────────────────┘
```

| 索引 | 电机 | 位置 | 编码器总线 | ADC 通道 | Wings_motor[] |
|------|------|------|------------|----------|---------------|
| M1 | 左前翼 | 左前 | I2C1 / ADC_CH0 | CH0 (PA0) | [0] |
| M3 | 右前翼 | 右前 | I2C3 / ADC_CH6 | CH6 (PA6) | [1] |
| M2 | 左后翼 | 左后 | I2C2 / ADC_CH1 | CH1 (PA1) | [2] |
| M4 | 右后翼 | 右后 | I2C4 / ADC_CH7 | CH7 (PA7) | [3] |

> **注意：** 由于 PCB 布线限制，`Set_Pwm()` 函数内部的 PWM 寄存器与逻辑电机编号存在交叉映射（M2↔M3），已在代码注释中明确标注，**请勿修改 `Set_Pwm()` 内部的寄存器赋值顺序**。

---

## 4. 引脚分配

### 电机 PWM 输出

| 信号 | 引脚 | 定时器通道 | 说明 |
|------|------|------------|------|
| PWM_M1_1 | PA15 | TIM2_CH1 | M1 左前翼正转 |
| PWM_M1_2 | PB3  | TIM2_CH2 | M1 左前翼反转 |
| PWM_M2_1 | PA2  | TIM2_CH3 | 硬件M2（逻辑M3右前翼正转）|
| PWM_M2_2 | PA3  | TIM2_CH4 | 硬件M2（逻辑M3右前翼反转）|
| PWM_M3_1 | PB4  | TIM3_CH1 | 硬件M3（逻辑M2左后翼正转）|
| PWM_M3_2 | PB5  | TIM3_CH2 | 硬件M3（逻辑M2左后翼反转）|
| PWM_M4_1 | PB0  | TIM3_CH3 | M4 右后翼正转 |
| PWM_M4_2 | PB1  | TIM3_CH4 | M4 右后翼反转 |

> PWM 频率：1 MHz / 20000 = **50 Hz**，占空比分辨率 20000 级。

### 编码器 ADC 输入（AS5600 PWM 模式）

| 信号 | 引脚 | ADC 通道 | 对应电机 |
|------|------|----------|----------|
| ENC1 | PA0 | ADC1_IN0 | M1 左前翼 |
| ENC2 | PA1 | ADC1_IN1 | M2 左后翼 |
| ENC3 | PA6 | ADC1_IN6 | M3 右前翼 |
| ENC4 | PA7 | ADC1_IN7 | M4 右后翼 |

> ADC 采用 DMA 批量读取，4 路同步采样。

### 软件模拟 I2C（AS5600 I2C 模式，备用）

| 总线 | SCL 引脚 | SDA 引脚 | 对应电机 |
|------|----------|----------|----------|
| I2C1 | SW_I2C1_SCL | SW_I2C1_SDA | M1 左前翼 |
| I2C2 | SW_I2C2_SCL | SW_I2C2_SDA | M2 左后翼 |
| I2C3 | SW_I2C3_SCL | SW_I2C3_SDA | M3 右前翼 |
| I2C4 | SW_I2C4_SCL | SW_I2C4_SDA | M4 右后翼 |

### 串口

| 串口 | 引脚 | 功能 | 波特率 |
|------|------|------|--------|
| USART1 TX | PB6 | 发送（预留） | 420000 |
| USART1 RX | PB7 | ELRS 接收机输入 | 420000 |

---

## 5. 软件架构

```
Bionic_Butterfly_STM32/
├── Core/
│   ├── Src/
│   │   ├── main.c          # 主程序：模式状态机、扑翼算法、PID 调用
│   │   ├── tim.c           # TIM2/TIM3 PWM 初始化（4路×2极性 = 8通道）
│   │   ├── adc.c           # ADC1 DMA 初始化（4路编码器同步采样）
│   │   ├── usart.c         # USART1 初始化（420kbaud, DMA_RX）
│   │   ├── gpio.c          # GPIO 初始化
│   │   ├── dma.c           # DMA 通道配置
│   │   └── stm32g0xx_it.c  # 中断服务程序
│   └── Inc/
│       └── main.h          # 全局宏定义、引脚定义
│
├── CRSF/
│   ├── CRSF_PROTOCOL.h     # CRSF 协议常量与结构体定义
│   ├── CRC.h / CRC.c       # CRC8 校验（多项式 0xD5）
│   └── CRSF.h / CRSF.c     # CRSF 数据包解析
│
├── user/
│   ├── bsp/
│   │   └── bsp_usart.h/c   # 串口 BSP 层（注册/发送/回调统一管理）
│   ├── struct_typedef.h    # 基础类型定义（fp32, int8_t 等）
│   └── module/
│       ├── motor/
│       │   ├── motor.h/c       # 2驱版 PID 控制（保留）
│       │   └── motor_4WD.h/c   # 4驱版 PID 控制（当前使用）
│       ├── AS5600/
│       │   ├── AS5600_PWM.h/c  # ADC 方式读取 AS5600 角度（当前使用）
│       │   └── as5600.h/c      # I2C 方式读取 AS5600（备用）
│       ├── encoder/
│       │   └── encoder.h/c     # 编码器角度校正与中点变换
│       ├── elrs/
│       │   └── elrs.h/c        # ELRS 遥控器数据解析与通道映射
│       ├── pid/
│       │   └── pid.h/c         # 位置式 / 增量式 PID 控制器
│       ├── bluetooth/
│       │   └── HC05.h/c        # HC-05 蓝牙模块驱动（预留）
│       ├── Receiver/
│       │   └── Receiver.h/c    # SBUS/CRSF 通用接收机解析（备用）
│       └── mt6816/
│           └── MT6816_SPI.h/c  # MT6816 SPI 磁编码器驱动（备用）
│
└── Drivers/                # STM32 HAL 库（ST 官方，不修改）
```

---

## 6. 控制模式说明

系统通过**通道6（拨杆B）**切换三种模式，**通道5（拨杆F）**为总开关：

### Mode 0 — 收翅模式

翅膀平滑收起至预设折叠位置，用于起降或停机状态。

- 目标角度：`motor_LF/RF/LR/RR_folded`
- PID Kp：12
- 平滑步进：每 10ms 最多移动 70 个编码器单位
- 动态 Kp 补偿：根据前后翼到目标的距离比例自动调整增益，防止一侧先到位后另一侧过冲

### Mode 1 — 立翅模式（调试 / 静态展翅）

四片翅膀竖直向上，可通过右摇杆 Y 轴（通道2）微调角度，便于校准 `_standing` 基准点。

- 目标角度：`motor_LF/RF/LR/RR_standing + elrs_data.midpoint`
- PID Kp：10
- 平滑步进：每 5ms 最多移动 70 个编码器单位

### Mode 2 — 飞行模式（扑翼）

前后翼各自独立频率，基于余弦查表（9点 Q15 定点）驱动扑翼运动。

**扑翼开关（通道8 - 拨杆8）：** 每次拨动切换「悬停水平」与「扑翼飞行」两个子状态。

#### 扑翼子状态一：悬停水平
翅膀平滑移动并保持在扑翼中心位置（`_flying` 基准点），用于飞前准备或短暂悬停调整。

#### 扑翼子状态二：扑翼飞行

| 参数 | 控制通道 | 范围 | 说明 |
|------|----------|------|------|
| 整体频率 | 左摇杆Y（CH3） | 3 ~ 10 Hz | 控制前后翼基础拍打频率 |
| 前后频率差 | 左摇杆X（CH4） | ±2 Hz | 右推=前翼加速=抬头 |
| 整体幅度 | 右摇杆Y（CH2） | 90° ~ 150° | 上推=幅度增大 |
| 左右幅度差 | 右摇杆X（CH1） | ±30° | 右推=右翼幅度减小=右转 |
| 前后相位差 | `phase_offset`（代码） | 0 ~ 8 步 | 推荐值 2（约40°） |

**扑翼算法：** 采用 9 点余弦状态机，前后翼各自维护独立状态索引，按各自频率推进步进，实现独立频率与相位差控制。

---

## 7. 遥控器通道映射

使用 ELRS 接收机，CRSF 协议。原始通道范围：174 ~ 1811，中位：992。

| 通道 | 摇杆/拨杆 | 解析范围 | 对应变量 | 功能 |
|------|-----------|----------|----------|------|
| CH1 | 右摇杆 X | -400 ~ 400 | `elrs_data.Roll` | 左右幅度差（转向） |
| CH2 | 右摇杆 Y | -80 ~ 80 | `elrs_data.midpoint` | 整体幅度 / Mode1微调角度 |
| CH3 | 左摇杆 Y | 5 ~ 15 Hz | `elrs_data.Throttle` | 扑翼频率 |
| CH4 | 左摇杆 X | -100 ~ 100 | `elrs_data.Yaw` | 前后频率差（俯仰） |
| CH5 | 拨杆F | 0 / 1 | `elrs_data.Switch` | 总启动开关（上=启动） |
| CH6 | 拨杆B | 0 / 1 / 2 | `elrs_data.Mode` | 模式选择 |
| CH8 | 拨杆8 | -100 / 100 | `elrs_data.Arm` | 扑翼切换开关（Mode2） |

> CH6 拨杆B 状态：下=Mode0收翅，中=Mode1立翅，上=Mode2飞行

---

## 8. 飞行参数调试指南

### 8.1 编码器中点校准（`AS5600_PWM.h`）

编码器中点是整个系统最基础的参数，**每次重新安装或拆卸翅膀后都需重新校准**。

```c
// AS5600_PWM.h
#define MOTOR1_MIDPOINT  1024   // M1 左前翼 — 需调整
#define MOTOR2_MIDPOINT  1024   // M2 左后翼 — 需调整
#define MOTOR3_MIDPOINT  1024   // M3 右前翼 — 需调整
#define MOTOR4_MIDPOINT  1024   // M4 右后翼 — 需调整
```

**校准步骤：**
1. 将翅膀手动拨到目标零点位置（通常为水平位置）
2. 通过调试器或串口读取 `AD_Value[0~3]` 的当前值
3. 将读取到的值分别填入对应的 `MOTOR_MIDPOINT` 宏
4. 重新编译烧录，验证 Mode1 立翅时四翼是否对齐

### 8.2 模式基准点校准（`main.c`）

```c
// Mode1 立翅基准点（竖直向上）
int16_t motor_LF_standing = 1690;  // 左前翼
int16_t motor_RF_standing = 1690;  // 右前翼
int16_t motor_LR_standing = 3150;  // 左后翼
int16_t motor_RR_standing = 3150;  // 右后翼

// Mode2 扑翼基准点（水平展开）
int16_t motor_LF_flying = 2300;
int16_t motor_RF_flying = 2300;
int16_t motor_LR_flying = 2330;
int16_t motor_RR_flying = 2330;

// Mode0 收翅基准点
int16_t motor_LF_folded = 2000;
int16_t motor_RF_folded = 2000;
int16_t motor_LR_folded = 2600;
int16_t motor_RR_folded = 2600;
```

**校准步骤：**
1. 进入 Mode1（中位拨杆B），通过右摇杆Y轴微调每个翅膀角度
2. 读取此时四个电机的 `Corrective_Angle` 值（均应在 2048 附近）
3. 将对应值填入 `_standing` 变量
4. 同理对 `_flying` 和 `_folded` 进行校准

### 8.3 PID 参数调整

当前各模式 Kp 配置：

| 模式 | Kp | Ki | Kd |
|------|----|----|-----|
| Mode0 收翅 | 12（自适应） | 0 | 0 |
| Mode1 立翅 | 10 | 0 | 0 |
| Mode2 飞行 | 30 | 0 | 0 |

全局 PID 参数在 `motor.h` 中定义：

```c
#define KP  20.0f
#define KD  00.0f
```

**调参建议：**
- 若翅膀抖动/震荡，降低 Kp 或适当增加 Kd
- 若响应迟钝，增大 Kp
- 位置误差持续存在可少量引入 Ki（建议 < 0.1）

### 8.4 扑翼相位差调整

```c
int8_t phase_offset = 2;  // main.c 中定义，范围 0~8
```

| 值 | 效果 |
|----|------|
| 0 | 前后翼完全同步 |
| 2 | 后翼滞后约 40°（推荐起飞） |
| 4 | 后翼滞后约 80°（较大俯仰力矩） |

---

## 9. 模块说明

### `motor_4WD.c` — 四驱电机 PID 控制

```c
void Chassis_PID_Init(void);   // PID 初始化，在 main() 上电后调用一次
void Motor_PID_Control(void);  // PID 计算并输出 PWM，在主循环中每帧调用
void Set_Pwm(int16_t m1, int16_t m2, int16_t m3, int16_t m4);  // 底层 PWM 写入
```

> `Set_Pwm()` 参数顺序为逻辑顺序：m1=左前, m2=左后, m3=右前, m4=右后。内部已处理硬件交叉映射。

### `AS5600_PWM.c` — 编码器角度读取

```c
void AS5600_PWM_Init(void);   // ADC 校准，上电调用一次
void StarAndGetResult(void);  // DMA 读取 4 路 ADC，更新 Wings_Data.Corrective_Angle
```

角度处理宏：
```c
// 将原始ADC值以 MIDPOINT 为零点，映射到 0~4095，中点对应 2048
#define PROCESS_VALUE(raw, zero) \
    (((raw) + 4096u - (((zero) + 3072u) & 0x0FFFu)) & 0x0FFFu)
```

### `elrs.c` — 遥控器解析

```c
void ELRS_Init(void);                      // 启动 DMA 接收
void ELRS_UARTE_RxCallback(uint16_t Size); // 空闲中断回调，解析 CRSF 帧
```

接收到的数据存储在全局结构体 `elrs_data` 中，在 `main()` 主循环直接访问。

### `pid.c` — PID 控制器

```c
void PID_init(pid_type_def *pid, uint8_t mode, const fp32 PID[3], fp32 max_out, fp32 max_iout);
fp32 PID_calc(pid_type_def *pid, fp32 ref, fp32 set);
void PID_clear(pid_type_def *pid);
```

- `mode = PID_POSITION`：位置式 PID（当前使用）
- `mode = PID_DELTA`：增量式 PID

---

## 10. 注意事项

### 🔴 硬件相关

1. **PWM 硬件交叉映射：** `Set_Pwm()` 中 m2（左后翼）输出到 `PWM_M3` 寄存器，m3（右前翼）输出到 `PWM_M2` 寄存器。这是由 PCB 布线决定的，**修改前务必确认硬件原理图**。

2. **PA2/PA3 冲突：** ADC 初始化（`HAL_ADC_MspInit`）可能覆盖 PA2/PA3 的 GPIO 模式配置。`main()` 中在 ADC 初始化后强制重新配置了 PA2/PA3 为 TIM2 复用功能，**请勿移除这段代码**。

3. **编码器方向：** M3（右前翼）和 M4（右后翼）的安装方向与左侧相反，`AS5600_PWM.c` 中已对其取反：
   ```c
   Wings_Data.Wings_motor[1].Corrective_Angle = PROCESS_VALUE(MAX_VALUE - AD_Value[2], MOTOR3_MIDPOINT);
   Wings_Data.Wings_motor[3].Corrective_Angle = PROCESS_VALUE(MAX_VALUE - AD_Value[3], MOTOR4_MIDPOINT);
   ```
   若更换编码器安装方向，需同步修改此处。

4. **TIM3 CH3/CH4 引脚：** M4 电机使用 PB0/PB1（TIM3_CH3/CH4）。如实际 PCB 使用不同引脚，需修改 `tim.c` 中 `HAL_TIM_MspPostInit()` 的 GPIO 配置。

### 🟡 软件相关

5. **编码器中点未校准时禁止上电运行：** `MOTOR_MIDPOINT` 默认值为 1024，可能导致电机启动时大角度偏转。**首次使用前必须完成编码器校准**。

6. **模式切换平滑移动：** Mode0 和 Mode1 使用带步进限制的软件滤波，确保翅膀不会因目标角度突变而猛烈动作。请勿在切换模式后立即断开电源。

7. **主循环无 RTOS：** 所有控制逻辑在裸机主循环中顺序执行，`HAL_GetTick()` 用于时间管理。如添加复杂任务需注意单次循环时间，避免扑翼状态机步进超时。

8. **`motor.h` 与 `motor_4WD.h` 同名保护宏冲突：** 两个头文件均使用 `#ifndef __MOTOR_H`，Keil 工程中同时只能包含其中一个，**当前激活文件为 `motor_4WD.c`**。

9. **AS5600 I2C 驱动（`as5600.c`）：** 目前系统使用 ADC PWM 方式读取角度（`AS5600_PWM.c`）。I2C 驱动已完整实现作为备用，如需切换需在 `main.h` 中修改 include 并重新校准时序延迟。

10. **DMA 半传输中断已关闭：** `ELRS_Init()` 和 ADC DMA 初始化后均调用了 `__HAL_DMA_DISABLE_IT(..., DMA_IT_HT)` 以防止半帧触发错误回调，**请勿删除**。

### 🟢 调试建议

11. 首次调试建议在 Keil 调试模式下实时监视 `Wings_Data.Wings_motor[0~3].Corrective_Angle`，确认四路编码器均有有效读数（0~4095 范围内，非全0也非全4095）再上电运行。

12. 遥控器连接后可先将 Mode 置于 Mode0 收翅，确认四翼缓慢运动至收翅位置后再切换至 Mode1/Mode2。

13. 第一次 Mode2 飞行时建议 `phase_offset = 0`（同步），确认前后翼均正常扑动后再逐步调大相位差。

---

## 11. 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-02-28 | 四驱版本完成，独立 PID + 独立编码器，前后翼独立频率控制 |
| v0.2 | 2026-02 | 双驱版本，前后翼共用频率，ELRS 接收机集成 |
| v0.1 | 2025 | 单驱原型验证，AS5600 I2C 编码器，SBUS 接收机 |

---

*本项目为个人实验性项目，代码与参数仅供参考，不提供任何飞行安全保证。实验时请保持安全距离，注意桨叶伤人风险。*

---

## 版权说明

Copyright © 2026 Ying Qichi. All rights reserved.

本项目所有源代码、文档及设计方案均为作者原创，受著作权法保护。

**授权范围：**

- ✅ 允许个人学习、研究与非商业用途的参考
- ✅ 允许在注明原作者及项目来源的前提下进行二次开发
- ❌ 禁止将本项目代码或设计方案用于任何商业用途



如需商业授权或有其他合作意向，请通过 GitHub Issues 联系作者。

> 本项目中 `Drivers/` 目录下的 STM32 HAL 库由 STMicroelectronics 提供，遵循其原始开源协议（BSD 3-Clause）。
