#include "as5600.h"
#include <stdio.h>
/**
 * @brief   AS5600 I2C软件模拟驱动 - 四路版本
 * @author  Ying Qichi
 */

uint16_t _rawStartAngle = 0;
uint16_t _zPosition     = 0;
uint16_t _rawEndAngle   = 0;
uint16_t _mPosition     = 0;
uint16_t _maxAngle      = 0;


void Sim_I2C_Delay(uint32_t delay)
{
	while(--delay);
}


/* ========== I2C1 ========== */

uint8_t Sim_I2C1_START(void)
{
	SDA1_OUT();
	Sim_I2C1_SDA_HIG;
	Sim_I2C1_SCL_HIG;
	Sim_I2C1_NOP;
	Sim_I2C1_SDA_LOW;
	Sim_I2C1_NOP;
	Sim_I2C1_SCL_LOW;
	Sim_I2C1_NOP;
	return Sim_I2C1_READY;
}

void Sim_I2C1_STOP(void)
{
	SDA1_OUT();
	Sim_I2C1_SCL_LOW;
	Sim_I2C1_SDA_LOW;
	Sim_I2C1_NOP;
	Sim_I2C1_SCL_HIG;
	Sim_I2C1_SDA_HIG;
	Sim_I2C1_NOP;
}

unsigned char Sim_I2C1_Wait_Ack(void)
{
	volatile unsigned char ucErrTime = 0;
	SDA1_IN();
	Sim_I2C1_SDA_HIG;
	Sim_I2C1_NOP;
	Sim_I2C1_SCL_HIG;
	Sim_I2C1_NOP;
	while(Sim_I2C1_SDA_STATE)
	{
		ucErrTime++;
		if(ucErrTime > 250) { Sim_I2C1_STOP(); return 1; }
	}
	Sim_I2C1_SCL_LOW;
	return Sim_I2C1_READY;
}

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

uint8_t Sim_I2C1_SendByte(uint8_t Sim_i2c_data)
{
	uint8_t i;
	SDA1_OUT();
	Sim_I2C1_SCL_LOW;
	for(i = 0; i < 8; i++)
	{
		if(Sim_i2c_data & 0x80) Sim_I2C1_SDA_HIG;
		else Sim_I2C1_SDA_LOW;
		Sim_i2c_data <<= 1;
		Sim_I2C1_NOP;
		Sim_I2C1_SCL_HIG;
		Sim_I2C1_NOP;
		Sim_I2C1_SCL_LOW;
		Sim_I2C1_NOP;
	}
	return Sim_I2C1_READY;
}

uint8_t Sim_I2C1_ReceiveByte(void)
{
	uint8_t i, Sim_i2c_data = 0;
	SDA1_IN();
	for(i = 0; i < 8; i++)
	{
		Sim_I2C1_SCL_LOW;
		Sim_I2C1_NOP;
		Sim_I2C1_SCL_HIG;
		Sim_i2c_data <<= 1;
		if(Sim_I2C1_SDA_STATE) Sim_i2c_data |= 0x01;
		Sim_I2C1_NOP;
	}
	Sim_I2C1_SendNACK();
	return Sim_i2c_data;
}

uint8_t Sim_I2C1_ReceiveByte_WithACK(void)
{
	uint8_t i, Sim_i2c_data = 0;
	SDA1_IN();
	for(i = 0; i < 8; i++)
	{
		Sim_I2C1_SCL_LOW;
		Sim_I2C1_NOP;
		Sim_I2C1_SCL_HIG;
		Sim_i2c_data <<= 1;
		if(Sim_I2C1_SDA_STATE) Sim_i2c_data |= 0x01;
		Sim_I2C1_NOP;
	}
	Sim_I2C1_SendACK();
	return Sim_i2c_data;
}


/* ========== I2C2 ========== */

uint8_t Sim_I2C2_START(void)
{
	SDA2_OUT();
	Sim_I2C2_SDA_HIG;
	Sim_I2C2_SCL_HIG;
	Sim_I2C2_NOP;
	Sim_I2C2_SDA_LOW;
	Sim_I2C2_NOP;
	Sim_I2C2_SCL_LOW;
	Sim_I2C2_NOP;
	return Sim_I2C2_READY;
}

void Sim_I2C2_STOP(void)
{
	SDA2_OUT();
	Sim_I2C2_SCL_LOW;
	Sim_I2C2_SDA_LOW;
	Sim_I2C2_NOP;
	Sim_I2C2_SCL_HIG;
	Sim_I2C2_SDA_HIG;
	Sim_I2C2_NOP;
}

unsigned char Sim_I2C2_Wait_Ack(void)
{
	volatile unsigned char ucErrTime = 0;
	SDA2_IN();
	Sim_I2C2_SDA_HIG;
	Sim_I2C2_NOP;
	Sim_I2C2_SCL_HIG;
	Sim_I2C2_NOP;
	while(Sim_I2C2_SDA_STATE)
	{
		ucErrTime++;
		if(ucErrTime > 250) { Sim_I2C2_STOP(); return 1; }
	}
	Sim_I2C2_SCL_LOW;
	return Sim_I2C2_READY;
}

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

uint8_t Sim_I2C2_SendByte(uint8_t Sim_i2c_data)
{
	uint8_t i;
	SDA2_OUT();
	Sim_I2C2_SCL_LOW;
	for(i = 0; i < 8; i++)
	{
		if(Sim_i2c_data & 0x80) Sim_I2C2_SDA_HIG;
		else Sim_I2C2_SDA_LOW;
		Sim_i2c_data <<= 1;
		Sim_I2C2_NOP;
		Sim_I2C2_SCL_HIG;
		Sim_I2C2_NOP;
		Sim_I2C2_SCL_LOW;
		Sim_I2C2_NOP;
	}
	return Sim_I2C2_READY;
}

uint8_t Sim_I2C2_ReceiveByte(void)
{
	uint8_t i, Sim_i2c_data = 0;
	SDA2_IN();
	for(i = 0; i < 8; i++)
	{
		Sim_I2C2_SCL_LOW;
		Sim_I2C2_NOP;
		Sim_I2C2_SCL_HIG;
		Sim_i2c_data <<= 1;
		if(Sim_I2C2_SDA_STATE) Sim_i2c_data |= 0x01;
		Sim_I2C2_NOP;
	}
	Sim_I2C2_SendNACK();
	return Sim_i2c_data;
}

uint8_t Sim_I2C2_ReceiveByte_WithACK(void)
{
	uint8_t i, Sim_i2c_data = 0;
	SDA2_IN();
	for(i = 0; i < 8; i++)
	{
		Sim_I2C2_SCL_LOW;
		Sim_I2C2_NOP;
		Sim_I2C2_SCL_HIG;
		Sim_i2c_data <<= 1;
		if(Sim_I2C2_SDA_STATE) Sim_i2c_data |= 0x01;
		Sim_I2C2_NOP;
	}
	Sim_I2C2_SendACK();
	return Sim_i2c_data;
}


/* ========== I2C3 ========== */

uint8_t Sim_I2C3_START(void)
{
	SDA3_OUT();
	Sim_I2C3_SDA_HIG;
	Sim_I2C3_SCL_HIG;
	Sim_I2C3_NOP;
	Sim_I2C3_SDA_LOW;
	Sim_I2C3_NOP;
	Sim_I2C3_SCL_LOW;
	Sim_I2C3_NOP;
	return Sim_I2C3_READY;
}

void Sim_I2C3_STOP(void)
{
	SDA3_OUT();
	Sim_I2C3_SCL_LOW;
	Sim_I2C3_SDA_LOW;
	Sim_I2C3_NOP;
	Sim_I2C3_SCL_HIG;
	Sim_I2C3_SDA_HIG;
	Sim_I2C3_NOP;
}

unsigned char Sim_I2C3_Wait_Ack(void)
{
	volatile unsigned char ucErrTime = 0;
	SDA3_IN();
	Sim_I2C3_SDA_HIG;
	Sim_I2C3_NOP;
	Sim_I2C3_SCL_HIG;
	Sim_I2C3_NOP;
	while(Sim_I2C3_SDA_STATE)
	{
		ucErrTime++;
		if(ucErrTime > 250) { Sim_I2C3_STOP(); return 1; }
	}
	Sim_I2C3_SCL_LOW;
	return Sim_I2C3_READY;
}

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

uint8_t Sim_I2C3_SendByte(uint8_t Sim_i2c_data)
{
	uint8_t i;
	SDA3_OUT();
	Sim_I2C3_SCL_LOW;
	for(i = 0; i < 8; i++)
	{
		if(Sim_i2c_data & 0x80) Sim_I2C3_SDA_HIG;
		else Sim_I2C3_SDA_LOW;
		Sim_i2c_data <<= 1;
		Sim_I2C3_NOP;
		Sim_I2C3_SCL_HIG;
		Sim_I2C3_NOP;
		Sim_I2C3_SCL_LOW;
		Sim_I2C3_NOP;
	}
	return Sim_I2C3_READY;
}

uint8_t Sim_I2C3_ReceiveByte(void)
{
	uint8_t i, Sim_i2c_data = 0;
	SDA3_IN();
	for(i = 0; i < 8; i++)
	{
		Sim_I2C3_SCL_LOW;
		Sim_I2C3_NOP;
		Sim_I2C3_SCL_HIG;
		Sim_i2c_data <<= 1;
		if(Sim_I2C3_SDA_STATE) Sim_i2c_data |= 0x01;
		Sim_I2C3_NOP;
	}
	Sim_I2C3_SendNACK();
	return Sim_i2c_data;
}

uint8_t Sim_I2C3_ReceiveByte_WithACK(void)
{
	uint8_t i, Sim_i2c_data = 0;
	SDA3_IN();
	for(i = 0; i < 8; i++)
	{
		Sim_I2C3_SCL_LOW;
		Sim_I2C3_NOP;
		Sim_I2C3_SCL_HIG;
		Sim_i2c_data <<= 1;
		if(Sim_I2C3_SDA_STATE) Sim_i2c_data |= 0x01;
		Sim_I2C3_NOP;
	}
	Sim_I2C3_SendACK();
	return Sim_i2c_data;
}


/* ========== I2C4 ========== */

uint8_t Sim_I2C4_START(void)
{
	SDA4_OUT();
	Sim_I2C4_SDA_HIG;
	Sim_I2C4_SCL_HIG;
	Sim_I2C4_NOP;
	Sim_I2C4_SDA_LOW;
	Sim_I2C4_NOP;
	Sim_I2C4_SCL_LOW;
	Sim_I2C4_NOP;
	return Sim_I2C4_READY;
}

void Sim_I2C4_STOP(void)
{
	SDA4_OUT();
	Sim_I2C4_SCL_LOW;
	Sim_I2C4_SDA_LOW;
	Sim_I2C4_NOP;
	Sim_I2C4_SCL_HIG;
	Sim_I2C4_SDA_HIG;
	Sim_I2C4_NOP;
}

unsigned char Sim_I2C4_Wait_Ack(void)
{
	volatile unsigned char ucErrTime = 0;
	SDA4_IN();
	Sim_I2C4_SDA_HIG;
	Sim_I2C4_NOP;
	Sim_I2C4_SCL_HIG;
	Sim_I2C4_NOP;
	while(Sim_I2C4_SDA_STATE)
	{
		ucErrTime++;
		if(ucErrTime > 250) { Sim_I2C4_STOP(); return 1; }
	}
	Sim_I2C4_SCL_LOW;
	return Sim_I2C4_READY;
}

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

uint8_t Sim_I2C4_SendByte(uint8_t Sim_i2c_data)
{
	uint8_t i;
	SDA4_OUT();
	Sim_I2C4_SCL_LOW;
	for(i = 0; i < 8; i++)
	{
		if(Sim_i2c_data & 0x80) Sim_I2C4_SDA_HIG;
		else Sim_I2C4_SDA_LOW;
		Sim_i2c_data <<= 1;
		Sim_I2C4_NOP;
		Sim_I2C4_SCL_HIG;
		Sim_I2C4_NOP;
		Sim_I2C4_SCL_LOW;
		Sim_I2C4_NOP;
	}
	return Sim_I2C4_READY;
}

uint8_t Sim_I2C4_ReceiveByte(void)
{
	uint8_t i, Sim_i2c_data = 0;
	SDA4_IN();
	for(i = 0; i < 8; i++)
	{
		Sim_I2C4_SCL_LOW;
		Sim_I2C4_NOP;
		Sim_I2C4_SCL_HIG;
		Sim_i2c_data <<= 1;
		if(Sim_I2C4_SDA_STATE) Sim_i2c_data |= 0x01;
		Sim_I2C4_NOP;
	}
	Sim_I2C4_SendNACK();
	return Sim_i2c_data;
}

uint8_t Sim_I2C4_ReceiveByte_WithACK(void)
{
	uint8_t i, Sim_i2c_data = 0;
	SDA4_IN();
	for(i = 0; i < 8; i++)
	{
		Sim_I2C4_SCL_LOW;
		Sim_I2C4_NOP;
		Sim_I2C4_SCL_HIG;
		Sim_i2c_data <<= 1;
		if(Sim_I2C4_SDA_STATE) Sim_i2c_data |= 0x01;
		Sim_I2C4_NOP;
	}
	Sim_I2C4_SendACK();
	return Sim_i2c_data;
}


/* ========== 通用读写接口 ========== */

uint8_t Sim_I2C_Read8(uint8_t moni_id, uint8_t moni_dev_addr, uint8_t moni_reg_addr, uint8_t moni_i2c_len, uint8_t *moni_i2c_data_buf)
{
	switch(moni_id)
	{
		case 0x01:
			Sim_I2C1_START();
			Sim_I2C1_SendByte(moni_dev_addr << 1 | I2C1_Direction_Transmitter);
			Sim_I2C1_Wait_Ack();
			Sim_I2C1_SendByte(moni_reg_addr);
			Sim_I2C1_Wait_Ack();
			Sim_I2C1_START();
			Sim_I2C1_SendByte(moni_dev_addr << 1 | I2C1_Direction_Receiver);
			Sim_I2C1_Wait_Ack();
			while(moni_i2c_len)
			{
				if(moni_i2c_len == 1) *moni_i2c_data_buf = Sim_I2C1_ReceiveByte();
				else *moni_i2c_data_buf = Sim_I2C1_ReceiveByte_WithACK();
				moni_i2c_data_buf++;
				moni_i2c_len--;
			}
			Sim_I2C1_STOP();
			break;
		case 0x02:
			Sim_I2C2_START();
			Sim_I2C2_SendByte(moni_dev_addr << 1 | I2C2_Direction_Transmitter);
			Sim_I2C2_Wait_Ack();
			Sim_I2C2_SendByte(moni_reg_addr);
			Sim_I2C2_Wait_Ack();
			Sim_I2C2_START();
			Sim_I2C2_SendByte(moni_dev_addr << 1 | I2C2_Direction_Receiver);
			Sim_I2C2_Wait_Ack();
			while(moni_i2c_len)
			{
				if(moni_i2c_len == 1) *moni_i2c_data_buf = Sim_I2C2_ReceiveByte();
				else *moni_i2c_data_buf = Sim_I2C2_ReceiveByte_WithACK();
				moni_i2c_data_buf++;
				moni_i2c_len--;
			}
			Sim_I2C2_STOP();
			break;
		case 0x03:
			Sim_I2C3_START();
			Sim_I2C3_SendByte(moni_dev_addr << 1 | I2C3_Direction_Transmitter);
			Sim_I2C3_Wait_Ack();
			Sim_I2C3_SendByte(moni_reg_addr);
			Sim_I2C3_Wait_Ack();
			Sim_I2C3_START();
			Sim_I2C3_SendByte(moni_dev_addr << 1 | I2C3_Direction_Receiver);
			Sim_I2C3_Wait_Ack();
			while(moni_i2c_len)
			{
				if(moni_i2c_len == 1) *moni_i2c_data_buf = Sim_I2C3_ReceiveByte();
				else *moni_i2c_data_buf = Sim_I2C3_ReceiveByte_WithACK();
				moni_i2c_data_buf++;
				moni_i2c_len--;
			}
			Sim_I2C3_STOP();
			break;
		case 0x04:
			Sim_I2C4_START();
			Sim_I2C4_SendByte(moni_dev_addr << 1 | I2C4_Direction_Transmitter);
			Sim_I2C4_Wait_Ack();
			Sim_I2C4_SendByte(moni_reg_addr);
			Sim_I2C4_Wait_Ack();
			Sim_I2C4_START();
			Sim_I2C4_SendByte(moni_dev_addr << 1 | I2C4_Direction_Receiver);
			Sim_I2C4_Wait_Ack();
			while(moni_i2c_len)
			{
				if(moni_i2c_len == 1) *moni_i2c_data_buf = Sim_I2C4_ReceiveByte();
				else *moni_i2c_data_buf = Sim_I2C4_ReceiveByte_WithACK();
				moni_i2c_data_buf++;
				moni_i2c_len--;
			}
			Sim_I2C4_STOP();
			break;
		default: break;
	}
	return 0x00;
}

int8_t Sim_I2C_Write8(uint8_t moni_id, uint8_t moni_dev_addr, uint8_t moni_reg_addr, uint8_t moni_i2c_len, uint8_t *moni_i2c_data_buf)
{
    uint8_t i;
    switch(moni_id)
	{
        case 0x01:
            Sim_I2C1_START();
            Sim_I2C1_SendByte(moni_dev_addr << 1 | I2C1_Direction_Transmitter);
            Sim_I2C1_Wait_Ack();
            Sim_I2C1_SendByte(moni_reg_addr);
            Sim_I2C1_Wait_Ack();
            for(i = 0; i < moni_i2c_len; i++) { Sim_I2C1_SendByte(moni_i2c_data_buf[i]); Sim_I2C1_Wait_Ack(); }
            Sim_I2C1_STOP();
            break;
        case 0x02:
            Sim_I2C2_START();
            Sim_I2C2_SendByte(moni_dev_addr << 1 | I2C2_Direction_Transmitter);
            Sim_I2C2_Wait_Ack();
            Sim_I2C2_SendByte(moni_reg_addr);
            Sim_I2C2_Wait_Ack();
            for(i = 0; i < moni_i2c_len; i++) { Sim_I2C2_SendByte(moni_i2c_data_buf[i]); Sim_I2C2_Wait_Ack(); }
            Sim_I2C2_STOP();
            break;
        case 0x03:
            Sim_I2C3_START();
            Sim_I2C3_SendByte(moni_dev_addr << 1 | I2C3_Direction_Transmitter);
            Sim_I2C3_Wait_Ack();
            Sim_I2C3_SendByte(moni_reg_addr);
            Sim_I2C3_Wait_Ack();
            for(i = 0; i < moni_i2c_len; i++) { Sim_I2C3_SendByte(moni_i2c_data_buf[i]); Sim_I2C3_Wait_Ack(); }
            Sim_I2C3_STOP();
            break;
        case 0x04:
            Sim_I2C4_START();
            Sim_I2C4_SendByte(moni_dev_addr << 1 | I2C4_Direction_Transmitter);
            Sim_I2C4_Wait_Ack();
            Sim_I2C4_SendByte(moni_reg_addr);
            Sim_I2C4_Wait_Ack();
            for(i = 0; i < moni_i2c_len; i++) { Sim_I2C4_SendByte(moni_i2c_data_buf[i]); Sim_I2C4_Wait_Ack(); }
            Sim_I2C4_STOP();
            break;
        default:
            return -1;
    }
    return 0;
}


/* ========== AS5600 高层接口 ========== */

uint8_t highByte(uint16_t value) { return (uint8_t)(value >> 8); }
uint8_t lowByte(uint16_t value)  { return (uint8_t)(value & 0x00FF); }

uint8_t readOneByte(uint8_t i2c_bus_id, uint8_t in_adr)
{
    uint8_t retVal = 0;
    Sim_I2C_Read8(i2c_bus_id, _ams5600_Address, in_adr, 1, &retVal);
    return retVal;
}

uint16_t readTwoBytes(uint8_t i2c_bus_id, uint8_t in_adr_hi, uint8_t in_adr_lo)
{
    uint8_t low = readOneByte(i2c_bus_id, in_adr_lo);
    uint8_t high = readOneByte(i2c_bus_id, in_adr_hi);
    return (uint16_t)(high << 8) | low;
}

void writeOneByte(uint8_t i2c_bus_id, uint8_t adr_in, uint8_t dat_in)
{
    uint8_t dat = dat_in;
    Sim_I2C_Write8(i2c_bus_id, _ams5600_Address, adr_in, 1, &dat);
}

int16_t getAddress(void)          { return _ams5600_Address; }
int16_t getMaxAngle(uint8_t id)   { return readTwoBytes(id, _mang_hi, _mang_lo); }
int16_t getRawAngle(uint8_t id)   { return readTwoBytes(id, _raw_ang_hi, _raw_ang_lo); }
int16_t getStartPosition(uint8_t id) { return readTwoBytes(id, _zpos_hi, _zpos_lo); }
int16_t getEndPosition(uint8_t id)   { return readTwoBytes(id, _mpos_hi, _mpos_lo); }
int16_t getScaledAngle(uint8_t id)   { return readTwoBytes(id, _ang_hi, _ang_lo); }
int16_t getAgc(uint8_t id)           { return readOneByte(id, _agc); }
int16_t getMagnitude(uint8_t id)     { return readTwoBytes(id, _mag_hi, _mag_lo); }
int16_t getBurnCount(uint8_t id)     { return readOneByte(id, _zmco); }
int16_t AgetRawAngle(uint8_t id)     { return readTwoBytes(id, _raw_ang_hi, _raw_ang_lo); }

int16_t setEndPosition(uint8_t i2c_bus_id, int16_t endAngle)
{
    _rawEndAngle = (endAngle == -1) ? getRawAngle(i2c_bus_id) : endAngle;
    writeOneByte(i2c_bus_id, _mpos_hi, highByte(_rawEndAngle)); HAL_Delay(2);
    writeOneByte(i2c_bus_id, _mpos_lo, lowByte(_rawEndAngle));  HAL_Delay(2);
    _mPosition = readTwoBytes(i2c_bus_id, _mpos_hi, _mpos_lo);
    return _mPosition;
}

int16_t setStartPosition(uint8_t i2c_bus_id, int16_t startAngle)
{
    _rawStartAngle = (startAngle == -1) ? getRawAngle(i2c_bus_id) : startAngle;
    writeOneByte(i2c_bus_id, _zpos_hi, highByte(_rawStartAngle)); HAL_Delay(2);
    writeOneByte(i2c_bus_id, _zpos_lo, lowByte(_rawStartAngle));  HAL_Delay(2);
    _zPosition = readTwoBytes(i2c_bus_id, _zpos_hi, _zpos_lo);
    return _zPosition;
}

int16_t setMaxAngle(uint8_t i2c_bus_id, int16_t newMaxAngle)
{
    _maxAngle = (newMaxAngle == -1) ? getRawAngle(i2c_bus_id) : newMaxAngle;
    writeOneByte(i2c_bus_id, _mang_hi, highByte(_maxAngle)); HAL_Delay(2);
    writeOneByte(i2c_bus_id, _mang_lo, lowByte(_maxAngle));  HAL_Delay(2);
    return readTwoBytes(i2c_bus_id, _mang_hi, _mang_lo);
}

uint8_t detectMagnet(uint8_t i2c_bus_id)
{
    uint8_t magStatus = readOneByte(i2c_bus_id, _stat);
    return (magStatus & 0x20) ? 1 : 0;
}

uint8_t getMagnetStrength(uint8_t i2c_bus_id)
{
    uint8_t magStatus = readOneByte(i2c_bus_id, _stat);
    uint8_t retVal = 0;
    if(detectMagnet(i2c_bus_id) == 1)
    {
        retVal = 2;
        if(magStatus & 0x10) retVal = 1;
        else if(magStatus & 0x08) retVal = 3;
    }
    return retVal;
}

int8_t burnAngle(uint8_t i2c_bus_id)
{
    _zPosition = getStartPosition(i2c_bus_id);
    _mPosition = getEndPosition(i2c_bus_id);
    _maxAngle  = getMaxAngle(i2c_bus_id);
    if(detectMagnet(i2c_bus_id) == 1)
    {
        if(getBurnCount(i2c_bus_id) < 3)
        {
            if((_zPosition == 0) && (_mPosition == 0)) return -3;
            writeOneByte(i2c_bus_id, _burn, 0x80);
            return 1;
        }
        return -2;
    }
    return -1;
}

int8_t burnMaxAngleAndConfig(uint8_t i2c_bus_id)
{
    _maxAngle = getMaxAngle(i2c_bus_id);
    if(getBurnCount(i2c_bus_id) == 0)
    {
        if(_maxAngle * 0.087 < 18) return -2;
        writeOneByte(i2c_bus_id, _burn, 0x40);
        return 1;
    }
    return -1;
}

float convertRawAngleToDegrees(int16_t newAngle)
{
    return newAngle * 0.087f;
}

void Programe_Run(uint8_t i2c_bus_id)
{
    uint8_t dect    = detectMagnet(i2c_bus_id);
    uint16_t rawdata = getRawAngle(i2c_bus_id);
    float degress   = convertRawAngleToDegrees(rawdata);
    printf("detectMagnet is %d\r\n", dect);
    printf("rawdata is %d\r\n", rawdata);
    printf("degress is %f\r\n", degress);
}
