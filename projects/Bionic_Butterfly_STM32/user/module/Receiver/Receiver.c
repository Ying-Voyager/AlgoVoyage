#include "Receiver.h"

/*--------------SBUS-------------*/
SBUS_CH_Struct SBUS_CH;


/*--------------CRSF-------------*/
uint8_t Crsf_Rx_buffer[64]; 		
CRSF_CH_Struct CRSF_CH;
uint8_t _lut[256];
uint8_t _rxBuf[CRSF_MAX_PACKET_SIZE];
uint8_t _rxBufPos;

int _channels[CRSF_NUM_CHANNELS];
crsfLinkStatistics_t _linkStatistics;
void (*onPacketLinkStatistics)(crsfLinkStatistics_t *ls);

// 开启串口空闲中断
void Receiver_Init(void)
{
//	uart_receive_dma_no_it(&huart1, Crsf_Rx_buffer, CRSF_MAX_PACKET_SIZE);
	
	Crc8_init(0xD5);
//	__HAL_UART_CLEAR_IDLEFLAG(&huart1);
	
	HAL_UARTEx_ReceiveToIdle_DMA(&huart1, Crsf_Rx_buffer, 64);
    __HAL_DMA_DISABLE_IT(&hdma_usart1_rx, DMA_IT_HT);                      // 关闭DMA传输过半中断
  
	
}

//int uart_receive_dma_no_it(UART_HandleTypeDef *huart, uint8_t *pData, uint32_t Size)
//{
//    uint32_t tmp = 0;

//    tmp = huart->RxState;
//    if (tmp == HAL_UART_STATE_READY)
//    {
//        if ((pData == NULL) || (Size == 0))
//        {
//            return HAL_ERROR;
//        }

//        /* Process Locked */
//        __HAL_LOCK(huart);

//        huart->pRxBuffPtr = pData;
//        huart->RxXferSize = Size;

//        huart->ErrorCode = HAL_UART_ERROR_NONE;

//        /* Enable the DMA Stream */
//        HAL_DMA_Start(huart->hdmarx, (uint32_t)&huart->Instance->DR,
//                      (uint32_t)pData, Size);

//        /* Enable the DMA transfer for the receiver request by setting the DMAR bit
//        in the UART CR3 register */
//        SET_BIT(huart->Instance->CR3, USART_CR3_DMAR);

//        /* Process Unlocked */
//        __HAL_UNLOCK(huart);

//        return HAL_OK;
//    }
//    else
//    {
//        return HAL_BUSY;
//    }
//}

//// 接收中断处理
//void Receiver_Handler(UART_HandleTypeDef *huart)
//{
//	// 判断是否为串口空闲中断以及是否为接收机串口对应的句柄
//	if(__HAL_UART_GET_FLAG(huart, UART_FLAG_IDLE) && __HAL_UART_GET_IT_SOURCE(huart, UART_IT_IDLE))
//	{
//		// 清除空闲中断标志位
//		__HAL_UART_CLEAR_IDLEFLAG(huart);
//		if (huart == &huart1)
//    {
//      // 停止DMA传输
//      __HAL_DMA_DISABLE(huart->hdmarx);

//			// 判断接收到的字节数
//      uint8_t size = CRSF_MAX_PACKET_SIZE - __HAL_DMA_GET_COUNTER(huart1.hdmarx);
//			
//			// 处理接收数据
//			Crsf_Data_Read(Crsf_Rx_buffer, Crsf_Rx_buffer[1]);
//			
//			// 重新开启接收
//			HAL_UART_Receive_DMA(&huart1, Crsf_Rx_buffer, 64);

//    }
//		
//	}	
//}


void Sbus_Data_Read(uint8_t *buf)
{
	if(buf[23] == 0)		// 判断是否出现数据混乱
	{
		SBUS_CH.CH1  = ((int16_t)buf[ 1] >> 0 | ((int16_t)buf[ 2] << 8 )) & 0x07FF;
		SBUS_CH.CH2  = ((int16_t)buf[ 2] >> 3 | ((int16_t)buf[ 3] << 5 )) & 0x07FF;
		SBUS_CH.CH3  = ((int16_t)buf[ 3] >> 6 | ((int16_t)buf[ 4] << 2 ) | (int16_t)buf[ 5] << 10 ) & 0x07FF;
		SBUS_CH.CH4  = ((int16_t)buf[ 5] >> 1 | ((int16_t)buf[ 6] << 7 )) & 0x07FF;
		SBUS_CH.CH5  = ((int16_t)buf[ 6] >> 4 | ((int16_t)buf[ 7] << 4 )) & 0x07FF;
		SBUS_CH.CH6  = ((int16_t)buf[ 7] >> 7 | ((int16_t)buf[ 8] << 1 ) | (int16_t)buf[9] << 9 ) & 0x07FF;
		SBUS_CH.CH7  = ((int16_t)buf[ 9] >> 2 | ((int16_t)buf[10] << 6 )) & 0x07FF;
		SBUS_CH.CH8  = ((int16_t)buf[10] >> 5 | ((int16_t)buf[11] << 3 )) & 0x07FF;
		SBUS_CH.CH9	 = ((int16_t)buf[12] << 0 | ((int16_t)buf[13] << 8 )) & 0x07FF;
		SBUS_CH.CH10 = ((int16_t)buf[13] >> 3 | ((int16_t)buf[14] << 5 )) & 0x07FF;
		SBUS_CH.CH11 = ((int16_t)buf[14] >> 6 | ((int16_t)buf[15] << 2 ) | (int16_t)buf[16] << 10 ) & 0x07FF;
		SBUS_CH.CH12 = ((int16_t)buf[16] >> 1 | ((int16_t)buf[17] << 7 )) & 0x07FF;
		SBUS_CH.CH13 = ((int16_t)buf[17] >> 4 | ((int16_t)buf[18] << 4 )) & 0x07FF;
		SBUS_CH.CH14 = ((int16_t)buf[18] >> 7 | ((int16_t)buf[19] << 1 ) | (int16_t)buf[20] << 9 ) & 0x07FF;
		SBUS_CH.CH15 = ((int16_t)buf[20] >> 2 | ((int16_t)buf[21] << 6 )) & 0x07FF;
		SBUS_CH.CH16 = ((int16_t)buf[21] >> 5 | ((int16_t)buf[22] << 3 )) & 0x07FF;
		
		SBUS_CH.ConnectState = SBUS_SIGNAL_OK;
	}
	else
	{
//		if (buf[23] & (1<<5))//2
//		{
//			SBUS_CH.ConnectState = SBUS_SIGNAL_LOST;		// 信号丢失
//		}
//		if (buf[23] & (1<<4))//3
//		{
//			SBUS_CH.ConnectState = SBUS_SIGNAL_FAILSAFE;		// 失控保护激活
//		}
	}
}

void Crsf_Data_Read(uint8_t *data, uint8_t len)
{
	uint8_t inCrc = data[2 + len - 1];
	// CRC计算
	uint8_t crc = Crc8_calc(&data[2], len - 1);
	
	if( (data[2] == CRSF_FRAMETYPE_RC_CHANNELS_PACKED)&&(inCrc == crc) )
	{
		CRSF_CH.CH1  = ((int16_t)data[ 3] >> 0 | ((int16_t)data[ 4] << 8 )) & 0x07FF;
		CRSF_CH.CH2  = ((int16_t)data[ 4] >> 3 | ((int16_t)data[ 5] << 5 )) & 0x07FF;
		CRSF_CH.CH3  = ((int16_t)data[ 5] >> 6 | ((int16_t)data[ 6] << 2 ) | (int16_t)data[ 7] << 10 ) & 0x07FF;
		CRSF_CH.CH4  = ((int16_t)data[ 7] >> 1 | ((int16_t)data[ 8] << 7 )) & 0x07FF;
		CRSF_CH.CH5  = ((int16_t)data[ 8] >> 4 | ((int16_t)data[ 9] << 4 )) & 0x07FF;
		CRSF_CH.CH6  = ((int16_t)data[ 9] >> 7 | ((int16_t)data[10] << 1 ) | (int16_t)data[11] << 9 ) & 0x07FF;
		CRSF_CH.CH7  = ((int16_t)data[11] >> 2 | ((int16_t)data[12] << 6 )) & 0x07FF;
		CRSF_CH.CH8  = ((int16_t)data[12] >> 5 | ((int16_t)data[13] << 3 )) & 0x07FF;
		CRSF_CH.CH9	 = ((int16_t)data[14] << 0 | ((int16_t)data[15] << 8 )) & 0x07FF;
		CRSF_CH.CH10 = ((int16_t)data[15] >> 3 | ((int16_t)data[16] << 5 )) & 0x07FF;
		CRSF_CH.CH11 = ((int16_t)data[16] >> 6 | ((int16_t)data[17] << 2 ) | (int16_t)data[18] << 10 ) & 0x07FF;
		CRSF_CH.CH12 = ((int16_t)data[18] >> 1 | ((int16_t)data[19] << 7 )) & 0x07FF;
		CRSF_CH.CH13 = ((int16_t)data[19] >> 4 | ((int16_t)data[20] << 4 )) & 0x07FF;
		CRSF_CH.CH14 = ((int16_t)data[20] >> 7 | ((int16_t)data[21] << 1 ) | (int16_t)data[22] << 9 ) & 0x07FF;
		CRSF_CH.CH15 = ((int16_t)data[22] >> 2 | ((int16_t)data[23] << 6 )) & 0x07FF;
		CRSF_CH.CH16 = ((int16_t)data[23] >> 5 | ((int16_t)data[24] << 3 )) & 0x07FF;		
	}
}

// 获取CRC8校验余数
void Crc8_init(uint8_t poly)		// poly为crc校验常数  0xD5
{
    for (int idx=0; idx<256; ++idx)
    {
        uint8_t crc = idx;
        for (int shift=0; shift<8; ++shift)
        {
            crc = (crc << 1) ^ ((crc & 0x80) ? poly : 0);
        }
        _lut[idx] = crc & 0xff;
    }
}

// CRC8处理，得到计算的CRC
uint8_t Crc8_calc(uint8_t *data, uint8_t len)
{
    uint8_t crc = 0;
    while (len--)
    {
        crc = _lut[crc ^ *data++];
    }
    return crc;
}

//
void CrsfSerial_processPacketIn(uint8_t len)
{
    const crsf_header_t *hdr = (crsf_header_t *)_rxBuf;
    if (hdr->device_addr == CRSF_ADDRESS_FLIGHT_CONTROLLER)
    {
        switch (hdr->type)
        {
//        case CRSF_FRAMETYPE_GPS:
//            packetGps(hdr);
//            break;
        case CRSF_FRAMETYPE_RC_CHANNELS_PACKED:
            CrsfSerial_packetChannelsPacked(hdr);
            break;
//        case CRSF_FRAMETYPE_LINK_STATISTICS:
//            CrsfSerial_packetLinkStatistics(hdr);
//            break;
        }
    } // CRSF_ADDRESS_FLIGHT_CONTROLLER
}

// 信号质量回调
void CrsfSerial_packetLinkStatistics(const crsf_header_t *p)
{
    const crsfLinkStatistics_t *link = (crsfLinkStatistics_t *)p->data;
    memcpy(&_linkStatistics, link, sizeof(_linkStatistics));

    if (onPacketLinkStatistics)
        onPacketLinkStatistics(&_linkStatistics);
}

// 获取通道数值
void CrsfSerial_packetChannelsPacked(const crsf_header_t *p)
{
    crsf_channels_t *ch = (crsf_channels_t *)&p->data;
    _channels[0] = ch->ch0;
    _channels[1] = ch->ch1;
    _channels[2] = ch->ch2;
    _channels[3] = ch->ch3;
    _channels[4] = ch->ch4;
    _channels[5] = ch->ch5;
    _channels[6] = ch->ch6;
    _channels[7] = ch->ch7;
    _channels[8] = ch->ch8;
    _channels[9] = ch->ch9;
    _channels[10] = ch->ch10;
    _channels[11] = ch->ch11;
    _channels[12] = ch->ch12;
    _channels[13] = ch->ch13;
    _channels[14] = ch->ch14;
    _channels[15] = ch->ch15;

}

void CrsfSerial_shiftRxBuffer(uint8_t cnt)
{
    // If removing the whole thing, just set pos to 0
    if (cnt >= _rxBufPos)
    {
        _rxBufPos = 0;
        return;
    }

//    if (cnt == 1 && onOobData)
//        onOobData(_rxBuf[0]);

    // Otherwise do the slow shift down
    uint8_t *src = &_rxBuf[cnt];
    uint8_t *dst = &_rxBuf[0];
    _rxBufPos -= cnt;
    uint8_t left = _rxBufPos;
    while (left--)
        *dst++ = *src++;
}

void CrsfSerial_handleByteReceived()
{
    bool reprocess;
    do
    {
        reprocess = false;
        if (_rxBufPos > 1)
        {
            uint8_t len = _rxBuf[1];
            // Sanity check the declared length isn't outside Type + X{1,CRSF_MAX_PAYLOAD_LEN} + CRC
            // assumes there never will be a CRSF message that just has a type and no data (X)
            if (len < 3 || len > (CRSF_MAX_PAYLOAD_LEN + 2))
            {
                CrsfSerial_shiftRxBuffer(1);
                reprocess = true;
            }

            else if (_rxBufPos >= (len + 2))
            {
                uint8_t inCrc = _rxBuf[2 + len - 1];
                uint8_t crc = Crc8_calc(&_rxBuf[2], len - 1);
                if (crc == inCrc)
                {
                    CrsfSerial_processPacketIn(len);
                    CrsfSerial_shiftRxBuffer(len + 2);
                    reprocess = true;
                }
                else
                {
                    CrsfSerial_shiftRxBuffer(1);
                    reprocess = true;
                }
            }  // if complete packet
        } // if pos > 1
    } while (reprocess);
}
