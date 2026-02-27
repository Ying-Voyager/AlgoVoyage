#ifndef MT6816_SPI_H
#define MT6816_SPI_H

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <spi.h>
#include <main.h>
#include <stdbool.h>

/* CS引脚选择（取消注释对应的CS，其余保持注释） */
// #define MT6816_SPI_CS_H()  HAL_GPIO_WritePin(CS1_GPIO_Port, CS1_Pin, 1)
// #define MT6816_SPI_CS_L()  HAL_GPIO_WritePin(CS1_GPIO_Port, CS1_Pin, 0)
// #define MT6816_SPI_CS_H()  HAL_GPIO_WritePin(CS2_GPIO_Port, CS2_Pin, 1)
// #define MT6816_SPI_CS_L()  HAL_GPIO_WritePin(CS2_GPIO_Port, CS2_Pin, 0)
// #define MT6816_SPI_CS_H()  HAL_GPIO_WritePin(CS3_GPIO_Port, CS3_Pin, 1)
// #define MT6816_SPI_CS_L()  HAL_GPIO_WritePin(CS3_GPIO_Port, CS3_Pin, 0)
#define MT6816_SPI_CS_H()  HAL_GPIO_WritePin(CS4_GPIO_Port, CS4_Pin, 1)  // 当前使用CS4
#define MT6816_SPI_CS_L()  HAL_GPIO_WritePin(CS4_GPIO_Port, CS4_Pin, 0)

#define MT6816_SPI_Get_HSPI  (hspi1)
#define MT6816_Mode_SPI      (0x03)

typedef struct {
    uint16_t sample_data;   // 采样原始值
    uint16_t angle;         // 角度值
    bool     no_mag_flag;   // 无磁铁标志
    bool     pc_flag;       // 奇偶校验标志
} MT6816_SPI_Signal_Typedef;

typedef struct {
    uint16_t angle_data;      // 原始角度数据
    uint16_t rectify_angle;   // 校正后角度
    bool     rectify_valid;   // 校正有效标志
} MT6816_Typedef;

extern MT6816_Typedef mt6816;

void     REIN_MT6816_SPI_Signal_Init(void);
void     RINE_MT6816_SPI_Get_AngleData(void);
float    REIN_MT6816_Get_AngleData(void);
uint32_t ReadAngle(void);

#endif
