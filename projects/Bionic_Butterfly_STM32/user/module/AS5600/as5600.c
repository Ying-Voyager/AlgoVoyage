/*
	 AS5600硬件
*/
/*******************************************************************************
* 文件名称：as5600.c
*
* 摘    要：1.采用软件模拟I2C通信协议
*           2.初始化as5600的相关设置,
*
* 当前版本：
* 作    者：子	
* 日    期：2018/12/31
* 编译环境：keil5
*
* 历史信息：
*******************************************************************************/
#include "as5600.h"
#include <stdio.h>


uint16_t _rawStartAngle=0;
uint16_t _zPosition=0;
uint16_t _rawEndAngle=0;
uint16_t _mPosition=0;
uint16_t _maxAngle=0;	
/*******************************************************************************/
/**
  * @brief  模拟IIC延时
  * @param
  * @note
  * @retval void
  * @author 子
  */
void Sim_I2C_Delay(uint32_t delay)
{
	while(--delay);	//dly=100: 8.75us; dly=100: 85.58 us (SYSCLK=72MHz)
}

/**
  * @brief  模拟IIC开始时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
uint8_t Sim_I2C1_START(void)
{
	SDA1_OUT();
	Sim_I2C1_SDA_HIG;
	Sim_I2C1_SCL_HIG;
	Sim_I2C1_NOP;

// if(!Sim_I2C1_SDA_STATE) return Sim_I2C1_BUS_BUSY;

	Sim_I2C1_SDA_LOW;
	Sim_I2C1_NOP;

	Sim_I2C1_SCL_LOW;
	Sim_I2C1_NOP;

	//if(Sim_I2C1_SDA_STATE) return Sim_I2C1_BUS_ERROR;

	return Sim_I2C1_READY;
}

/**
  * @brief  模拟IIC停止时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
void Sim_I2C1_STOP(void)
{
	SDA1_OUT();
	Sim_I2C1_SCL_LOW;
	Sim_I2C1_SDA_LOW;
	Sim_I2C1_NOP;

//	Sim_I2C1_SCL_LOW;
//  Sim_I2C1_NOP;

	Sim_I2C1_SCL_HIG;
	Sim_I2C1_SDA_HIG;
	Sim_I2C1_NOP;
}

unsigned char Sim_I2C1_Wait_Ack(void)
{
	volatile unsigned char ucErrTime=0;
	SDA1_IN();
	Sim_I2C1_SDA_HIG;
	Sim_I2C1_NOP;;
	Sim_I2C1_SCL_HIG;
	Sim_I2C1_NOP;;
	while(Sim_I2C1_SDA_STATE)
	{
		ucErrTime++;
		if(ucErrTime>250)
		{
			Sim_I2C1_STOP();
			return 1;
		}
	}
	Sim_I2C1_SCL_LOW;
	return Sim_I2C1_READY;
}

/**
  * @brief  模拟IIC应答时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
void Sim_I2C1_SendACK(void)
{
	Sim_I2C1_SCL_LOW;
	SDA1_OUT();
	Sim_I2C1_SDA_LOW;
	Sim_I2C1_NOP;
	Sim_I2C1_SCL_HIG;
	Sim_I2C1_NOP;
	Sim_I2C1_SCL_LOW;
	Sim_I2C1_NOP;
}

/**
  * @brief  模拟IIC无应答时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
void Sim_I2C1_SendNACK(void)
{
	Sim_I2C1_SCL_LOW;
	SDA1_OUT();
	Sim_I2C1_SDA_HIG;
	Sim_I2C1_NOP;
	Sim_I2C1_SCL_HIG;
	Sim_I2C1_NOP;
	Sim_I2C1_SCL_LOW;
	Sim_I2C1_NOP;
}

/**
  * @brief  模拟IIC发送单字节时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
uint8_t Sim_I2C1_SendByte(uint8_t Sim_i2c_data)
{
	uint8_t i;
	SDA1_OUT();
	Sim_I2C1_SCL_LOW;
	for(i=0; i<8; i++)
	{
		if(Sim_i2c_data&0x80) Sim_I2C1_SDA_HIG;
		else Sim_I2C1_SDA_LOW;

		Sim_i2c_data<<=1;
		Sim_I2C1_NOP;

		Sim_I2C1_SCL_HIG;
		Sim_I2C1_NOP;
		Sim_I2C1_SCL_LOW;
		Sim_I2C1_NOP;
	}
	return Sim_I2C1_READY;
}

/**
  * @brief  模拟IIC读单字节，无应答
  * @param
  * @note
  * @retval void
  * @author 子
  */
uint8_t Sim_I2C1_ReceiveByte(void)
{
	uint8_t i,Sim_i2c_data;
	SDA1_IN();
	//Sim_I2C1_SDA_HIG;
// Sim_I2C1_SCL_LOW;
	Sim_i2c_data=0;

	for(i=0; i<8; i++)
	{
		Sim_I2C1_SCL_LOW;
		Sim_I2C1_NOP;
		Sim_I2C1_SCL_HIG;
		// Sim_I2C1_NOP;
		Sim_i2c_data<<=1;

		if(Sim_I2C1_SDA_STATE)	Sim_i2c_data|=0x01;

		// Sim_I2C1_SCL_LOW;
		Sim_I2C1_NOP;
	}
	Sim_I2C1_SendNACK();
	return Sim_i2c_data;
}

/**
  * @brief  模拟IIC读单字节，带应答
  * @param
  * @note
  * @retval void
  * @author 子
  */
uint8_t Sim_I2C1_ReceiveByte_WithACK(void)
{

	uint8_t i,Sim_i2c_data;
	SDA1_IN();
	//Sim_I2C1_SDA_HIG;
// Sim_I2C1_SCL_LOW;
	Sim_i2c_data=0;

	for(i=0; i<8; i++)
	{
		Sim_I2C1_SCL_LOW;
		Sim_I2C1_NOP;
		Sim_I2C1_SCL_HIG;
		// Sim_I2C1_NOP;
		Sim_i2c_data<<=1;

		if(Sim_I2C1_SDA_STATE)	Sim_i2c_data|=0x01;

		// Sim_I2C1_SCL_LOW;
		Sim_I2C1_NOP;
	}
	Sim_I2C1_SendACK();
	return Sim_i2c_data;
}

/**
  * @brief  模拟IIC开始时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
uint8_t Sim_I2C2_START(void)
{
	SDA2_OUT();
	Sim_I2C2_SDA_HIG;
	Sim_I2C2_SCL_HIG;
	Sim_I2C2_NOP;

// if(!Sim_I2C2_SDA_STATE) return Sim_I2C2_BUS_BUSY;

	Sim_I2C2_SDA_LOW;
	Sim_I2C2_NOP;

	Sim_I2C2_SCL_LOW;
	Sim_I2C2_NOP;

	//if(Sim_I2C2_SDA_STATE) return Sim_I2C2_BUS_ERROR;

	return Sim_I2C2_READY;
}

/**
  * @brief  模拟IIC停止时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
void Sim_I2C2_STOP(void)
{
	SDA2_OUT();
	Sim_I2C2_SCL_LOW;
	Sim_I2C2_SDA_LOW;
	Sim_I2C2_NOP;

//	Sim_I2C2_SCL_LOW;
//  Sim_I2C2_NOP;

	Sim_I2C2_SCL_HIG;
	Sim_I2C2_SDA_HIG;
	Sim_I2C2_NOP;
}

unsigned char Sim_I2C2_Wait_Ack(void)
{
	volatile unsigned char ucErrTime=0;
	SDA2_IN();
	Sim_I2C2_SDA_HIG;
	Sim_I2C2_NOP;;
	Sim_I2C2_SCL_HIG;
	Sim_I2C2_NOP;;
	while(Sim_I2C2_SDA_STATE)
	{
		ucErrTime++;
		if(ucErrTime>250)
		{
			Sim_I2C2_STOP();
			return 1;
		}
	}
	Sim_I2C2_SCL_LOW;
	return Sim_I2C2_READY;
}

/**
  * @brief  模拟IIC应答时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
void Sim_I2C2_SendACK(void)
{
	Sim_I2C2_SCL_LOW;
	SDA2_OUT();
	Sim_I2C2_SDA_LOW;
	Sim_I2C2_NOP;
	Sim_I2C2_SCL_HIG;
	Sim_I2C2_NOP;
	Sim_I2C2_SCL_LOW;
	Sim_I2C2_NOP;
}

/**
  * @brief  模拟IIC无应答时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
void Sim_I2C2_SendNACK(void)
{
	Sim_I2C2_SCL_LOW;
	SDA2_OUT();
	Sim_I2C2_SDA_HIG;
	Sim_I2C2_NOP;
	Sim_I2C2_SCL_HIG;
	Sim_I2C2_NOP;
	Sim_I2C2_SCL_LOW;
	Sim_I2C2_NOP;
}

/**
  * @brief  模拟IIC发送单字节时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
uint8_t Sim_I2C2_SendByte(uint8_t Sim_i2c_data)
{
	uint8_t i;
	SDA2_OUT();
	Sim_I2C2_SCL_LOW;
	for(i=0; i<8; i++)
	{
		if(Sim_i2c_data&0x80) Sim_I2C2_SDA_HIG;
		else Sim_I2C2_SDA_LOW;

		Sim_i2c_data<<=1;
		Sim_I2C2_NOP;

		Sim_I2C2_SCL_HIG;
		Sim_I2C2_NOP;
		Sim_I2C2_SCL_LOW;
		Sim_I2C2_NOP;
	}
	return Sim_I2C2_READY;
}

/**
  * @brief  模拟IIC读单字节，无应答
  * @param
  * @note
  * @retval void
  * @author 子
  */
uint8_t Sim_I2C2_ReceiveByte(void)
{
	uint8_t i,Sim_i2c_data;
	SDA2_IN();
	//Sim_I2C2_SDA_HIG;
// Sim_I2C2_SCL_LOW;
	Sim_i2c_data=0;

	for(i=0; i<8; i++)
	{
		Sim_I2C2_SCL_LOW;
		Sim_I2C2_NOP;
		Sim_I2C2_SCL_HIG;
		// Sim_I2C2_NOP;
		Sim_i2c_data<<=1;

		if(Sim_I2C2_SDA_STATE)	Sim_i2c_data|=0x01;

		// Sim_I2C2_SCL_LOW;
		Sim_I2C2_NOP;
	}
	Sim_I2C2_SendNACK();
	return Sim_i2c_data;
}

/**
  * @brief  模拟IIC读单字节，带应答
  * @param
  * @note
  * @retval void
  * @author 子
  */
uint8_t Sim_I2C2_ReceiveByte_WithACK(void)
{

	uint8_t i,Sim_i2c_data;
	SDA2_IN();
	//Sim_I2C2_SDA_HIG;
// Sim_I2C2_SCL_LOW;
	Sim_i2c_data=0;

	for(i=0; i<8; i++)
	{
		Sim_I2C2_SCL_LOW;
		Sim_I2C2_NOP;
		Sim_I2C2_SCL_HIG;
		// Sim_I2C2_NOP;
		Sim_i2c_data<<=1;

		if(Sim_I2C2_SDA_STATE)	Sim_i2c_data|=0x01;

		// Sim_I2C2_SCL_LOW;
		Sim_I2C2_NOP;
	}
	Sim_I2C2_SendACK();
	return Sim_i2c_data;
}

/**
  * @brief  模拟IIC开始时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
uint8_t Sim_I2C3_START(void)
{
	SDA3_OUT();
	Sim_I2C3_SDA_HIG;
	Sim_I2C3_SCL_HIG;
	Sim_I2C3_NOP;

// if(!Sim_I2C3_SDA_STATE) return Sim_I2C3_BUS_BUSY;

	Sim_I2C3_SDA_LOW;
	Sim_I2C3_NOP;

	Sim_I2C3_SCL_LOW;
	Sim_I2C3_NOP;

	//if(Sim_I2C3_SDA_STATE) return Sim_I2C3_BUS_ERROR;

	return Sim_I2C3_READY;
}

/**
  * @brief  模拟IIC停止时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
void Sim_I2C3_STOP(void)
{
	SDA3_OUT();
	Sim_I2C3_SCL_LOW;
	Sim_I2C3_SDA_LOW;
	Sim_I2C3_NOP;

//	Sim_I2C3_SCL_LOW;
//  Sim_I2C3_NOP;

	Sim_I2C3_SCL_HIG;
	Sim_I2C3_SDA_HIG;
	Sim_I2C3_NOP;
}

unsigned char Sim_I2C3_Wait_Ack(void)
{
	volatile unsigned char ucErrTime=0;
	SDA3_IN();
	Sim_I2C3_SDA_HIG;
	Sim_I2C3_NOP;;
	Sim_I2C3_SCL_HIG;
	Sim_I2C3_NOP;;
	while(Sim_I2C3_SDA_STATE)
	{
		ucErrTime++;
		if(ucErrTime>250)
		{
			Sim_I2C3_STOP();
			return 1;
		}
	}
	Sim_I2C3_SCL_LOW;
	return Sim_I2C3_READY;
}

/**
  * @brief  模拟IIC应答时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
void Sim_I2C3_SendACK(void)
{
	Sim_I2C3_SCL_LOW;
	SDA3_OUT();
	Sim_I2C3_SDA_LOW;
	Sim_I2C3_NOP;
	Sim_I2C3_SCL_HIG;
	Sim_I2C3_NOP;
	Sim_I2C3_SCL_LOW;
	Sim_I2C3_NOP;
}

/**
  * @brief  模拟IIC无应答时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
void Sim_I2C3_SendNACK(void)
{
	Sim_I2C3_SCL_LOW;
	SDA3_OUT();
	Sim_I2C3_SDA_HIG;
	Sim_I2C3_NOP;
	Sim_I2C3_SCL_HIG;
	Sim_I2C3_NOP;
	Sim_I2C3_SCL_LOW;
	Sim_I2C3_NOP;
}

/**
  * @brief  模拟IIC发送单字节时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
uint8_t Sim_I2C3_SendByte(uint8_t Sim_i2c_data)
{
	uint8_t i;
	SDA3_OUT();
	Sim_I2C3_SCL_LOW;
	for(i=0; i<8; i++)
	{
		if(Sim_i2c_data&0x80) Sim_I2C3_SDA_HIG;
		else Sim_I2C3_SDA_LOW;

		Sim_i2c_data<<=1;
		Sim_I2C3_NOP;

		Sim_I2C3_SCL_HIG;
		Sim_I2C3_NOP;
		Sim_I2C3_SCL_LOW;
		Sim_I2C3_NOP;
	}
	return Sim_I2C3_READY;
}

/**
  * @brief  模拟IIC读单字节，无应答
  * @param
  * @note
  * @retval void
  * @author 子
  */
uint8_t Sim_I2C3_ReceiveByte(void)
{
	uint8_t i,Sim_i2c_data;
	SDA3_IN();
	//Sim_I2C3_SDA_HIG;
// Sim_I2C3_SCL_LOW;
	Sim_i2c_data=0;

	for(i=0; i<8; i++)
	{
		Sim_I2C3_SCL_LOW;
		Sim_I2C3_NOP;
		Sim_I2C3_SCL_HIG;
		// Sim_I2C3_NOP;
		Sim_i2c_data<<=1;

		if(Sim_I2C3_SDA_STATE)	Sim_i2c_data|=0x01;

		// Sim_I2C3_SCL_LOW;
		Sim_I2C3_NOP;
	}
	Sim_I2C3_SendNACK();
	return Sim_i2c_data;
}

/**
  * @brief  模拟IIC读单字节，带应答
  * @param
  * @note
  * @retval void
  * @author 子
  */
uint8_t Sim_I2C3_ReceiveByte_WithACK(void)
{

	uint8_t i,Sim_i2c_data;
	SDA3_IN();
	//Sim_I2C3_SDA_HIG;
// Sim_I2C3_SCL_LOW;
	Sim_i2c_data=0;

	for(i=0; i<8; i++)
	{
		Sim_I2C3_SCL_LOW;
		Sim_I2C3_NOP;
		Sim_I2C3_SCL_HIG;
		// Sim_I2C3_NOP;
		Sim_i2c_data<<=1;

		if(Sim_I2C3_SDA_STATE)	Sim_i2c_data|=0x01;

		// Sim_I2C3_SCL_LOW;
		Sim_I2C3_NOP;
	}
	Sim_I2C3_SendACK();
	return Sim_i2c_data;
}

/**
  * @brief  模拟IIC开始时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
uint8_t Sim_I2C4_START(void)
{
	SDA4_OUT();
	Sim_I2C4_SDA_HIG;
	Sim_I2C4_SCL_HIG;
	Sim_I2C4_NOP;

// if(!Sim_I2C4_SDA_STATE) return Sim_I2C4_BUS_BUSY;

	Sim_I2C4_SDA_LOW;
	Sim_I2C4_NOP;

	Sim_I2C4_SCL_LOW;
	Sim_I2C4_NOP;

	//if(Sim_I2C4_SDA_STATE) return Sim_I2C4_BUS_ERROR;

	return Sim_I2C4_READY;
}

/**
  * @brief  模拟IIC停止时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
void Sim_I2C4_STOP(void)
{
	SDA4_OUT();
	Sim_I2C4_SCL_LOW;
	Sim_I2C4_SDA_LOW;
	Sim_I2C4_NOP;

//	Sim_I2C4_SCL_LOW;
//  Sim_I2C4_NOP;

	Sim_I2C4_SCL_HIG;
	Sim_I2C4_SDA_HIG;
	Sim_I2C4_NOP;
}

unsigned char Sim_I2C4_Wait_Ack(void)
{
	volatile unsigned char ucErrTime=0;
	SDA4_IN();
	Sim_I2C4_SDA_HIG;
	Sim_I2C4_NOP;;
	Sim_I2C4_SCL_HIG;
	Sim_I2C4_NOP;;
	while(Sim_I2C4_SDA_STATE)
	{
		ucErrTime++;
		if(ucErrTime>250)
		{
			Sim_I2C4_STOP();
			return 1;
		}
	}
	Sim_I2C4_SCL_LOW;
	return Sim_I2C4_READY;
}

/**
  * @brief  模拟IIC应答时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
void Sim_I2C4_SendACK(void)
{
	Sim_I2C4_SCL_LOW;
	SDA4_OUT();
	Sim_I2C4_SDA_LOW;
	Sim_I2C4_NOP;
	Sim_I2C4_SCL_HIG;
	Sim_I2C4_NOP;
	Sim_I2C4_SCL_LOW;
	Sim_I2C4_NOP;
}

/**
  * @brief  模拟IIC无应答时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
void Sim_I2C4_SendNACK(void)
{
	Sim_I2C4_SCL_LOW;
	SDA4_OUT();
	Sim_I2C4_SDA_HIG;
	Sim_I2C4_NOP;
	Sim_I2C4_SCL_HIG;
	Sim_I2C4_NOP;
	Sim_I2C4_SCL_LOW;
	Sim_I2C4_NOP;
}

/**
  * @brief  模拟IIC发送单字节时序
  * @param
  * @note
  * @retval void
  * @author 子
  */
uint8_t Sim_I2C4_SendByte(uint8_t Sim_i2c_data)
{
	uint8_t i;
	SDA4_OUT();
	Sim_I2C4_SCL_LOW;
	for(i=0; i<8; i++)
	{
		if(Sim_i2c_data&0x80) Sim_I2C4_SDA_HIG;
		else Sim_I2C4_SDA_LOW;

		Sim_i2c_data<<=1;
		Sim_I2C4_NOP;

		Sim_I2C4_SCL_HIG;
		Sim_I2C4_NOP;
		Sim_I2C4_SCL_LOW;
		Sim_I2C4_NOP;
	}
	return Sim_I2C4_READY;
}

/**
  * @brief  模拟IIC读单字节，无应答
  * @param
  * @note
  * @retval void
  * @author 子
  */
uint8_t Sim_I2C4_ReceiveByte(void)
{
	uint8_t i,Sim_i2c_data;
	SDA4_IN();
	//Sim_I2C4_SDA_HIG;
// Sim_I2C4_SCL_LOW;
	Sim_i2c_data=0;

	for(i=0; i<8; i++)
	{
		Sim_I2C4_SCL_LOW;
		Sim_I2C4_NOP;
		Sim_I2C4_SCL_HIG;
		// Sim_I2C4_NOP;
		Sim_i2c_data<<=1;

		if(Sim_I2C4_SDA_STATE)	Sim_i2c_data|=0x01;

		// Sim_I2C4_SCL_LOW;
		Sim_I2C4_NOP;
	}
	Sim_I2C4_SendNACK();
	return Sim_i2c_data;
}

/**
  * @brief  模拟IIC读单字节，带应答
  * @param
  * @note
  * @retval void
  * @author 子
  */
uint8_t Sim_I2C4_ReceiveByte_WithACK(void)
{

	uint8_t i,Sim_i2c_data;
	SDA4_IN();
	//Sim_I2C4_SDA_HIG;
// Sim_I2C4_SCL_LOW;
	Sim_i2c_data=0;

	for(i=0; i<8; i++)
	{
		Sim_I2C4_SCL_LOW;
		Sim_I2C4_NOP;
		Sim_I2C4_SCL_HIG;
		// Sim_I2C4_NOP;
		Sim_i2c_data<<=1;

		if(Sim_I2C4_SDA_STATE)	Sim_i2c_data|=0x01;

		// Sim_I2C4_SCL_LOW;
		Sim_I2C4_NOP;
	}
	Sim_I2C4_SendACK();
	return Sim_i2c_data;
}



/**
  * @brief  模拟IIC的多字节读
  * @param
  * @note
  * @retval void
  * @author 
  */
uint8_t Sim_I2C_Read8(uint8_t moni_id, uint8_t moni_dev_addr, uint8_t moni_reg_addr, uint8_t moni_i2c_len, uint8_t *moni_i2c_data_buf)
{
	switch(moni_id){
		
		case 0x01:{
			Sim_I2C1_START();
			Sim_I2C1_SendByte(moni_dev_addr << 1 | I2C1_Direction_Transmitter);
			Sim_I2C1_Wait_Ack();
			Sim_I2C1_SendByte(moni_reg_addr);
			Sim_I2C1_Wait_Ack();
			//Sim_I2C1_STOP();
			
			Sim_I2C1_START();
			Sim_I2C1_SendByte(moni_dev_addr << 1 | I2C1_Direction_Receiver);
			Sim_I2C1_Wait_Ack();
			while (moni_i2c_len)
			{
				if (moni_i2c_len==1) *moni_i2c_data_buf =Sim_I2C1_ReceiveByte();
				else *moni_i2c_data_buf =Sim_I2C1_ReceiveByte_WithACK();
				moni_i2c_data_buf++;
				moni_i2c_len--;
			}
			Sim_I2C1_STOP();
			break;
		}
		case 0x02:{
			Sim_I2C2_START();
			Sim_I2C2_SendByte(moni_dev_addr << 1 | I2C2_Direction_Transmitter);
			Sim_I2C2_Wait_Ack();
			Sim_I2C2_SendByte(moni_reg_addr);
			Sim_I2C2_Wait_Ack();
			//Sim_I2C2_STOP();

			Sim_I2C2_START();
			Sim_I2C2_SendByte(moni_dev_addr << 1 | I2C2_Direction_Receiver);
			Sim_I2C2_Wait_Ack();
			while (moni_i2c_len)
			{
				if (moni_i2c_len==1) *moni_i2c_data_buf = Sim_I2C2_ReceiveByte();
				else *moni_i2c_data_buf = Sim_I2C2_ReceiveByte_WithACK();
				moni_i2c_data_buf++;
				moni_i2c_len--;
			}
			Sim_I2C2_STOP();
			break;
		}
		case 0x03:{
			Sim_I2C3_START();
			Sim_I2C3_SendByte(moni_dev_addr << 1 | I2C3_Direction_Transmitter);
			Sim_I2C3_Wait_Ack();
			Sim_I2C3_SendByte(moni_reg_addr);
			Sim_I2C3_Wait_Ack();
			//Sim_I2C3_STOP();

			Sim_I2C3_START();
			Sim_I2C3_SendByte(moni_dev_addr << 1 | I2C3_Direction_Receiver);
			Sim_I2C3_Wait_Ack();
			while (moni_i2c_len)
			{
				if (moni_i2c_len==1) *moni_i2c_data_buf = Sim_I2C3_ReceiveByte();
				else *moni_i2c_data_buf = Sim_I2C3_ReceiveByte_WithACK();
				moni_i2c_data_buf++;
				moni_i2c_len--;
			}
			Sim_I2C3_STOP();
			break;
		}
		case 0x04:{
			Sim_I2C4_START();
			Sim_I2C4_SendByte(moni_dev_addr << 1 | I2C4_Direction_Transmitter);
			Sim_I2C4_Wait_Ack();
			Sim_I2C4_SendByte(moni_reg_addr);
			Sim_I2C4_Wait_Ack();
			//Sim_I2C4_STOP();

			Sim_I2C4_START();
			Sim_I2C4_SendByte(moni_dev_addr << 1 | I2C4_Direction_Receiver);
			Sim_I2C4_Wait_Ack();
			while (moni_i2c_len)
			{
				if (moni_i2c_len==1) *moni_i2c_data_buf = Sim_I2C4_ReceiveByte();
				else *moni_i2c_data_buf = Sim_I2C4_ReceiveByte_WithACK();
				moni_i2c_data_buf++;
				moni_i2c_len--;
			}
			Sim_I2C4_STOP();
			break;
		}
		default:break;
	}
	return 0x00;
}


/**
  * @brief  模拟IIC的多字节写
  * @param  moni_id: I2C总线标识 (1-4)
  * @param  moni_dev_addr: 设备地址
  * @param  moni_reg_addr: 寄存器地址
  * @param  moni_i2c_len: 要写入的字节数
  * @param  moni_i2c_data_buf: 数据源缓冲区
  * @note   当启用check功能的时候，只能是单字节写的情况，多字接写不可启用check功能
  * @retval int8_t: 操作状态
  * @author 子
  */
int8_t Sim_I2C_Write8(uint8_t moni_id, uint8_t moni_dev_addr, uint8_t moni_reg_addr, uint8_t moni_i2c_len, uint8_t *moni_i2c_data_buf)
{
    uint8_t i;
    
    switch(moni_id){
        case 0x01:{
            Sim_I2C1_START();
            Sim_I2C1_SendByte(moni_dev_addr << 1 | I2C1_Direction_Transmitter);
            Sim_I2C1_Wait_Ack();
            Sim_I2C1_SendByte(moni_reg_addr);
            Sim_I2C1_Wait_Ack();
            
            for (i=0; i<moni_i2c_len; i++)
            {
                Sim_I2C1_SendByte(moni_i2c_data_buf[i]);
                Sim_I2C1_Wait_Ack();
            }
            Sim_I2C1_STOP();
            break;
        }
        case 0x02:{
            Sim_I2C2_START();
            Sim_I2C2_SendByte(moni_dev_addr << 1 | I2C2_Direction_Transmitter);
            Sim_I2C2_Wait_Ack();
            Sim_I2C2_SendByte(moni_reg_addr);
            Sim_I2C2_Wait_Ack();
            
            for (i=0; i<moni_i2c_len; i++)
            {
                Sim_I2C2_SendByte(moni_i2c_data_buf[i]);
                Sim_I2C2_Wait_Ack();
            }
            Sim_I2C2_STOP();
            break;
        }
        case 0x03:{
            Sim_I2C3_START();
            Sim_I2C3_SendByte(moni_dev_addr << 1 | I2C3_Direction_Transmitter);
            Sim_I2C3_Wait_Ack();
            Sim_I2C3_SendByte(moni_reg_addr);
            Sim_I2C3_Wait_Ack();
            
            for (i=0; i<moni_i2c_len; i++)
            {
                Sim_I2C3_SendByte(moni_i2c_data_buf[i]);
                Sim_I2C3_Wait_Ack();
            }
            Sim_I2C3_STOP();
            break;
        }
        case 0x04:{
            Sim_I2C4_START();
            Sim_I2C4_SendByte(moni_dev_addr << 1 | I2C4_Direction_Transmitter);
            Sim_I2C4_Wait_Ack();
            Sim_I2C4_SendByte(moni_reg_addr);
            Sim_I2C4_Wait_Ack();
            
            for (i=0; i<moni_i2c_len; i++)
            {
                Sim_I2C4_SendByte(moni_i2c_data_buf[i]);
                Sim_I2C4_Wait_Ack();
            }
            Sim_I2C4_STOP();
            break;
        }
        default:
            return -1; // 无效的总线ID
    }
    return 0;
}


/************************************************************************************************************/
/************************************************************************************************************/
/*******************************************************************************/


uint8_t highByte(uint16_t value)
{
	uint8_t ret;
	value = value>>8;
	ret = (uint8_t)value;
  return ret;
}

uint8_t lowByte(uint16_t value)
{
	uint8_t ret;
	value = value&0x00ff;
	ret = (uint8_t)value;
  return ret;
}
/*******************************************************
 Method: readOneByte
 In: i2c_bus_id - I2C总线ID, in_adr - 寄存器地址
 Out: data read from i2c
 Description: reads one byte register from i2c
******************************************************/
uint8_t readOneByte(uint8_t i2c_bus_id, uint8_t in_adr)
{
    uint8_t retVal = 0;
    Sim_I2C_Read8(i2c_bus_id, _ams5600_Address, in_adr, 1, &retVal);
    
    // 根据总线ID选择适当的延时宏
    switch(i2c_bus_id){
        case 0x01: Sim_I2C1_NOP; break;
        case 0x02: Sim_I2C2_NOP; break;
        case 0x03: Sim_I2C3_NOP; break;
        case 0x04: Sim_I2C4_NOP; break;
    }
    
    return retVal;
}

/*******************************************************
 Method: readTwoBytes
 In: i2c_bus_id - I2C总线ID, in_adr_hi - 高字节寄存器地址, in_adr_lo - 低字节寄存器地址
 Out: data read from i2c as a uint16_t
 Description: reads two bytes register from i2c
******************************************************/
uint16_t readTwoBytes(uint8_t i2c_bus_id, uint8_t in_adr_hi, uint8_t in_adr_lo)
{
    uint16_t retVal = 0;
    uint8_t low = 0, high = 0;
    
    /* Read Low Byte */
    low = readOneByte(i2c_bus_id, in_adr_lo);
    
    /* Read High Byte */  
    high = readOneByte(i2c_bus_id, in_adr_hi);
    
    retVal = high << 8;
    retVal = retVal | low;
    
    return retVal;
}

/*******************************************************
 Method: writeOneByte
 In: i2c_bus_id - I2C总线ID, adr_in - 寄存器地址, dat_in - 数据
 Out: none
 Description: writes one byte to a i2c register
******************************************************/
void writeOneByte(uint8_t i2c_bus_id, uint8_t adr_in, uint8_t dat_in)
{
    uint8_t dat = dat_in;
    Sim_I2C_Write8(i2c_bus_id, _ams5600_Address, adr_in, 1, &dat);
}

/****************************************************
 Method: AMS_5600
 In: none
 Out: i2c address of AMS 5600
 Description: returns i2c address of AMS 5600
   **************************************************/
int16_t getAddress()
{
  return _ams5600_Address; 
}

/*******************************************************
 Method: getMaxAngle
 In: none
 Out: value of max angle register
 Description: gets value of maximum angle register.
******************************************************/
int16_t getMaxAngle(uint8_t i2c_bus_id)
{
  return readTwoBytes(i2c_bus_id,_mang_hi, _mang_lo);
}

/*******************************************************
 Method: getRawAngle
 In: i2c_bus_id - I2C总线ID
 Out: value of raw angle register
 Description: gets raw value of magnet position.
 start, end, and max angle settings do not apply
******************************************************/
int16_t getRawAngle(uint8_t i2c_bus_id)
{
    return readTwoBytes(i2c_bus_id, _raw_ang_hi, _raw_ang_lo);
}

/*******************************************************
 Method: getStartPosition
 In: none
 Out: value of start position register
 Description: gets value of start position register.
******************************************************/
int16_t getStartPosition(i2c_bus_id)
{
  return readTwoBytes(i2c_bus_id,_zpos_hi, _zpos_lo);
}  

/*******************************************************
 Method: getEndPosition
 In: i2c_bus_id - I2C总线ID
 Out: value of end position register
 Description: gets value of end position register.
******************************************************/
int16_t getEndPosition(uint8_t i2c_bus_id)
{
  int16_t retVal = readTwoBytes(i2c_bus_id, _mpos_hi, _mpos_lo);
  return retVal;
}

/*******************************************************
 Method: getScaledAngle
 In: i2c_bus_id - I2C总线ID
 Out: value of scaled angle register
 Description: gets scaled value of magnet position.
 start, end, or max angle settings are used to 
 determine value
******************************************************/
int16_t getScaledAngle(uint8_t i2c_bus_id)
{
  return readTwoBytes(i2c_bus_id, _ang_hi, _ang_lo);
}

/*******************************************************
 Method: getAgc
 In: i2c_bus_id - I2C总线ID
 Out: value of AGC register
 Description: gets value of AGC register.
******************************************************/
int16_t getAgc(uint8_t i2c_bus_id)
{
  return readOneByte(i2c_bus_id, _agc);
}

/*******************************************************
 Method: getMagnitude
 In: i2c_bus_id - I2C总线ID
 Out: value of magnitude register
 Description: gets value of magnitude register.
******************************************************/
int16_t getMagnitude(uint8_t i2c_bus_id)
{
  return readTwoBytes(i2c_bus_id, _mag_hi, _mag_lo);  
}

/*******************************************************
 Method: getBurnCount
 In: i2c_bus_id - I2C总线ID
 Out: value of zmco register
 Description: determines how many times chip has been
 permanently written to. 
******************************************************/
int16_t getBurnCount(uint8_t i2c_bus_id)
{
  return readOneByte(i2c_bus_id, _zmco);
}

/*******************************************************
 Method: AgetRawAngle
 In: i2c_bus_id - I2C总线ID
 Out: value of raw angle register
 Description: gets raw value of magnet position.
 start, end, and max angle settings do not apply
******************************************************/
int16_t AgetRawAngle(uint8_t i2c_bus_id)
{
  return readTwoBytes(i2c_bus_id, _raw_ang_hi, _raw_ang_lo);
}

/*******************************************************
 Method: setEndPosition
 In: i2c_bus_id - I2C总线ID, endAngle - 新的结束角度位置
 Out: value of end position register
 Description: sets a value in end position register.
 If no value is provided, method will read position of
 magnet.  
******************************************************/
int16_t setEndPosition(uint8_t i2c_bus_id, int16_t endAngle)
{
  if(endAngle == -1)
    _rawEndAngle = getRawAngle(i2c_bus_id);
  else
    _rawEndAngle = endAngle;
 
  writeOneByte(i2c_bus_id, _mpos_hi, highByte(_rawEndAngle));
  HAL_Delay(2); 
  writeOneByte(i2c_bus_id, _mpos_lo, lowByte(_rawEndAngle)); 
  HAL_Delay(2);               
  _mPosition = readTwoBytes(i2c_bus_id, _mpos_hi, _mpos_lo);
  
  return(_mPosition);
}


/*******************************************************
 Method: setStartPosition
 In: i2c_bus_id - I2C总线ID, startAngle - 新的起始角度位置
 Out: value of start position register
 Description: sets a value in start position register.
 If no value is provided, method will read position of
 magnet.  
******************************************************/
int16_t setStartPosition(uint8_t i2c_bus_id, int16_t startAngle)
{
  if(startAngle == -1)
  {
    _rawStartAngle = getRawAngle(i2c_bus_id);
  }
  else
    _rawStartAngle = startAngle;

  writeOneByte(i2c_bus_id, _zpos_hi, highByte(_rawStartAngle));
  HAL_Delay(2); 
  writeOneByte(i2c_bus_id, _zpos_lo, lowByte(_rawStartAngle)); 
  HAL_Delay(2);                
  _zPosition = readTwoBytes(i2c_bus_id, _zpos_hi, _zpos_lo);
  
  return(_zPosition);
}

/*******************************************************
 Method: setMaxAngle
 In: i2c_bus_id - I2C总线ID, newMaxAngle - 新的最大角度
 Out: value of max angle register
 Description: sets a value in maximum angle register.
 If no value is provided, method will read position of
 magnet.  Setting this register zeros out max position
 register.
******************************************************/
int16_t setMaxAngle(uint8_t i2c_bus_id, int16_t newMaxAngle)
{
  int32_t retVal;
  if(newMaxAngle == -1)
  {
    _maxAngle = getRawAngle(i2c_bus_id);
  }
  else
    _maxAngle = newMaxAngle;

  writeOneByte(i2c_bus_id, _mang_hi, highByte(_maxAngle));
  HAL_Delay(2);
  writeOneByte(i2c_bus_id, _mang_lo, lowByte(_maxAngle)); 
  HAL_Delay(2);     

  retVal = readTwoBytes(i2c_bus_id, _mang_hi, _mang_lo);
  return retVal;
}

/*******************************************************
 Method: detectMagnet
 In: i2c_bus_id - I2C总线ID
 Out: 1 if magnet is detected, 0 if not
 Description: reads status register and examines the 
 MH bit
******************************************************/
uint8_t detectMagnet(uint8_t i2c_bus_id)
{
  uint8_t magStatus;
  uint8_t retVal = 0;
  /*0 0 MD ML MH 0 0 0*/
  /* MD high = AGC minimum overflow, Magnet to strong */
  /* ML high = AGC Maximum overflow, magnet to weak*/ 
  /* MH high = magnet detected*/ 
  magStatus = readOneByte(i2c_bus_id, _stat);
  
  if(magStatus & 0x20)
    retVal = 1; 
  
  return retVal;
}

/*******************************************************
 Method: getMagnetStrength
 In: i2c_bus_id - I2C总线ID
 Out: 0 if no magnet is detected
      1 if magnet is to weak
      2 if magnet is just right
      3 if magnet is to strong
 Description: reads status register and examines the MH,ML,MD bits
******************************************************/
uint8_t getMagnetStrength(uint8_t i2c_bus_id)
{
  uint8_t magStatus;
  uint8_t retVal = 0;
  /*0 0 MD ML MH 0 0 0*/
  /* MD high = AGC minimum overflow, Magnet to strong */
  /* ML high = AGC Maximum overflow, magnet to weak*/ 
  /* MH high = magnet detected*/ 
  magStatus = readOneByte(i2c_bus_id, _stat);
  if(detectMagnet(i2c_bus_id) == 1)
  {
      retVal = 2; /*just right */
      if(magStatus & 0x10)
        retVal = 1; /*to weak */
      else if(magStatus & 0x08)
        retVal = 3; /*to strong */
  }
  
  return retVal;
}

/*******************************************************
 Method: burnAngle
 In: i2c_bus_id - I2C总线ID
 Out: 1 success
     -1 no magnet
     -2 burn limit exceeded
     -3 start and end positions not set (useless burn)
 Description: burns start and end positions to chip.
 THIS CAN ONLY BE DONE 3 TIMES
******************************************************/
int8_t burnAngle(uint8_t i2c_bus_id)
{
  int8_t retVal = 1;
  _zPosition = getStartPosition(i2c_bus_id);
  _mPosition = getEndPosition(i2c_bus_id);
  _maxAngle  = getMaxAngle(i2c_bus_id);
  
  if(detectMagnet(i2c_bus_id) == 1)
  {
    if(getBurnCount(i2c_bus_id) < 3)
    {
      if((_zPosition == 0)&&(_mPosition ==0))
        retVal = -3;
      else
        writeOneByte(i2c_bus_id, _burn, 0x80);
    }
    else
      retVal = -2;
  } 
  else
    retVal = -1;
    
  return retVal;
}

/*******************************************************
 Method: burnMaxAngleAndConfig
 In: i2c_bus_id - I2C总线ID
 Out: 1 success
     -1 burn limit exceeded
     -2 max angle is to small, must be at or above 18 degrees
 Description: burns max angle and config data to chip.
 THIS CAN ONLY BE DONE 1 TIME
******************************************************/
int8_t burnMaxAngleAndConfig(uint8_t i2c_bus_id)
{
  int8_t retVal = 1;
  _maxAngle  = getMaxAngle(i2c_bus_id);
  
  if(getBurnCount(i2c_bus_id) == 0)
  {
    if(_maxAngle * 0.087 < 18)
      retVal = -2;
    else
      writeOneByte(i2c_bus_id, _burn, 0x40);    
  }  
  else
    retVal = -1;
    
  return retVal;
}

/*******************************************************
 Function: convertRawAngleToDegrees
 In: angle data from AMS_5600::getRawAngle
 Out: human readable degrees as float
 Description: takes the raw angle and calculates 
 float value in degrees.
******************************************************/
float convertRawAngleToDegrees(int16_t newAngle)
{
  /* Raw data reports 0 - 4095 segments, which is 0.087 of a degree */    
  float retVal = newAngle * 0.087;
  return retVal;
}

/*******************************************************
 Function: Programe_Run
 In: i2c_bus_id - I2C总线ID
 Out: none
 Description: 测试函数，打印磁铁检测状态、原始角度和角度值
******************************************************/
void Programe_Run(uint8_t i2c_bus_id)
{
  uint8_t dect = 0;
  uint16_t rawdata = 0;
  float degress = 0;
  
  dect = detectMagnet(i2c_bus_id);
  printf("detectMagnet is %d\r\n", dect);
  rawdata = getRawAngle(i2c_bus_id);
  printf("rawdata is %d\r\n", rawdata);
  degress = convertRawAngleToDegrees(rawdata);
  printf("degress is %f\r\n", degress);
}
