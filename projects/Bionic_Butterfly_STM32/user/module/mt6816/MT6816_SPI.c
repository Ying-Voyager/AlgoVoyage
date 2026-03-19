#include "MT6816_SPI.h"
#include "stdio.h"

MT6816_SPI_Signal_Typedef	mt6816_spi;


unsigned int Angle = 0;
uint32_t AngleIn17bits = 0;
uint8_t Spi_TxData[4]={0x83,0xff,0xff,0xff};///////03 04 05 寄存器存角度
uint8_t Spi_pRxData[4]={0};

	uint16_t data_t[2]={0x8300,0x8400};
	uint16_t data_r[2]={0};


void REIN_MT6816_SPI_Signal_Init(void)
{
	mt6816_spi.sample_data = 0;
	mt6816_spi.angle = 0;
}



void RINE_MT6816_SPI_Get_AngleData(void)
{

	uint8_t h_count;

//	for(uint8_t i=0; i<3; i++){
		//读取SPI数据
		MT6816_SPI_CS_L();
		HAL_Delay(1);
		HAL_SPI_TransmitReceive(&MT6816_SPI_Get_HSPI, (uint8_t*)&data_t[0], (uint8_t*)&data_r[0], 1, HAL_MAX_DELAY);
		MT6816_SPI_CS_H();
		HAL_Delay(1);
		MT6816_SPI_CS_L();
		HAL_Delay(1);
		HAL_SPI_TransmitReceive(&MT6816_SPI_Get_HSPI, (uint8_t*)&data_t[1], (uint8_t*)&data_r[1], 1, HAL_MAX_DELAY);
		MT6816_SPI_CS_H();
		HAL_Delay(1);
		
		mt6816_spi.sample_data = (data_r[0]<< 6) | (data_r[1] >>2);
//		//奇偶校验
//		h_count = 0;
//		for(uint8_t j=0; j<16; j++){
//			if(mt6816_spi.sample_data & (0x0001 << j))
//				h_count++;
//		}
//		if(h_count & 0x01){
//			mt6816_spi.pc_flag = false;
//		}
//		else{
//			mt6816_spi.pc_flag = true;
//			break;
//		}
//	}
//	if(mt6816_spi.pc_flag){
//		mt6816_spi.angle = mt6816_spi.sample_data >> 2;
//		mt6816_spi.no_mag_flag = (bool)(mt6816_spi.sample_data & (0x0001 << 1));
//	}
}

MT6816_Typedef	mt6816;

float REIN_MT6816_Get_AngleData()
{
	RINE_MT6816_SPI_Get_AngleData();
	mt6816.angle_data = mt6816_spi.sample_data;  
	
	return mt6816.angle_data;
}

uint32_t ReadAngle(void)
{
    //Read in Burst mode
	    
	  MT6816_SPI_CS_L();///CSN LOW   
		HAL_Delay(1);
		HAL_SPI_TransmitReceive(&hspi1, &Spi_TxData[0], &Spi_pRxData[0],0x03,0xffff);
		HAL_Delay(1);
		MT6816_SPI_CS_H();///CSN HIGH
	
	  AngleIn17bits=Angle =(((Spi_pRxData[1]&0x00ff)<<8)|(Spi_pRxData[2]&0x00fc))>>2;;////14bits 
		
    return (AngleIn17bits);	    
}
