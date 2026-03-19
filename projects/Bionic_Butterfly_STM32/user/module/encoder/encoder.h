#ifndef __ENCODER_H
#define __ENCODER_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

// 编码器参数定义
#define ENCODER_MAX      4095    // 编码器最大值（12位分辨率）
#define ENCODER_HALF     2048    // 编码器半量程（4096/2）
#define TARGET_MIDPOINT  2048    // 目标中点位（统一校正到2048）

// 各电机中点位定义
#define MOTOR1_MIDPOINT  910    // 电机1中点编码器值
#define MOTOR2_MIDPOINT 720    // 电机2中点编码器值  
#define MOTOR3_MIDPOINT  987     // 电机3中点编码器值
#define MOTOR4_MIDPOINT  2333    // 电机4中点编码器值

// AS5600设备地址定义
#define AS5600_ADDR_M1   0x01    // 电机1设备地址
#define AS5600_ADDR_M2   0x02    // 电机2设备地址
#define AS5600_ADDR_M3   0x03    // 电机3设备地址
#define AS5600_ADDR_M4   0x04    // 电机4设备地址

typedef struct {
    struct {
        int16_t Magnet_Flag;        // 磁编码器状态标志（0:磁铁丢失, 1:磁铁正常, 2:磁铁过强等）
        int16_t Raw_Angle;          // 原始角度值（AS5600原始编码器值，范围0-4095）
        int16_t Corrective_Angle;   // 校正后角度（经过零位校准和滤波处理后的角度）
        int16_t Target_Angle;       // 目标角度（PID控制的目标位置，单位与Corrective_Angle一致）
        int16_t Out_Chassis;        // 底盘输出值（发送给电机的控制量，通常是PWM或电流值）
        int16_t Speed;              // 电机转速（单位：RPM 或 度/秒，根据具体配置决定）
        int16_t Position;           // 电机绝对位置（累积角度值，用于记录多圈运动）
    } Wings_motor[5];   // 翅翼电机数组：[0]左前翅, [1]右前翅, [2]左后翅, [3]右后翅, [4]预留或特殊用途
    
} WINGS_DATA;

//编码器实时数据快捷接口
extern int ECD_1,ECD_2,ECD_3,ECD_4;
extern WINGS_DATA Wings_Data;


/**
 * @brief 角度转换核心函数
 * @param raw_angle 原始编码器值(0-4095)
 * @param midpoint 机械中点值
 * @return 以2048为中点的角度值(0-4095)
 */
uint16_t AngleTransform(uint16_t raw_angle, uint16_t midpoint);

/**
 * @brief 获取指定电机的机械中点值
 * @param motor_index 电机索引(0-3)
 * @return 机械中点值
 */
uint16_t GetMotorMidpoint(uint8_t motor_index);

/**
 * @brief 处理单个电机的编码器数据
 * @param motor_index 电机索引(0-3)
 * @param raw_angle 原始编码器值
 * @return 相对于目标中点2048的角度值
 */
uint16_t ProcessMotorEncoder(uint8_t motor_index, uint16_t raw_angle);

/**
 * @brief 获取原始角度数据
 * @note 遍历四个编码器，检测磁铁状态并读取原始角度值
 * @note 只有磁铁状态正常时才读取角度数据
 */
void Get_Raw_Angle(void);

/**
 * @brief 获取校正后角度数据
 * @note 对四个电机的原始角度进行中点校正处理
 */
void Get_Corrective_Angle(void);

#ifdef __cplusplus
}
#endif

#endif /* __ENCODER_H */
