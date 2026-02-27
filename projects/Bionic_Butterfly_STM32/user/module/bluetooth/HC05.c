/**
 * @file    HC05.c
 * @brief   蓝牙HC05模块驱动
 * @author  Ying Qichi
 */

#include "HC05.h"
#include "bsp_usart.h"
#include <string.h>
#include <stdio.h>

#define HC05_BUFFERSIZE  (HC05_DATASIZE + 2)
#define FRAME_HEAD  0xAA
#define FRAME_END   0x55

static USARTInstance_t *hc05_usart_instances[HC05_MAX_INSTANCES];
static HC05_data_t     *hc05_data_instances[HC05_MAX_INSTANCES];
static uint8_t          hc05_instance_count = 0;

static void HC05RxCallback(USARTInstance_t *uart_instance)
{
    HC05_data_t *_hc05 = (HC05_data_t *)uart_instance->user_context;
    if (_hc05 == NULL)
        while(1);

    memset(_hc05->recv_data, 0, HC05_DATASIZE);
    memcpy(_hc05->recv_data, uart_instance->recv_buff,
           uart_instance->recv_buff_size > HC05_DATASIZE ? HC05_DATASIZE : uart_instance->recv_buff_size);
}

HC05_data_t *HC05Init(UART_HandleTypeDef *hc05_usart_handle)
{
    USART_Init_Config_t *ptr_instance = (USART_Init_Config_t *)malloc(sizeof(USART_Init_Config_t));
    memset(ptr_instance, 0, sizeof(USART_Init_Config_t));

    ptr_instance->module_callback = HC05RxCallback;
    ptr_instance->usart_handle    = hc05_usart_handle;
    ptr_instance->recv_buff_size  = HC05_BUFFERSIZE;

    char *ptr_name = (char *)malloc(sizeof(char) * 10);
    sprintf(ptr_name, "HC05_%d", hc05_instance_count);
    ptr_instance->name = ptr_name;

    hc05_usart_instances[hc05_instance_count] = USARTRegister(ptr_instance);

    HC05_data_t *ptr_hc05_instance = (HC05_data_t *)malloc(sizeof(HC05_data_t));
    memset(ptr_hc05_instance, 0, sizeof(HC05_data_t));
    ptr_hc05_instance->usart_handle = hc05_usart_instances[hc05_instance_count];

    hc05_data_instances[hc05_instance_count] = ptr_hc05_instance;
    hc05_usart_instances[hc05_instance_count]->user_context = (void *)ptr_hc05_instance;
    hc05_instance_count++;

    return ptr_hc05_instance;
}

void HC05_SendData(HC05_data_t *instance, uint8_t *data, uint8_t data_long)
{
    if (!instance || data_long > HC05_DATASIZE || !instance->usart_handle)
        return;

    memset(instance->send_data, 0, HC05_BUFFERSIZE);
    instance->send_data[0] = FRAME_HEAD;
    for (int i = 0; i < data_long; i++)
        instance->send_data[i + 1] = data[i];
    instance->send_data[data_long + 1] = FRAME_END;

    USARTSend(instance->usart_handle, instance->send_data, data_long + 2, USART_TRANSFER_BLOCKING);
}
