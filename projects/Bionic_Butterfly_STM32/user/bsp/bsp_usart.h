#ifndef __BSP_USART_H
#define  __BSP_USART_H
#include "main.h"

#define DEVICE_USART_CNT 5     // 至多分配5个串口
#define USART_RXBUFF_LIMIT 256 // 如果协议需要更大的buff,请修改这里

typedef struct USARTInstance USARTInstance_t;

// 模块回调函数,用于解析协议
typedef void (*usart_module_callback)(USARTInstance_t *instance);

/* 发送模式枚举 */
typedef enum
{
    USART_TRANSFER_NONE=0,
    USART_TRANSFER_BLOCKING,
    USART_TRANSFER_IT,
    USART_TRANSFER_DMA,
} USART_TRANSFER_MODE;



// 串口实例结构体,每个module都要包含一个实例.
// 由于串口是独占的点对点通信,所以不需要考虑多个module同时使用一个串口的情况,因此不用加入id;当然也可以选择加入,这样在bsp层可以访问到module的其他信息
struct USARTInstance
{
	const char *name;
	uint8_t recv_buff[USART_RXBUFF_LIMIT]; // 预先定义的最大buff大小,如果太小请修改USART_RXBUFF_LIMIT
	uint16_t recv_buff_size;                // 模块接收一包数据的大小
	uint16_t recv_actual_size;					//接受数组实际大小
	UART_HandleTypeDef *usart_handle;      // 实例对应的usart_handle
	usart_module_callback module_callback; // 解析收到的数据的回调函数
	
	void *user_context;  // 添加的上下文指针 ( 当多个usart 回传到同一个modules 的callbbreak 的时候直接 寻找 )
} ;




// 串口实例结构体,每个module都要包含一个实例.
// 由于串口是独占的点对点通信,所以不需要考虑多个module同时使用一个串口的情况,因此不用加入id;当然也可以选择加入,这样在bsp层可以访问到module的其他信息
/* usart 初始化配置结构体 */
typedef struct
{
	const char *name;
	uint8_t  recv_buff_size;                // 模块接收一包数据的大小
	UART_HandleTypeDef  *usart_handle;      // 实例对应的usart_handle
	usart_module_callback  module_callback; // 解析收到的数据的回调函数
} USART_Init_Config_t;






/**
 * @brief  USART设备注册
 * @param  ptr_init_config: USART_Init_Config_t 类型的指针 用于传递初始化参数
 * @retval USARTInstance_t类型的指针
 */
USARTInstance_t *USARTRegister(USART_Init_Config_t *ptr_init_config);


/**
 * @brief 通过调用该函数可以发送一帧数据,需要传入一个usart实例,发送buff以及这一帧的长度
 * @note 在短时间内连续调用此接口,若采用IT/DMA会导致上一次的发送未完成而新的发送取消.
 * @note 若希望连续使用DMA/IT进行发送,请配合USARTIsReady()使用,或自行为你的module实现一个发送队列和任务.
 * @todo 是否考虑为USARTInstance增加发送队列以进行连续发送?
 * 
 * @param _instance 串口实例
 * @param send_buf 待发送数据的buffer
 * @param send_size how many bytes to send
 */
void USARTSend(USARTInstance_t *_instance, uint8_t *send_buf, uint16_t send_size,USART_TRANSFER_MODE mode);


#endif //__BSP_USART_H

