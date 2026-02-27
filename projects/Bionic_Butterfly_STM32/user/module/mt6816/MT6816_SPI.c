#include "MT6816_SPI.h"
#include "stdio.h"
/**
 * @brief   MT6816 SPI磁编码器驱动
 * @author  Ying Qichi
 */

MT6816_SPI_Signal_Typedef mt6816_spi;

unsigned int Angle = 0;
uint32_t AngleIn17bits = 0;
uint8_t Spi_TxData[4]  = {0x83, 0xff, 0xff, 0xff};
uint8_t Spi_pRxData[4] = {0};

uint16_t data_t[2] = {0x8300, 0x8400};
uint16_t data_r[2] = {0};

void REIN_MT6816_SPI_Signal_Init(void)
{
	mt6816_spi.sample_data = 0;
	mt6816_spi.angle       = 0;
}

void RINE_MT6816_SPI_Get_AngleData(void)
{
	MT6816_SPI_CS_L();
	HAL_Delay(1);
	HAL_SPI_TransmitReceive(&MT6816_SPI_Get_HSPI, (uint8_t *)&data_t[0], (uint8_t *)&data_r[0], 1, HAL_MAX_DELAY);
	MT6816_SPI_CS_H();
	HAL_Delay(1);
	MT6816_SPI_CS_L();
	HAL_Delay(1);
	HAL_SPI_TransmitReceive(&MT6816_SPI_Get_HSPI, (uint8_t *)&data_t[1], (uint8_t *)&data_r[1], 1, HAL_MAX_DELAY);
	MT6816_SPI_CS_H();
	HAL_Delay(1);

	mt6816_spi.sample_data = (data_r[0] << 6) | (data_r[1] >> 2);
}

MT6816_Typedef mt6816;

float REIN_MT6816_Get_AngleData(void)
{
	RINE_MT6816_SPI_Get_AngleData();
	mt6816.angle_data = mt6816_spi.sample_data;
	return mt6816.angle_data;
}

uint32_t ReadAngle(void)
{
	MT6816_SPI_CS_L();
	HAL_Delay(1);
	HAL_SPI_TransmitReceive(&hspi1, &Spi_TxData[0], &Spi_pRxData[0], 0x03, 0xFFFF);
	HAL_Delay(1);
	MT6816_SPI_CS_H();

	AngleIn17bits = Angle = (((Spi_pRxData[1] & 0x00FF) << 8) | (Spi_pRxData[2] & 0x00FC)) >> 2;
	return AngleIn17bits;
}
