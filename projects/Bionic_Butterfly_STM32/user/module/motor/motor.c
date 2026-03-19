#include "motor.h"
/**
************************************************************************************************
* @brief    四驱仿生蝴蝶运动算法
* @param    None
* @return   None
* @author   Ying Qichi 2026.3.19
************************************************************************************************
**/

// 外部调用变量
WINGS_DATA Wings_Data;

/************ 运动速度变量定义 *************/
int motor_1_set_pwm;  // M1 左前翼
int motor_2_set_pwm;  // M2 左后翼
int motor_3_set_pwm;  // M3 右前翼
int motor_4_set_pwm;  // M4 右后翼

/************ PID结构体变量定义 *************/
pid_type_def motor_1_pid, motor_2_pid, motor_3_pid, motor_4_pid;

/************** 速度PID限幅参数 *************/
const float motore_max_out = 12000, motor_max_iout = 4095; // 速度环输出限幅 积分项限幅


/**四个PID初始化**/
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

/*************** 四个PID控制 ****************/
void Motor_PID_Control(void)
{
	// ====== 交换motor_2和motor_3的PID绑定，让motor数字对应M数字 ======
	// M1 左前翼: 使用Wings_motor[0], 输出到motor_1
	Wings_Data.Wings_motor[0].Target_Speed = motor_1_set_pwm = -PID_calc(&motor_1_pid, 
		Wings_Data.Wings_motor[0].Corrective_Angle, 
		Wings_Data.Wings_motor[0].Target_Angle);
	
	// M2 左后翼: 使用Wings_motor[2], 输出到motor_2 (修改：原来是[1])
	Wings_Data.Wings_motor[2].Target_Speed = motor_2_set_pwm = -PID_calc(&motor_2_pid, 
		Wings_Data.Wings_motor[2].Corrective_Angle, 
		Wings_Data.Wings_motor[2].Target_Angle);
	
	// M3 右前翼: 使用Wings_motor[1], 输出到motor_3 (修改：原来是[2])
	// 修改：加负号，和左边保持一致
	Wings_Data.Wings_motor[1].Target_Speed = motor_3_set_pwm = -PID_calc(&motor_3_pid, 
		Wings_Data.Wings_motor[1].Corrective_Angle, 
		Wings_Data.Wings_motor[1].Target_Angle);
	
	// M4 右后翼: 使用Wings_motor[3], 输出到motor_4
	// 修改：加负号，和左边保持一致
	Wings_Data.Wings_motor[3].Target_Speed = motor_4_set_pwm = -PID_calc(&motor_4_pid, 
		Wings_Data.Wings_motor[3].Corrective_Angle, 
		Wings_Data.Wings_motor[3].Target_Angle);
	
	// 修改：改成正常顺序，不再交换motor_2和motor_3
	Set_Pwm(motor_1_set_pwm, motor_2_set_pwm, motor_3_set_pwm, motor_4_set_pwm);
}

/**************************************************************************
Function: Assign a value to the PWM register to control wing speed and direction
Input   : m1 - M1左前翼控制值, m2 - M2左后翼控制值
          m3 - M3右前翼控制值, m4 - M4右后翼控制值
Output  : none
修改后的映射关系：
       m1 → 物理motor_1 (M1左前)
       m2 → 物理motor_2 (M2左后)
       m3 → 物理motor_3 (M3右前)  
       m4 → 物理motor_4 (M4右后)
**************************************************************************/

// 分支消除的 int16 绝对值（两补码）
static inline uint16_t abs16_fast(int16_t x) {
    int16_t m = x >> 15;            // x<0 则 -1；x>=0 则 0
    return (uint16_t)((x ^ m) - m); // 等价于 abs(x)
}

void Set_Pwm(int16_t m1, int16_t m2, int16_t m3, int16_t m4)
{
    // 根据实际测试结果修正：
    // 调用：Set_Pwm(motor_1, motor_2, motor_3, motor_4)
    //                   ↑         ↑         ↑         ↑
    //                  m1        m2        m3        m4
    //
    // 实际测试发现的硬件PWM映射：
    // PWM_M1 → 左前
    // PWM_M2 → 右后  ← 注意！
    // PWM_M3 → 右前  ← 注意！
    // PWM_M4 → 左后  ← 注意！
    //
    // 修改后的目标映射：
    // m1 (motor_1) → 左前 → PWM_M1 ✓
    // m2 (motor_2) → 左后 → PWM_M4 ✓
    // m3 (motor_3) → 右前 → PWM_M3 ✓
    // m4 (motor_4) → 右后 → PWM_M2 ✓
    
    // -------- m1 → PWM_M1 (左前) --------
    uint16_t pwm1  = abs16_fast(m1);
    uint16_t mask1 = (uint16_t)-(m1 > 0);
    PWM_M1_2 = (uint16_t)(pwm1 & mask1);
    PWM_M1_1 = (uint16_t)(pwm1 & ~mask1);

    // -------- m2 → PWM_M4 (左后) --------
    uint16_t pwm2  = abs16_fast(m2);
    uint16_t mask2 = (uint16_t)-(m2 > 0);
    PWM_M4_2 = (uint16_t)(pwm2 & mask2);
    PWM_M4_1 = (uint16_t)(pwm2 & ~mask2);

    // -------- m3 → PWM_M3 (右前) --------
    uint16_t pwm3  = abs16_fast(m3);
    uint16_t mask3 = (uint16_t)-(m3 > 0);
    PWM_M3_2 = (uint16_t)(pwm3 & mask3);
    PWM_M3_1 = (uint16_t)(pwm3 & ~mask3);

    // -------- m4 → PWM_M2 (右后) --------
    uint16_t pwm4  = abs16_fast(m4);
    uint16_t mask4 = (uint16_t)-(m4 > 0);
    PWM_M2_2 = (uint16_t)(pwm4 & mask4);
    PWM_M2_1 = (uint16_t)(pwm4 & ~mask4);
}
