#ifndef __ENCODER_H
#define __ENCODER_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

/* ========== 编码器参数 ========== */
#define ENCODER_MAX      4095   // 12位编码器最大值
#define ENCODER_HALF     2048   // 半程值（4096/2）
#define TARGET_MIDPOINT  2048   // 统一校准后的中点

/* ========== 各电机机械中点 ========== */
// 调试方法：手动将翅膀置于水平位置，读取对应编码器原始值填入
#define MOTOR1_MIDPOINT   910   // M1 左前翼
#define MOTOR2_MIDPOINT   720   // M2 左后翼
#define MOTOR3_MIDPOINT   987   // M3 右前翼
#define MOTOR4_MIDPOINT  2333   // M4 右后翼

/* ========== AS5600 I2C 总线编号 ========== */
#define AS5600_ADDR_M1   0x01
#define AS5600_ADDR_M2   0x02
#define AS5600_ADDR_M3   0x03
#define AS5600_ADDR_M4   0x04

typedef struct {
    struct {
        int16_t  Magnet_Flag;       // 磁铁状态：0=丢失, 1=正常, 2=过强
        int16_t  Raw_Angle;         // AS5600 原始值（0~4095）
        int16_t  Corrective_Angle;  // 校正后角度（中点对齐到2048）
        int16_t  Target_Angle;      // PID 目标角度
        int16_t  Out_Chassis;       // 底盘输出控制量
        int16_t  Speed;             // 实时转速
        int16_t  Position;          // 累计位置（多圈）
    } Wings_motor[5]; // [0]M1左前, [1]M3右前, [2]M2左后, [3]M4右后, [4]预留
} WINGS_DATA;

extern int ECD_1, ECD_2, ECD_3, ECD_4;
extern WINGS_DATA Wings_Data;

uint16_t AngleTransform(uint16_t raw_angle, uint16_t midpoint);
uint16_t GetMotorMidpoint(uint8_t motor_index);
uint16_t ProcessMotorEncoder(uint8_t motor_index, uint16_t raw_angle);
void Get_Raw_Angle(void);
void Get_Corrective_Angle(void);

#ifdef __cplusplus
}
#endif

#endif /* __ENCODER_H */
