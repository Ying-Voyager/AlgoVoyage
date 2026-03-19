#include "AS5600_PWM.h"

/**
************************************************************************************************
* @brief    AS5600_PWM角度读取 - 四编码器版本
* @param    None
* @return   None
* @author   Ying Qichi 2026.3.19
************************************************************************************************
**/

void AS5600_PWM_Init(void)
{
	HAL_ADCEx_Calibration_Start(&hadc1);
}

uint16_t AD_Value[4];

HAL_StatusTypeDef hhStatue;
void StarAndGetResult(void){

	// 读取4个ADC通道
	hhStatue = HAL_ADC_Start_DMA(&hadc1, (uint32_t*)AD_Value, 4);
	if(hhStatue != HAL_OK){
		// DMA启动失败，清零所有值
		AD_Value[0] = 0;
		AD_Value[1] = 0;
		AD_Value[2] = 0;
		AD_Value[3] = 0;
	}
	
	// 等待DMA传输完成
	while (hdma_adc1.State != HAL_DMA_STATE_READY);
	HAL_ADC_Stop_DMA(&hadc1);
	
	// ========== 4个独立编码器角度处理 ==========
	// 每个电机完全独立控制，互不影响
	
	// 编码器0 → 左前翼(M1) - ADC_CH0 (AD_Value[0])
	// 直接使用编码器0的数据控制motor_1
	Wings_Data.Wings_motor[0].Corrective_Angle = PROCESS_VALUE(AD_Value[0], MOTOR1_MIDPOINT);
	
	// 编码器2 → 右前翼(M3) - ADC_CH6 (AD_Value[2])
	// 直接使用编码器2的数据控制motor_3（右前和左前完全独立）
	Wings_Data.Wings_motor[1].Corrective_Angle = PROCESS_VALUE(AD_Value[2], MOTOR3_MIDPOINT);
	
	// 编码器1 → 左后翼(M2) - ADC_CH1 (AD_Value[1])
	// 直接使用编码器1的数据控制motor_2
	Wings_Data.Wings_motor[2].Corrective_Angle = PROCESS_VALUE(AD_Value[1], MOTOR2_MIDPOINT);
	
	// 编码器3 → 右后翼(M4) - ADC_CH7 (AD_Value[3])
	// 直接使用编码器3的数据控制motor_4（右后和左后完全独立）
	Wings_Data.Wings_motor[3].Corrective_Angle = PROCESS_VALUE(AD_Value[3], MOTOR4_MIDPOINT);
}
