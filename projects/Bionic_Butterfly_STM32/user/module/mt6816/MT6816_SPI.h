#ifndef MT6816_SPI_H
#define MT6816_SPI_H


#include <string.h>		
#include <stdlib.h>		
#include <stdio.h>		
#include <spi.h>		
#include <main.h>		
#include <stdbool.h>  // bool 量

//#define MT6816_SPI_CS_H()	     HAL_GPIO_WritePin(CS1_GPIO_Port,CS1_Pin,1) //cs1口
//#define MT6816_SPI_CS_L()		 HAL_GPIO_WritePin(CS1_GPIO_Port,CS1_Pin,0) 

//#define MT6816_SPI_CS_H()	     HAL_GPIO_WritePin(CS2_GPIO_Port,CS2_Pin,1) //cs2口
//#define MT6816_SPI_CS_L()		 HAL_GPIO_WritePin(CS2_GPIO_Port,CS2_Pin,0) 

//#define MT6816_SPI_CS_H()	     HAL_GPIO_WritePin(CS3_GPIO_Port,CS3_Pin,1) //cs3口
//#define MT6816_SPI_CS_L()		 HAL_GPIO_WritePin(CS3_GPIO_Port,CS3_Pin,0) 

#define MT6816_SPI_CS_H()	     HAL_GPIO_WritePin(CS4_GPIO_Port,CS4_Pin,1) //cs4口
#define MT6816_SPI_CS_L()		 HAL_GPIO_WritePin(CS4_GPIO_Port,CS4_Pin,0) 

#define MT6816_SPI_Get_HSPI		    (hspi1)
#define MT6816_Mode_SPI		        (0x03)	




typedef struct{
	uint16_t	sample_data;	
	uint16_t	angle;		
	bool		no_mag_flag;	
	bool		pc_flag;			
}MT6816_SPI_Signal_Typedef;

void REIN_MT6816_SPI_Signal_Init(void);		
void RINE_MT6816_SPI_Get_AngleData(void);	

typedef struct{
	uint16_t	angle_data;			
	uint16_t	rectify_angle;		
	bool			rectify_valid;		
}MT6816_Typedef;

extern MT6816_Typedef	mt6816;
					
float REIN_MT6816_Get_AngleData();
uint32_t ReadAngle(void);

#endif
