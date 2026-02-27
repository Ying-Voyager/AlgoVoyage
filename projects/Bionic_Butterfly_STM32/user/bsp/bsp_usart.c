/**
 * @file    bsp_usart.c
 * @brief   串口BSP层驱动
 * @author  Ying Qichi
 */

#include "bsp_usart.h"
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>

static uint8_t idx;
static USARTInstance_t *usart_instance[DEVICE_USART_CNT] = {NULL};

static void USARTServiceInit(USARTInstance_t *_instance)
{
    HAL_UARTEx_ReceiveToIdle_DMA(_instance->usart_handle, _instance->recv_buff, _instance->recv_buff_size);
    __HAL_DMA_DISABLE_IT(_instance->usart_handle->hdmarx, DMA_IT_HT);
}

USARTInstance_t *USARTRegister(USART_Init_Config_t *ptr_init_config)
{
    if (idx >= DEVICE_USART_CNT)
        while (1);
    for (uint8_t i = 0; i < idx; i++)
        if (usart_instance[i]->usart_handle == ptr_init_config->usart_handle)
            while (1);

    USARTInstance_t *ptr_instance = (USARTInstance_t *)malloc(sizeof(USARTInstance_t));
    memset(ptr_instance, 0, sizeof(USARTInstance_t));

    ptr_instance->name            = ptr_init_config->name;
    ptr_instance->usart_handle    = ptr_init_config->usart_handle;
    ptr_instance->recv_buff_size  = ptr_init_config->recv_buff_size;
    ptr_instance->module_callback = ptr_init_config->module_callback;
    ptr_instance->recv_actual_size = 0;

    usart_instance[idx++] = ptr_instance;
    USARTServiceInit(ptr_instance);
    return ptr_instance;
}

void HAL_UARTEx_RxEventCallback(UART_HandleTypeDef *huart, uint16_t Size)
{
    for (uint8_t i = 0; i < idx; ++i)
    {
        if (huart == usart_instance[i]->usart_handle)
        {
            if (usart_instance[i]->module_callback != NULL)
            {
                usart_instance[i]->recv_actual_size = Size;
                usart_instance[i]->module_callback(usart_instance[i]);
                memset(usart_instance[i]->recv_buff, 0, Size);
            }
            HAL_UARTEx_ReceiveToIdle_DMA(usart_instance[i]->usart_handle,
                                          usart_instance[i]->recv_buff,
                                          usart_instance[i]->recv_buff_size);
            __HAL_DMA_DISABLE_IT(usart_instance[i]->usart_handle->hdmarx, DMA_IT_HT);
            return;
        }
    }
}

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
        while (1);
    }
}
