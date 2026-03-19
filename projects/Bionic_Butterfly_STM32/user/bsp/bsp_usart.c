/**
 * @file    bsp_usart.c
 * @brief   串口BSP层驱动 - 新增USARTSend函数
 * @author  林森，玖零
 * @date    2025-07-05  
 * @version 1.1          
 * 
 * @新增功能说明：
 * 1. 通过HAL库USART接口发送数据，支持阻塞/中断/DMA三种传输模式
 * 
 * @修改记录：
 * - v1.0 (2025-07-04) 初始版本，支持串口注册初始化，串口接收回调
 * - v1.1 (2025-07-05) 新增上述功能
 */
 
 
#include "bsp_usart.h"
#include <stdlib.h>  // 支持 malloc/free
#include <stdio.h>
#include <stdint.h>
#include <string.h>

/* usart服务实例,所有注册了usart的模块信息会被保存在这里 */
static uint8_t idx;
static USARTInstance_t *usart_instance[DEVICE_USART_CNT] = {NULL};

static void USARTServiceInit(USARTInstance_t *_instance)
{
    HAL_UARTEx_ReceiveToIdle_DMA(_instance->usart_handle, _instance->recv_buff, _instance->recv_buff_size);
    // 关闭dma half transfer中断防止两次进入HAL_UARTEx_RxEventCallback()
    // 这是HAL库的一个设计失误,发生DMA传输完成/半完成以及串口IDLE中断都会触发HAL_UARTEx_RxEventCallback()
    // 我们只希望处理第一种和第三种情况,因此直接关闭DMA半传输中断
    __HAL_DMA_DISABLE_IT(_instance->usart_handle->hdmarx, DMA_IT_HT);
}

/**
 * @brief  USART设备注册
 * @param  ptr_init_config: USARTInstance_t 类型的指针 用于传递初始化参数
 * @retval USARTInstance_t类型的指针
 */
USARTInstance_t *USARTRegister(USART_Init_Config_t *ptr_init_config)
{
	//目前只支持DMA接收
    if (idx >= DEVICE_USART_CNT) // 超过最大实例数
        while (1);
    for (uint8_t i = 0; i < idx; i++) // 检查是否已经注册过
        if (usart_instance[i]->usart_handle == ptr_init_config->usart_handle)
            while (1);
				
    USARTInstance_t *ptr_instance = (USARTInstance_t *)malloc(sizeof(USARTInstance_t));//申请内存
    memset(ptr_instance, 0, sizeof(USARTInstance_t));//赋值为0
				
		ptr_instance->name = ptr_init_config->name;
    ptr_instance->usart_handle = ptr_init_config->usart_handle;
    ptr_instance->recv_buff_size = ptr_init_config->recv_buff_size;
    ptr_instance->module_callback = ptr_init_config->module_callback;

		ptr_instance->recv_actual_size = 0;
    usart_instance[idx++] = ptr_instance;
    USARTServiceInit(ptr_instance);
    return ptr_instance;
}

void HAL_UARTEx_RxEventCallback(UART_HandleTypeDef *huart, uint16_t Size)
{
    for (uint8_t i = 0; i < idx; ++i)
    { // find the instance which is being handled
        if (huart == usart_instance[i]->usart_handle)
        { // call the callback function if it is not NULL
            if (usart_instance[i]->module_callback != NULL)
            {
								usart_instance[i]->recv_actual_size = Size;
                usart_instance[i]->module_callback(usart_instance[i]);
                memset(usart_instance[i]->recv_buff, 0, Size); // 接收结束后清空buffer,对于变长数据是必要的
            }
            HAL_UARTEx_ReceiveToIdle_DMA(usart_instance[i]->usart_handle, 
														usart_instance[i]->recv_buff, 
														usart_instance[i]->recv_buff_size);
            __HAL_DMA_DISABLE_IT(usart_instance[i]->usart_handle->hdmarx, DMA_IT_HT);
            return; // break the loop
        }
    }
}

/**
 * @brief  通过USART接口发送数据，支持阻塞/中断/DMA三种传输模式
 * @param  _instance   指向USART实例的指针，需包含已初始化的HAL_UART_HandleTypeDef句柄
 * @param  send_buf    待发送数据的缓冲区指针，需确保内存有效且长度匹配send_size
 * @param  send_size   待发送数据的字节数，不得超过缓冲区实际容量
 * @param  mode        传输模式选择，可选：
 *                     - USART_TRANSFER_BLOCKING: 阻塞模式（占用CPU直至发送完成）
 *                     - USART_TRANSFER_IT: 中断模式（非阻塞，通过中断回调通知完成）
 *                     - USART_TRANSFER_DMA: DMA模式（非阻塞，硬件自动传输）
 * @retval void
 * @note  
 * 1. 阻塞模式超时固定为100ms，若需调整需修改源码
 * 2. DMA模式需预先配置DMA通道及流控制器，且缓冲区需保持有效直至传输完成
 * 3. 中断模式下，发送完成会触发HAL_UART_TxCpltCallback回调
 * @warning 
 * 1. 若mode参数非法（非上述三种模式），函数会进入死循环，需检查调用上下文
 * 2. 在DMA/中断模式中，禁止在传输完成前修改send_buf内容
 * @example 
 * // 初始化阶段配置DMA（以STM32为例）
 * MX_DMA_Init();  
 * MX_USART1_UART_Init();
 * 
 * // 发送示例
 * uint8_t data[] = {0x01, 0x02};
 * USARTSend(&huart1, data, 2, USART_TRANSFER_DMA);
 * 
 * // DMA传输完成回调（HAL库）
 * void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart) {
 *     if(huart == &huart1) {
 *         // 处理发送完成逻辑
 *     }
 * }
 */

void USARTSend(USARTInstance_t *_instance, uint8_t *send_buf, uint16_t send_size, USART_TRANSFER_MODE mode)
{
    switch (mode)
    {
    case USART_TRANSFER_BLOCKING:
        HAL_UART_Transmit(_instance->usart_handle, send_buf, send_size, 100);
        break;
    case USART_TRANSFER_IT:
        HAL_UART_Transmit_IT(_instance->usart_handle, send_buf, send_size);
        break;
    case USART_TRANSFER_DMA:
        HAL_UART_Transmit_DMA(_instance->usart_handle, send_buf, send_size);
        break;
    default:
        while (1)
            ; // illegal mode! check your code context! 检查定义instance的代码上下文,可能出现指针越界
        //break;
    }
}
