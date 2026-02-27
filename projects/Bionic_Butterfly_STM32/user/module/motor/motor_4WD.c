#include "motor.h"
/**
 * @brief   四驱仿生蝴蝶运动算法
 * @author  Ying Qichi
 */

WINGS_DATA Wings_Data;

int motor_1_set_pwm;  // M1 左前翼
int motor_2_set_pwm;  // M2 左后翼
int motor_3_set_pwm;  // M3 右前翼
int motor_4_set_pwm;  // M4 右后翼

pid_type_def motor_1_pid, motor_2_pid, motor_3_pid, motor_4_pid;

const float motore_max_out = 12000, motor_max_iout = 4095;


void Chassis_PID_Init(void) 
{
	const float motor_1_speed_pid[3] = {MOTOR_1_SPEED_PID_KP, MOTOR_1_SPEED_PID_KI, MOTOR_1_SPEED_PID_KD};
	const float motor_2_speed_pid[3] = {MOTOR_2_SPEED_PID_KP, MOTOR_2_SPEED_PID_KI, MOTOR_2_SPEED_PID_KD};
	const float motor_3_speed_pid[3] = {MOTOR_3_SPEED_PID_KP, MOTOR_3_SPEED_PID_KI, MOTOR_3_SPEED_PID_KD};
	const float motor_4_speed_pid[3] = {MOTOR_4_SPEED_PID_KP, MOTOR_4_SPEED_PID_KI, MOTOR_4_SPEED_PID_KD};
	
	PID_init(&motor_1_pid, PID_POSITION, motor_1_speed_pid, motore_max_out, motor_max_iout);
	PID_init(&motor_2_pid, PID_POSITION, motor_2_speed_pid, motore_max_out, motor_max_iout);
	PID_init(&motor_3_pid, PID_POSITION, motor_3_speed_pid, motore_max_out, motor_max_iout);
	PID_init(&motor_4_pid, PID_POSITION, motor_4_speed_pid, motore_max_out, motor_max_iout);
}

void Motor_PID_Control(void)
{
	// M1 左前翼
	Wings_Data.Wings_motor[0].Target_Speed = motor_1_set_pwm = -PID_calc(&motor_1_pid, 
		Wings_Data.Wings_motor[0].Corrective_Angle, 
		Wings_Data.Wings_motor[0].Target_Angle);
	
	// M2 左后翼
	Wings_Data.Wings_motor[2].Target_Speed = motor_2_set_pwm = -PID_calc(&motor_2_pid, 
		Wings_Data.Wings_motor[2].Corrective_Angle, 
		Wings_Data.Wings_motor[2].Target_Angle);
	
	// M3 右前翼
	Wings_Data.Wings_motor[1].Target_Speed = motor_3_set_pwm = PID_calc(&motor_3_pid, 
		Wings_Data.Wings_motor[1].Corrective_Angle, 
		Wings_Data.Wings_motor[1].Target_Angle);
	
	// M4 右后翼
	Wings_Data.Wings_motor[3].Target_Speed = motor_4_set_pwm = PID_calc(&motor_4_pid, 
		Wings_Data.Wings_motor[3].Corrective_Angle, 
		Wings_Data.Wings_motor[3].Target_Angle);
	
	Set_Pwm(motor_1_set_pwm, motor_2_set_pwm, motor_3_set_pwm, motor_4_set_pwm);
}

static inline uint16_t abs16_fast(int16_t x) {
    int16_t m = x >> 15;
    return (uint16_t)((x ^ m) - m);
}

// 电机布局：M1(左前) M3(右前) / M2(左后) M4(右后)
// 参数映射：m1→左前(TIM2 CH1/2), m2→左后(PWM_M3), m3→右前(PWM_M2), m4→右后(TIM3 CH3/4)
void Set_Pwm(int16_t m1, int16_t m2, int16_t m3, int16_t m4)
{
    // M1 左前翼
    uint16_t pwm1  = abs16_fast(m1);
    uint16_t mask1 = (uint16_t)-(m1 > 0);
    PWM_M1_2 = (uint16_t)(pwm1 & mask1);
    PWM_M1_1 = (uint16_t)(pwm1 & ~mask1);

    // M2 左后翼（输出到PWM_M3）
    uint16_t pwm2  = abs16_fast(m2);
    uint16_t mask2 = (uint16_t)-(m2 > 0);
    PWM_M3_2 = (uint16_t)(pwm2 & mask2);
    PWM_M3_1 = (uint16_t)(pwm2 & ~mask2);

    // M3 右前翼（输出到PWM_M2）
    uint16_t pwm3  = abs16_fast(m3);
    uint16_t mask3 = (uint16_t)-(m3 > 0);
    PWM_M2_2 = (uint16_t)(pwm3 & mask3);
    PWM_M2_1 = (uint16_t)(pwm3 & ~mask3);

    // M4 右后翼
    uint16_t pwm4  = abs16_fast(m4);
    uint16_t mask4 = (uint16_t)-(m4 > 0);
    PWM_M4_2 = (uint16_t)(pwm4 & mask4);
    PWM_M4_1 = (uint16_t)(pwm4 & ~mask4);
}
