/*
   本代码由淘宝店提供
	 AS5600硬件购买链接：https://item.taobao.com/item.htm?spm=a1z38n.10677092.0.0.2c351debwMQV2w&id=584601996739
*/
/*******************************************************************************
* 文件名称：as5600.h
*
* 摘    要：1.采用软件模拟I2C通信协议
*           2.初始化as5600的相关设置,
* 编译环境：keil5
*******************************************************************************/

#ifndef __MD_AS5600_H
#define __MD_AS5600_H

#include "main.h"


/*******************************************************************************
* 宏定义内容：Sim_I2C1
* 变更引脚主要修改
*/
//#define SDA1_IN()（修改位置）  do { \
//  GPIO_InitTypeDef GPIO_InitStruct = {0}; \
//  GPIO_InitStruct.Pin = SW_I2C1_SDA_Pin;（修改位置） \
//  GPIO_InitStruct.Mode = GPIO_MODE_INPUT; \
//  GPIO_InitStruct.Pull = GPIO_PULLUP; \
//  HAL_GPIO_Init(SW_I2C1_SDA_GPIO_Port（修改位置）, &GPIO_InitStruct); \
//} while(0)

//#define SDA1_OUT()（修改位置） do { \
//  GPIO_InitTypeDef GPIO_InitStruct = {0}; \
//  GPIO_InitStruct.Pin = SW_I2C1_SDA_Pin（修改位置）; \
//  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD; /* 开漏输出 */ \
//  GPIO_InitStruct.Pull = GPIO_PULLUP; \
//  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_MEDIUM; \
//  HAL_GPIO_Init(SW_I2C1_SDA_GPIO_Port（修改位置）, &GPIO_InitStruct); \
//} while(0)


//#define Sim_I2C1_SCL_LOW          (SW_I2C1_SCL_GPIO_Port->ODR &= ~(SW_I2C1_SCL_Pin))（修改位置）
//#define Sim_I2C1_SCL_HIG          (SW_I2C1_SCL_GPIO_Port->ODR |=  (SW_I2C1_SCL_Pin))（修改位置）
//#define Sim_I2C1_SDA_LOW          (SW_I2C1_SDA_GPIO_Port->ODR &= ~(SW_I2C1_SDA_Pin))（修改位置）
//#define Sim_I2C1_SDA_HIG          (SW_I2C1_SDA_GPIO_Port->ODR |=  (SW_I2C1_SDA_Pin))（修改位置）

//#define Sim_I2C1_SDA_STATE        (SW_I2C1_SDA_GPIO_Port->IDR &= (SW_I2C1_SDA_Pin))（修改位置）

//#define Sim_I2C_Delay 		Sim_I2C_Delay(100000)（修改位置）
//#define Sim_I2C1_NOP		  Sim_I2C_Delay(400)  //25 （修改位置）

//#define Sim_I2C1_READY			0x00（修改位置）
//#define Sim_I2C1_BUS_BUSY		0x01（修改位置）
//#define Sim_I2C1_BUS_ERROR	0x02（修改位置）

//#define Sim_I2C1_NACK	      0x00（修改位置）
//#define Sim_I2C1_ACK				0x01（修改位置）

//#define I2C1_Direction_Transmitter 		0x00（修改位置）
//#define I2C1_Direction_Receiver   	  0x01（修改位置）

/*******************************************************************************/



/*******************************************************************************
* 宏定义内容：Sim_I2C1
*
* 摘    要：1.采用软件模拟I2C通信协议
*           2.初始化as5600的相关设置,
* 编译环境：keil5
*******************************************************************************/
#define SDA1_IN()  do { \
  GPIO_InitTypeDef GPIO_InitStruct = {0}; \
  GPIO_InitStruct.Pin = SW_I2C1_SDA_Pin; \
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT; \
  GPIO_InitStruct.Pull = GPIO_PULLUP; \
  HAL_GPIO_Init(SW_I2C1_SDA_GPIO_Port, &GPIO_InitStruct); \
} while(0)


#define SDA1_OUT() do { \
  GPIO_InitTypeDef GPIO_InitStruct = {0}; \
  GPIO_InitStruct.Pin = SW_I2C1_SDA_Pin; \
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD; /* 开漏输出 */ \
  GPIO_InitStruct.Pull = GPIO_PULLUP; \
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_MEDIUM; \
  HAL_GPIO_Init(SW_I2C1_SDA_GPIO_Port, &GPIO_InitStruct); \
} while(0)


#define Sim_I2C1_SCL_LOW          (SW_I2C1_SCL_GPIO_Port->ODR &= ~(SW_I2C1_SCL_Pin))
#define Sim_I2C1_SCL_HIG          (SW_I2C1_SCL_GPIO_Port->ODR |=  (SW_I2C1_SCL_Pin))
#define Sim_I2C1_SDA_LOW          (SW_I2C1_SDA_GPIO_Port->ODR &= ~(SW_I2C1_SDA_Pin))
#define Sim_I2C1_SDA_HIG          (SW_I2C1_SDA_GPIO_Port->ODR |=  (SW_I2C1_SDA_Pin))

#define Sim_I2C1_SDA_STATE        (SW_I2C1_SDA_GPIO_Port->IDR &= (SW_I2C1_SDA_Pin))

#define Sim_I2C1_DELAY 		Sim_I2C_Delay(100000)
#define Sim_I2C1_NOP		  Sim_I2C_Delay(25)  //25 

#define Sim_I2C1_READY			0x00
#define Sim_I2C1_BUS_BUSY		0x01
#define Sim_I2C1_BUS_ERROR	0x02

#define Sim_I2C1_NACK	      0x00
#define Sim_I2C1_ACK				0x01

#define I2C1_Direction_Transmitter 		0x00
#define I2C1_Direction_Receiver   	  0x01




/*******************************************************************************
* 宏定义内容：Sim_I2C2
*
* 摘    要：1.采用软件模拟I2C通信协议
*           2.初始化as5600的相关设置,
* 编译环境：keil5
*******************************************************************************/
#define SDA2_IN()  do { \
  GPIO_InitTypeDef GPIO_InitStruct = {0}; \
  GPIO_InitStruct.Pin = SW_I2C2_SDA_Pin; \
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT; \
  GPIO_InitStruct.Pull = GPIO_PULLUP; \
  HAL_GPIO_Init(SW_I2C2_SDA_GPIO_Port, &GPIO_InitStruct); \
} while(0)

#define SDA2_OUT() do { \
  GPIO_InitTypeDef GPIO_InitStruct = {0}; \
  GPIO_InitStruct.Pin = SW_I2C2_SDA_Pin; \
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD; /* 开漏输出 */ \
  GPIO_InitStruct.Pull = GPIO_PULLUP; \
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_MEDIUM; \
  HAL_GPIO_Init(SW_I2C2_SDA_GPIO_Port, &GPIO_InitStruct); \
} while(0)

#define Sim_I2C2_SCL_LOW          (SW_I2C2_SCL_GPIO_Port->ODR &= ~(SW_I2C2_SCL_Pin))
#define Sim_I2C2_SCL_HIG          (SW_I2C2_SCL_GPIO_Port->ODR |=  (SW_I2C2_SCL_Pin))
#define Sim_I2C2_SDA_LOW          (SW_I2C2_SDA_GPIO_Port->ODR &= ~(SW_I2C2_SDA_Pin))
#define Sim_I2C2_SDA_HIG          (SW_I2C2_SDA_GPIO_Port->ODR |=  (SW_I2C2_SDA_Pin))

#define Sim_I2C2_SDA_STATE        (SW_I2C2_SDA_GPIO_Port->IDR &= (SW_I2C2_SDA_Pin))

#define Sim_I2C2_DELAY 		Sim_I2C_Delay(100000)
#define Sim_I2C2_NOP		  Sim_I2C_Delay(25)  //25 

#define Sim_I2C2_READY			0x00
#define Sim_I2C2_BUS_BUSY		0x01
#define Sim_I2C2_BUS_ERROR	0x02

#define Sim_I2C2_NACK	      0x00
#define Sim_I2C2_ACK				0x01

#define I2C2_Direction_Transmitter 		0x00
#define I2C2_Direction_Receiver   	  0x01


/*******************************************************************************
* 宏定义内容：Sim_I2C3
*
* 摘    要：1.采用软件模拟I2C通信协议
*           2.初始化as5600的相关设置,
* 编译环境：keil5
*******************************************************************************/
#define SDA3_IN()  do { \
  GPIO_InitTypeDef GPIO_InitStruct = {0}; \
  GPIO_InitStruct.Pin = SW_I2C3_SDA_Pin; \
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT; \
  GPIO_InitStruct.Pull = GPIO_PULLUP; \
  HAL_GPIO_Init(SW_I2C3_SDA_GPIO_Port, &GPIO_InitStruct); \
} while(0)

#define SDA3_OUT() do { \
  GPIO_InitTypeDef GPIO_InitStruct = {0}; \
  GPIO_InitStruct.Pin = SW_I2C3_SDA_Pin; \
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD; /* 开漏输出 */ \
  GPIO_InitStruct.Pull = GPIO_PULLUP; \
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_MEDIUM; \
  HAL_GPIO_Init(SW_I2C3_SDA_GPIO_Port, &GPIO_InitStruct); \
} while(0)

#define Sim_I2C3_SCL_LOW          (SW_I2C3_SCL_GPIO_Port->ODR &= ~(SW_I2C3_SCL_Pin))
#define Sim_I2C3_SCL_HIG          (SW_I2C3_SCL_GPIO_Port->ODR |=  (SW_I2C3_SCL_Pin))
#define Sim_I2C3_SDA_LOW          (SW_I2C3_SDA_GPIO_Port->ODR &= ~(SW_I2C3_SDA_Pin))
#define Sim_I2C3_SDA_HIG          (SW_I2C3_SDA_GPIO_Port->ODR |=  (SW_I2C3_SDA_Pin))

#define Sim_I2C3_SDA_STATE        (SW_I2C3_SDA_GPIO_Port->IDR &= (SW_I2C3_SDA_Pin))

#define Sim_I2C3_DELAY 		Sim_I2C_Delay(100000)
#define Sim_I2C3_NOP		  Sim_I2C_Delay(400)  //25 

#define Sim_I2C3_READY			0x00
#define Sim_I2C3_BUS_BUSY		0x01
#define Sim_I2C3_BUS_ERROR	0x02

#define Sim_I2C3_NACK	      0x00
#define Sim_I2C3_ACK				0x01

#define I2C3_Direction_Transmitter 		0x00
#define I2C3_Direction_Receiver   	  0x01

/*******************************************************************************
* 宏定义内容：Sim_I2C4
*
* 摘    要：1.采用软件模拟I2C通信协议
*           2.初始化as5600的相关设置,
* 编译环境：keil5
*******************************************************************************/
#define SDA4_IN()  do { \
  GPIO_InitTypeDef GPIO_InitStruct = {0}; \
  GPIO_InitStruct.Pin = SW_I2C4_SDA_Pin; \
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT; \
  GPIO_InitStruct.Pull = GPIO_PULLUP; \
  HAL_GPIO_Init(SW_I2C4_SDA_GPIO_Port, &GPIO_InitStruct); \
} while(0)

#define SDA4_OUT() do { \
  GPIO_InitTypeDef GPIO_InitStruct = {0}; \
  GPIO_InitStruct.Pin = SW_I2C4_SDA_Pin; \
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD; /* 开漏输出 */ \
  GPIO_InitStruct.Pull = GPIO_PULLUP; \
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_MEDIUM; \
  HAL_GPIO_Init(SW_I2C4_SDA_GPIO_Port, &GPIO_InitStruct); \
} while(0)

#define Sim_I2C4_SCL_LOW          (SW_I2C4_SCL_GPIO_Port->ODR &= ~(SW_I2C4_SCL_Pin))
#define Sim_I2C4_SCL_HIG          (SW_I2C4_SCL_GPIO_Port->ODR |=  (SW_I2C4_SCL_Pin))
#define Sim_I2C4_SDA_LOW          (SW_I2C4_SDA_GPIO_Port->ODR &= ~(SW_I2C4_SDA_Pin))
#define Sim_I2C4_SDA_HIG          (SW_I2C4_SDA_GPIO_Port->ODR |=  (SW_I2C4_SDA_Pin))

#define Sim_I2C4_SDA_STATE        (SW_I2C4_SDA_GPIO_Port->IDR &= (SW_I2C4_SDA_Pin))

#define Sim_I2C4_DELAY 		Sim_I2C_Delay(100000)
#define Sim_I2C4_NOP		  Sim_I2C_Delay(400)  //25 

#define Sim_I2C4_READY			0x00
#define Sim_I2C4_BUS_BUSY		0x01
#define Sim_I2C4_BUS_ERROR	0x02

#define Sim_I2C4_NACK	      0x00
#define Sim_I2C4_ACK				0x01

#define I2C4_Direction_Transmitter 		0x00
#define I2C4_Direction_Receiver   	  0x01

/*******************************************************************************/

#define AS5600_ADDRESS_MAG           0x36

typedef enum
{
/* set i2c address */ 
  _ams5600_Address = 0x36,
  _zmco = 0x00,
  _zpos_hi = 0x01,
  _zpos_lo = 0x02,
  _mpos_hi = 0x03,
  _mpos_lo = 0x04,
  _mang_hi = 0x05,
  _mang_lo = 0x06,
  _conf_hi = 0x07,    
  _conf_lo = 0x08,
  _raw_ang_hi = 0x0c,
  _raw_ang_lo = 0x0d,
  _ang_hi = 0x0e,
  _ang_lo = 0x0f,
  _stat = 0x0b,
  _agc = 0x1a,
  _mag_hi = 0x1b,
  _mag_lo = 0x1c,
  _burn = 0xff
}AMS5600Registers_t;


//void PrintMenu(void);
uint8_t detectMagnet(uint8_t i2c_bus_id);
int16_t getRawAngle(uint8_t i2c_bus_id);


#endif 
		
