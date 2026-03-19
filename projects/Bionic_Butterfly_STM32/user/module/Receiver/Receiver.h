#ifndef __RECEIVER_H__
#define __RECEIVER_H__

#include "main.h"
#include "stdio.h"
#include "string.h"
#include "stdbool.h"
#include "usart.h"

#define SBUS_SIGNAL_OK          0x00
#define SBUS_SIGNAL_LOST        0x01
#define SBUS_SIGNAL_FAILSAFE    0x03

typedef struct
{
	uint16_t CH1;		// 通道1数值
	uint16_t CH2;		// 通道2数值
	uint16_t CH3;		// 通道3数值
	uint16_t CH4;		// 通道4数值
	uint16_t CH5;		// 通道5数值
	uint16_t CH6;		// 通道6数值
	uint16_t CH7;		// 通道7数值
	uint16_t CH8;		// 通道8数值
	uint16_t CH9;		// 通道9数值
	uint16_t CH10;	// 通道10数值
	uint16_t CH11;	// 通道11数值
	uint16_t CH12;	// 通道12数值
	uint16_t CH13;	// 通道13数值
	uint16_t CH14;	// 通道14数值
	uint16_t CH15;	// 通道15数值
	uint16_t CH16;	// 通道16数值
	uint8_t ConnectState;		// 遥控器与接收器连接状态
}SBUS_CH_Struct;

void Sbus_Data_Read(uint8_t *buf);

/*---------------------------------CRSF------------------------------------*/

#define CRSF_BAUDRATE  420000
#define CRSF_NUM_CHANNELS  16
#define CRSF_MAX_PACKET_SIZE  64 													// max declared len is 62+DEST+LEN on top of that = 64
#define CRSF_MAX_PAYLOAD_LEN  (CRSF_MAX_PACKET_SIZE - 4) 	// Max size of payload in [dest] [len] [type] [payload] [crc8]

typedef struct
{
	uint16_t CH1;		// 通道1数值
	uint16_t CH2;		// 通道2数值
	uint16_t CH3;		// 通道3数值
	uint16_t CH4;		// 通道4数值
	uint16_t CH5;		// 通道5数值
	uint16_t CH6;		// 通道6数值
	uint16_t CH7;		// 通道7数值
	uint16_t CH8;		// 通道8数值
	uint16_t CH9;		// 通道9数值
	uint16_t CH10;	// 通道10数值
	uint16_t CH11;	// 通道11数值
	uint16_t CH12;	// 通道12数值
	uint16_t CH13;	// 通道13数值
	uint16_t CH14;	// 通道14数值
	uint16_t CH15;	// 通道15数值
	uint16_t CH16;	// 通道16数值
	uint8_t ConnectState;		// 遥控器与接收器连接状态
}CRSF_CH_Struct;

// 设备地址说明
typedef enum
{
    CRSF_ADDRESS_BROADCAST = 0x00,
    CRSF_ADDRESS_USB = 0x10,
    CRSF_ADDRESS_TBS_CORE_PNP_PRO = 0x80,
    CRSF_ADDRESS_RESERVED1 = 0x8A,
    CRSF_ADDRESS_CURRENT_SENSOR = 0xC0,
    CRSF_ADDRESS_GPS = 0xC2,
    CRSF_ADDRESS_TBS_BLACKBOX = 0xC4,
    CRSF_ADDRESS_FLIGHT_CONTROLLER = 0xC8,
    CRSF_ADDRESS_RESERVED2 = 0xCA,
    CRSF_ADDRESS_RACE_TAG = 0xCC,
    CRSF_ADDRESS_RADIO_TRANSMITTER = 0xEA,
    CRSF_ADDRESS_CRSF_RECEIVER = 0xEC,
    CRSF_ADDRESS_CRSF_TRANSMITTER = 0xEE,
}crsf_addr_e;

// 数据帧类型
typedef enum
{
    CRSF_FRAMETYPE_GPS = 0x02,
    CRSF_FRAMETYPE_BATTERY_SENSOR = 0x08,
    CRSF_FRAMETYPE_LINK_STATISTICS = 0x14,
    CRSF_FRAMETYPE_OPENTX_SYNC = 0x10,
    CRSF_FRAMETYPE_RADIO_ID = 0x3A,
    CRSF_FRAMETYPE_RC_CHANNELS_PACKED = 0x16,
    CRSF_FRAMETYPE_ATTITUDE = 0x1E,
    CRSF_FRAMETYPE_FLIGHT_MODE = 0x21,
    // Extended Header Frames, range: 0x28 to 0x96
    CRSF_FRAMETYPE_DEVICE_PING = 0x28,
    CRSF_FRAMETYPE_DEVICE_INFO = 0x29,
    CRSF_FRAMETYPE_PARAMETER_SETTINGS_ENTRY = 0x2B,
    CRSF_FRAMETYPE_PARAMETER_READ = 0x2C,
    CRSF_FRAMETYPE_PARAMETER_WRITE = 0x2D,
    CRSF_FRAMETYPE_COMMAND = 0x32,
    // MSP commands
    CRSF_FRAMETYPE_MSP_REQ = 0x7A,   // response request using msp sequence as command
    CRSF_FRAMETYPE_MSP_RESP = 0x7B,  // reply with 58 byte chunked binary
    CRSF_FRAMETYPE_MSP_WRITE = 0x7C, // write with 8 byte chunked binary (OpenTX outbound telemetry buffer limit)
}crsf_frame_type_e;

typedef struct crsf_header_s
{
    uint8_t device_addr; 
    uint8_t frame_size;  
    uint8_t type;        
    uint8_t *data;
}crsf_header_t;
 
typedef struct crsf_channels_s
{
    unsigned ch0 : 11;
    unsigned ch1 : 11;
    unsigned ch2 : 11;
    unsigned ch3 : 11;
    unsigned ch4 : 11;
    unsigned ch5 : 11;
    unsigned ch6 : 11;
    unsigned ch7 : 11;
    unsigned ch8 : 11;
    unsigned ch9 : 11;
    unsigned ch10 : 11;
    unsigned ch11 : 11;
    unsigned ch12 : 11;
    unsigned ch13 : 11;
    unsigned ch14 : 11;
    unsigned ch15 : 11;
}crsf_channels_t;

// 信号质量统计
typedef struct crsfPayloadLinkstatistics_s
{
    uint8_t uplink_RSSI_1;
    uint8_t uplink_RSSI_2;
    uint8_t uplink_Link_quality;
    int8_t uplink_SNR;
    uint8_t active_antenna;
    uint8_t rf_Mode;
    uint8_t uplink_TX_Power;
    uint8_t downlink_RSSI;
    uint8_t downlink_Link_quality;
    int8_t downlink_SNR;
}crsfLinkStatistics_t;


void Receiver_Init(void);
int uart_receive_dma_no_it(UART_HandleTypeDef *huart, uint8_t *pData, uint32_t Size);
void Receiver_Handler(UART_HandleTypeDef *huart);
void Crsf_Data_Read(uint8_t *data, uint8_t len);
//void (*onOobData)(uint8_t b);		// OobData is any byte which is not CRSF, including passthrough
void Crc8_init(uint8_t poly);		// poly为crc校验常数
uint8_t Crc8_calc(uint8_t *data, uint8_t len);
void CrsfSerial_shiftRxBuffer(uint8_t cnt);
void CrsfSerial_processPacketIn(uint8_t len);
void CrsfSerial_packetLinkStatistics(const crsf_header_t *p);
void CrsfSerial_packetChannelsPacked(const crsf_header_t *p);

#endif

