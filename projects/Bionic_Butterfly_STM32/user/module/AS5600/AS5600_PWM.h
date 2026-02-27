#ifndef __AS5600_PWM_H__
#define __AS5600_PWM_H__
#include "main.h"
#include "adc.h"

#define MAX_VALUE 4095  // 编码范围 0~4095，编码器总值为 4096

// ====== 4个编码器的1024零位校准 ======
// 注意：这些值需要根据实际机械装配位置调整！
// 电机布局：M1(左前) M3(右前)
//           M2(左后) M4(右后)

#define MOTOR1_MIDPOINT 1024      // 电机1 左前翼 1024零位角度值
#define MOTOR2_MIDPOINT 1024     // 电机2 左后翼 1024零位角度值
#define MOTOR3_MIDPOINT 1024     // 电机3 右前翼 1024零位角度值
#define MOTOR4_MIDPOINT 1024     // 电机4 右后翼 1024零位角度值

// ====== 零位校准说明 ======
// 1. MOTOR1_MIDPOINT和MOTOR3_MIDPOINT是前翼（左右）
// 2. MOTOR2_MIDPOINT和MOTOR4_MIDPOINT是后翼（左右）
// 3. 所有电机需要根据实际装配位置校准：
//    - 进入Mode1立翅模式
//    - 观察各电机的翅膀位置
//    - 如果不在正确位置，调整相应的MOTOR_MIDPOINT值

#define PROCESS_VALUE(raw, zero) \
    (((raw) + 4096u - (((zero) + 3072u) & 0x0FFFu)) & 0x0FFFu)

extern void StarAndGetResult(void);

#endif
