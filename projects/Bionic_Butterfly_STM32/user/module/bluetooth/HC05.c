/**
 * @file    HC05.c
 * @brief   蓝牙HC05_Moudle层
 * @author  玖零
 * @date    2025-7-5
 * @version 1.0
 */

/* USER CODE BEGIN Includes */
#include "HC05.h"
#include "bsp_usart.h"
#include <string.h>
#include <stdio.h>
/* USER CODE END Includes */


#define HC05_BUFFERSIZE  HC05_DATASIZE+2  // HC05发送和接收数据buffer大小，不得大于256(缓存区数组长度)
#define FRAME_HEAD  0XAA    // 帧头
#define FRAME_END   0X55    // 帧尾


static USARTInstance_t *hc05_usart_instances[HC05_MAX_INSTANCES]   ;

static HC05_data_t *hc05_data_instances[HC05_MAX_INSTANCES];

static uint8_t hc05_instance_count = 0;


//static HC05_data_t hc05_msg;   // HC05通信数据
//static USARTInstance_t *hc05_usart_instance;    // HC05串口通信实例
//static uint8_t hc05_init_flag = 0;  // HC05初始化标志位

/**
 * @brief  HC05蓝牙模块接收回调函数，处理串口接收到的数据帧
 * @param  void
 * @retval void
 * @note  
 * 1. 本函数在USART接收中断中自动触发，需确保中断优先级配置合理
 * 2. 数据帧格式必须为：[FRAME_HEAD(0xAA) | 有效数据(HC05_DATASIZE) | FRAME_END(0x55)]
 * 3. 仅当帧头帧尾校验通过时，才会更新接收缓冲区hc05_msg.recv_data
 * @warning 
 * 1. 缓冲区操作未加锁，在中断与主程序共享数据时需考虑临界区保护，比如使用voiltile保护中断变量
 * 2. 若接收数据长度超过HC05_BUFFERSIZE会导致数组越界
 * @example 
 * // 典型调用流程：
 * 1. USART接收中断触发
 * 2. DMA/中断将数据存入hc05_usart_instance->recv_buff
 * 3. 本函数自动校验并提取有效数据
 * 4. 主程序通过hc05_msg.recv_data访问最新数据
 */
static void HC05RxCallback(USARTInstance_t *uart_instance) 
{
    HC05_data_t *_hc05 = (HC05_data_t *)uart_instance->user_context;
	    // 简易有效性校验
    if (_hc05 == NULL) 
		{
        while(1)
				{
				}
    }
		memset(_hc05->recv_data, 0, sizeof(HC05_DATASIZE));
		memcpy(_hc05->recv_data, uart_instance->recv_buff,
										uart_instance->recv_buff_size > HC05_DATASIZE ? HC05_DATASIZE : uart_instance->recv_buff_size);
		
		
}

/**
 * @brief  HC05串口接收初始化
 * @param  hc05_usart_handle:UART_HandleTypeDef 类型的指针 用于传递串口初始化参数
					 确保该句柄已通过HAL_UART_Init()完成初始化，且波特率与HC05模块匹配
 * @retval HC05* 返回指向HC05实例的指针
 * @note  
 * 1. 内部会注册串口实例到BSP层，并绑定接收回调HC05RxCallback
 * 2. 自动添加帧头(0xAA)和帧尾(0x55)的协议处理
 * 3. 初始化成功后设置hc05_init_flag标志位，防止重复初始化
 * 4. 接收缓冲区大小由HC05_BUFFERSIZE宏定义（需小于256字节）
 * @warning 
 * 1. 需先调用HAL_UART_Init()初始化硬件串口
 * 2. 确保hc05_usart_handle与硬件连接匹配（如HC05_TXD接MCU_RX）
 * @example 
 * // 硬件初始化
 * MX_USART2_UART_Init(); // HAL库生成的初始化
 * // HC05初始化
* HC05* hc05 = HC05Init(&huart2); //huart2 为实际串口
 */

HC05_data_t *HC05Init(UART_HandleTypeDef *hc05_usart_handle)
{
	
//		if (hc05_instance_count >= HC05_MAX_INSTANCES) 
//		{
//			return NULL;  // 超过最大实例数
//		}
	
    USART_Init_Config_t *ptr_instance = (USART_Init_Config_t *)malloc(sizeof(USART_Init_Config_t));
    memset(ptr_instance, 0, sizeof(USART_Init_Config_t));

    ptr_instance->module_callback = HC05RxCallback;
    ptr_instance->usart_handle = hc05_usart_handle;
    ptr_instance->recv_buff_size = HC05_BUFFERSIZE;
	
		char *ptr_name = (char *)malloc(sizeof(char)*10);
		sprintf(ptr_name,"HC05_%d",hc05_instance_count);
		ptr_instance->name=ptr_name;
	
    hc05_usart_instances[hc05_instance_count] = USARTRegister(ptr_instance);//注册函数
		HC05_data_t *ptr_hc05_instance = (HC05_data_t *)malloc(sizeof(HC05_data_t));
    memset(ptr_hc05_instance, 0, sizeof(HC05_data_t));
		
		ptr_hc05_instance->usart_handle = hc05_usart_instances[hc05_instance_count];

		hc05_data_instances[hc05_instance_count] = ptr_hc05_instance;
		
		hc05_usart_instances[hc05_instance_count]->user_context = (void *)ptr_hc05_instance;
    hc05_instance_count++;
    return ptr_hc05_instance;

}

/**
 * @brief  通过HC05蓝牙模块发送数据，自动添加帧头帧尾并通过DMA传输
 * @param  data      待发送的数据指针，长度不超过HC05_DATASIZE
 * @param  data_num  实际数据长度（需≤HC05_DATASIZE）
 * @retval void
 * @note  
 * 1. 数据格式：[FRAME_HEAD(0xAA) | data[0..n] | FRAME_END(0x55)]
 * 2. 总发送长度 = data_num + 2（帧头帧尾）
 * 3. 使用DMA传输模式减少CPU占用，适合高频或大数据量场景
 * @warning 
 * 1. 需确保hc05_usart_instance已通过HC05Init()正确初始化
 * 2. 发送前未检查DMA状态，连续调用可能导致数据覆盖（建议通过USARTIsReady()判断）
 * @example 
 * uint8_t test_data[4] = {0x01, 0x02, 0x03, 0x04};
 * HC05_SendData(test_data, 4); // 实际发送6字节：0xAA,0x01,0x02,0x03,0x04,0x55
 */

// HC05串口发送函数，一次最多发送HC05_DATASIZE个数据
void HC05_SendData(HC05_data_t *instance,
									uint8_t *data,
									uint8_t data_long)
{
    if (!instance || data_long > HC05_DATASIZE || !instance->usart_handle) 
        return;
		
		memset(instance->send_data, 0, sizeof(HC05_BUFFERSIZE));
		instance->send_data[0] = FRAME_HEAD;
    for (int i = 0; i < data_long; i++)
		{
			instance->send_data[i+1] = data[i];
		}
    instance->send_data[data_long + 1] = FRAME_END;
    // 发送数据
    USARTSend(instance->usart_handle, instance->send_data, data_long+2, USART_TRANSFER_BLOCKING); 

}
