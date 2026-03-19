#include "encoder.h"
#include "as5600.h"
#include "motor.h"
//编码器实时数据快捷接口
int ECD_1,ECD_2,ECD_3,ECD_4;
// 外部变量声明
WINGS_DATA Wings_Data;

// 电机中点配置数组
static const uint16_t motor_midpoints[4] = {
    MOTOR1_MIDPOINT,
    MOTOR2_MIDPOINT, 
    MOTOR3_MIDPOINT,
    MOTOR4_MIDPOINT
};

// AS5600设备地址数组
static const uint8_t as5600_addresses[4] = {
    AS5600_ADDR_M1,
    AS5600_ADDR_M2,
    AS5600_ADDR_M3, 
    AS5600_ADDR_M4
};

/**
 * @brief 角度转换核心函数
 */
uint16_t AngleTransform(uint16_t raw_angle, uint16_t midpoint)
{
    // 计算相对角度并归一化到 [-ENCODER_HALF, ENCODER_HALF) 范围
    int normalized = raw_angle - midpoint;
    
    // 处理角度环绕
    if (normalized > ENCODER_HALF) {
        normalized -= ENCODER_MAX;
		
    } else if (normalized < -ENCODER_HALF) {
        normalized += ENCODER_MAX;
    }
    normalized = normalized + 2048;
    return normalized;
}

/**
 * @brief 获取指定电机的机械中点值
 */
uint16_t GetMotorMidpoint(uint8_t motor_index)
{
    if (motor_index < 4) {
        return motor_midpoints[motor_index];
    }
    return TARGET_MIDPOINT;
}

/**
 * @brief 处理单个电机的编码器数据
 */
uint16_t ProcessMotorEncoder(uint8_t motor_index, uint16_t raw_angle)
{
    uint16_t midpoint = GetMotorMidpoint(motor_index);
    return AngleTransform(raw_angle, midpoint);
}

/**
 * @brief 获取原始角度数据
 */
void Get_Raw_Angle(void)
{
//    for (uint8_t i = 0; i < 4; i++) {
//        // 检测磁铁状态
//        if (detectMagnet(as5600_addresses[i]) == 1) {
//            // 磁铁正常，读取角度值
//            Wings_Data.Wings_motor[i].Raw_Angle = getRawAngle(as5600_addresses[i]);
//            Wings_Data.Wings_motor[i].Magnet_Flag = 1;  // 标记磁铁正常
//        } else {
//            // 磁铁异常，保持原值并标记
//            Wings_Data.Wings_motor[i].Magnet_Flag = 0;  // 标记磁铁异常
//        }
//    }
		ECD_1=getRawAngle(as5600_addresses[0]);
		ECD_2=getRawAngle(as5600_addresses[1]);
		ECD_3=getRawAngle(as5600_addresses[2]);
		ECD_4=getRawAngle(as5600_addresses[3]);
}

/**
 * @brief 获取校正后角度数据
 */
void Get_Corrective_Angle(void)
{
	int16_t Corrective_Angle_test;
    for (uint8_t i = 0; i < 4; i++) {
        // 只在磁铁状态正常时进行校正
        if (Wings_Data.Wings_motor[i].Magnet_Flag == 1) {
			

			Corrective_Angle_test = ProcessMotorEncoder(i, Wings_Data.Wings_motor[i].Raw_Angle);
			           if(0<Corrective_Angle_test&&Corrective_Angle_test<4096) 
					   {Wings_Data.Wings_motor[i].Corrective_Angle = Corrective_Angle_test;}
					   else
					   {
						Wings_Data.Wings_motor[i].Corrective_Angle =Wings_Data.Wings_motor[i].Corrective_Angle;
						}
        } else {
            // 磁铁异常时设置为安全值（中点）
            Wings_Data.Wings_motor[i].Corrective_Angle = TARGET_MIDPOINT;
        }
    }
}
