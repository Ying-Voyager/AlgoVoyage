#ifndef HC05_H
#define HC05_H

#include <stdlib.h>  // 支持 malloc/free
#include <stdint.h>
#include "main.h"
#include "usart.h"
#include "bsp_usart.h"



#define  HC05_DATASIZE  4   // HC05接收和发送数据大小，根据需要修改
#define HC05_MAX_INSTANCES  2  // 实例数

// HC05通信数据结构体，后续根据需要添加和修改
typedef struct {
    USARTInstance_t *usart_handle;  // 绑定的串口句柄
    uint8_t send_data[HC05_DATASIZE+2]; // 实例专属发送缓冲区
    uint8_t recv_data[HC05_DATASIZE];   // 实例专属接收缓冲区
} HC05_data_t;

// HC05串口接收初始化
HC05_data_t *HC05Init(UART_HandleTypeDef *hc05_usart_handle);

// HC05串口发送函数，一次最多发送HC05_DATASIZE个数据
void HC05_SendData(HC05_data_t *instance,uint8_t *data, uint8_t data_num);

#endif
