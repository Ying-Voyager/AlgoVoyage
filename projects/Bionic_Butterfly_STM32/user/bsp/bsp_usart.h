#ifndef __BSP_USART_H
#define __BSP_USART_H

#include "main.h"

#define DEVICE_USART_CNT    5    // 最多分配的串口实例数
#define USART_RXBUFF_LIMIT  256  // 接收缓冲区最大长度

typedef struct USARTInstance USARTInstance_t;
typedef void (*usart_module_callback)(USARTInstance_t *instance);

typedef enum
{
    USART_TRANSFER_NONE = 0,
    USART_TRANSFER_BLOCKING,
    USART_TRANSFER_IT,
    USART_TRANSFER_DMA,
} USART_TRANSFER_MODE;

struct USARTInstance
{
    const char            *name;
    uint8_t                recv_buff[USART_RXBUFF_LIMIT];
    uint16_t               recv_buff_size;
    uint16_t               recv_actual_size;
    UART_HandleTypeDef    *usart_handle;
    usart_module_callback  module_callback;
    void                  *user_context;
};

typedef struct
{
    const char            *name;
    uint8_t                recv_buff_size;
    UART_HandleTypeDef    *usart_handle;
    usart_module_callback  module_callback;
} USART_Init_Config_t;

USARTInstance_t *USARTRegister(USART_Init_Config_t *ptr_init_config);
void USARTSend(USARTInstance_t *_instance, uint8_t *send_buf, uint16_t send_size, USART_TRANSFER_MODE mode);

#endif /* __BSP_USART_H */
