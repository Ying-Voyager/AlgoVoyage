#include "encoder.h"
#include "as5600.h"
#include "motor.h"
/**
 * @brief   编码器读取与角度校正
 * @author  Ying Qichi
 */

int ECD_1, ECD_2, ECD_3, ECD_4;

WINGS_DATA Wings_Data;

static const uint16_t motor_midpoints[4] = {
    MOTOR1_MIDPOINT,
    MOTOR2_MIDPOINT,
    MOTOR3_MIDPOINT,
    MOTOR4_MIDPOINT
};

static const uint8_t as5600_addresses[4] = {
    AS5600_ADDR_M1,
    AS5600_ADDR_M2,
    AS5600_ADDR_M3,
    AS5600_ADDR_M4
};

uint16_t AngleTransform(uint16_t raw_angle, uint16_t midpoint)
{
    int normalized = raw_angle - midpoint;
    if (normalized > ENCODER_HALF)
        normalized -= ENCODER_MAX;
    else if (normalized < -ENCODER_HALF)
        normalized += ENCODER_MAX;
    return (uint16_t)(normalized + 2048);
}

uint16_t GetMotorMidpoint(uint8_t motor_index)
{
    if (motor_index < 4)
        return motor_midpoints[motor_index];
    return TARGET_MIDPOINT;
}

uint16_t ProcessMotorEncoder(uint8_t motor_index, uint16_t raw_angle)
{
    return AngleTransform(raw_angle, GetMotorMidpoint(motor_index));
}

void Get_Raw_Angle(void)
{
    ECD_1 = getRawAngle(as5600_addresses[0]);
    ECD_2 = getRawAngle(as5600_addresses[1]);
    ECD_3 = getRawAngle(as5600_addresses[2]);
    ECD_4 = getRawAngle(as5600_addresses[3]);
}

void Get_Corrective_Angle(void)
{
    int16_t Corrective_Angle_test;
    for (uint8_t i = 0; i < 4; i++)
    {
        if (Wings_Data.Wings_motor[i].Magnet_Flag == 1)
        {
            Corrective_Angle_test = ProcessMotorEncoder(i, Wings_Data.Wings_motor[i].Raw_Angle);
            if (0 < Corrective_Angle_test && Corrective_Angle_test < 4096)
                Wings_Data.Wings_motor[i].Corrective_Angle = Corrective_Angle_test;
        }
        else
        {
            Wings_Data.Wings_motor[i].Corrective_Angle = TARGET_MIDPOINT;
        }
    }
}
