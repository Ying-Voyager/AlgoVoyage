#ifndef __MOTOR_H
#define __MOTOR_H


#include "pid.h"
#include "main.h"
#include "AS5600_PWM.h"
#include "stm32g0xx_hal.h"



typedef struct {
    struct {
        int16_t Magnet_Flag;        // 磁铁检测状态标志：0:磁铁丢失, 1:磁铁正常, 2:磁铁过强度
        int16_t Raw_Angle;          // 原始角度值：AS5600原始编码器值，范围0-4095
        uint16_t Corrective_Angle;   // 校正后角度：经过零位校准和滤波处理的角度
        int16_t Target_Angle;       // 目标角度：PID控制的目标位置，单位与Corrective_Angle一致
        int16_t Out_Chassis;        // 输出控制值：传递给底盘的控制量（通常为PWM控制值）
        int16_t Speed;              // 电机转速：单位：RPM 或 度/秒，根据具体设计决定
        int16_t Target_Speed;       // 目标转速：单位：RPM 或 度/秒，根据具体设计决定
        int16_t Position;           // 电机累计位置：累积角度值，用于记录多圈运动
    } Wings_motor[5];   // 支持多电机数组：[0]左前翼, [1]右前翼, [2]左后翼, [3]右后翼, [4]预留扩展电机;
    
} WINGS_DATA;

extern WINGS_DATA Wings_Data;
extern pid_type_def motor_1_pid, motor_2_pid, motor_3_pid, motor_4_pid;

#define KP 	20.0f
#define KD  00.0f

// 电机1 (左前翼) PID参数
#define MOTOR_1_SPEED_PID_KP KP
#define MOTOR_1_SPEED_PID_KI 0.0f
#define MOTOR_1_SPEED_PID_KD KD

// 电机2 (右前翼) PID参数
#define MOTOR_2_SPEED_PID_KP KP
#define MOTOR_2_SPEED_PID_KI 0.0f
#define MOTOR_2_SPEED_PID_KD KD

// 电机3 (左后翼) PID参数
#define MOTOR_3_SPEED_PID_KP KP
#define MOTOR_3_SPEED_PID_KI 0.0f
#define MOTOR_3_SPEED_PID_KD KD

// 电机4 (右后翼) PID参数
#define MOTOR_4_SPEED_PID_KP KP
#define MOTOR_4_SPEED_PID_KI 0.0f
#define MOTOR_4_SPEED_PID_KD KD

// 四驱电机布局
// M1(左前)  M3(右前)   ← 电机1,3是前翼
// M2(左后)  M4(右后)   ← 电机2,4是后翼

/*-------------Motor_PWM_M1(左前翼)--------------*/
#define PWM_M1_1 	  TIM2->CCR1	 // 电机1正转
#define PWM_M1_2 	  TIM2->CCR2	 // 电机1反转
/*------------------------------------*/

/*-------------Motor_PWM_M2(硬件位置-逻辑上M3右前翼)--------------*/
#define PWM_M2_1 	  TIM2->CCR3	 // 电机2正转
#define PWM_M2_2 	  TIM2->CCR4	 // 电机2反转
/*------------------------------------*/

/*-------------Motor_PWM_M3(硬件位置-逻辑上M2左后翼)--------------*/
#define PWM_M3_1 	  TIM3->CCR1	 // 电机3正转
#define PWM_M3_2 	  TIM3->CCR2	 // 电机3反转
/*------------------------------------*/

/*-------------Motor_PWM_M4(右后翼)--------------*/
#define PWM_M4_1 	  TIM3->CCR3	 // 电机4正转
#define PWM_M4_2 	  TIM3->CCR4	 // 电机4反转
/*------------------------------------*/

extern void Motor_PID_Control(void);
extern void Chassis_PID_Init(void);
extern void Set_Pwm(int16_t motor1_out, int16_t motor2_out, int16_t motor3_out, int16_t motor4_out);
extern uint16_t myabs(int16_t a);
extern void Motor_ECD_Control(void);
#endif
