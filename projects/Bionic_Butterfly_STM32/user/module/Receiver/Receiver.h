#ifndef __RECEIVER_H__
#define __RECEIVER_H__

#include "main.h"
#include "stdio.h"
#include "string.h"
#include "stdbool.h"
#include "usart.h"

/* ========== SBUS ========== */
#define SBUS_SIGNAL_OK        0x00
#define SBUS_SIGNAL_LOST      0x01
#define SBUS_SIGNAL_FAILSAFE  0x03

typedef struct
{
    uint16_t CH1,  CH2,  CH3,  CH4;
    uint16_t CH5,  CH6,  CH7,  CH8;
    uint16_t CH9,  CH10, CH11, CH12;
    uint16_t CH13, CH14, CH15, CH16;
    uint8_t  ConnectState;
} SBUS_CH_Struct;

void Sbus_Data_Read(uint8_t *buf);

/* ========== CRSF ========== */
#define CRSF_BAUDRATE          420000
#define CRSF_NUM_CHANNELS      16
#define CRSF_MAX_PACKET_SIZE   64
#define CRSF_MAX_PAYLOAD_LEN   (CRSF_MAX_PACKET_SIZE - 4)

typedef struct
{
    uint16_t CH1,  CH2,  CH3,  CH4;
    uint16_t CH5,  CH6,  CH7,  CH8;
    uint16_t CH9,  CH10, CH11, CH12;
    uint16_t CH13, CH14, CH15, CH16;
    uint8_t  ConnectState;
} CRSF_CH_Struct;

typedef enum
{
    CRSF_ADDRESS_BROADCAST          = 0x00,
    CRSF_ADDRESS_USB                = 0x10,
    CRSF_ADDRESS_TBS_CORE_PNP_PRO   = 0x80,
    CRSF_ADDRESS_RESERVED1          = 0x8A,
    CRSF_ADDRESS_CURRENT_SENSOR     = 0xC0,
    CRSF_ADDRESS_GPS                = 0xC2,
    CRSF_ADDRESS_TBS_BLACKBOX       = 0xC4,
    CRSF_ADDRESS_FLIGHT_CONTROLLER  = 0xC8,
    CRSF_ADDRESS_RESERVED2          = 0xCA,
    CRSF_ADDRESS_RACE_TAG           = 0xCC,
    CRSF_ADDRESS_RADIO_TRANSMITTER  = 0xEA,
    CRSF_ADDRESS_CRSF_RECEIVER      = 0xEC,
    CRSF_ADDRESS_CRSF_TRANSMITTER   = 0xEE,
} crsf_addr_e;

typedef enum
{
    CRSF_FRAMETYPE_GPS                       = 0x02,
    CRSF_FRAMETYPE_BATTERY_SENSOR            = 0x08,
    CRSF_FRAMETYPE_LINK_STATISTICS           = 0x14,
    CRSF_FRAMETYPE_OPENTX_SYNC               = 0x10,
    CRSF_FRAMETYPE_RADIO_ID                  = 0x3A,
    CRSF_FRAMETYPE_RC_CHANNELS_PACKED        = 0x16,
    CRSF_FRAMETYPE_ATTITUDE                  = 0x1E,
    CRSF_FRAMETYPE_FLIGHT_MODE               = 0x21,
    CRSF_FRAMETYPE_DEVICE_PING               = 0x28,
    CRSF_FRAMETYPE_DEVICE_INFO               = 0x29,
    CRSF_FRAMETYPE_PARAMETER_SETTINGS_ENTRY  = 0x2B,
    CRSF_FRAMETYPE_PARAMETER_READ            = 0x2C,
    CRSF_FRAMETYPE_PARAMETER_WRITE           = 0x2D,
    CRSF_FRAMETYPE_COMMAND                   = 0x32,
    CRSF_FRAMETYPE_MSP_REQ                   = 0x7A,
    CRSF_FRAMETYPE_MSP_RESP                  = 0x7B,
    CRSF_FRAMETYPE_MSP_WRITE                 = 0x7C,
} crsf_frame_type_e;

typedef struct crsf_header_s
{
    uint8_t  device_addr;
    uint8_t  frame_size;
    uint8_t  type;
    uint8_t *data;
} crsf_header_t;

typedef struct crsf_channels_s
{
    unsigned ch0:11;  unsigned ch1:11;  unsigned ch2:11;  unsigned ch3:11;
    unsigned ch4:11;  unsigned ch5:11;  unsigned ch6:11;  unsigned ch7:11;
    unsigned ch8:11;  unsigned ch9:11;  unsigned ch10:11; unsigned ch11:11;
    unsigned ch12:11; unsigned ch13:11; unsigned ch14:11; unsigned ch15:11;
} crsf_channels_t;

typedef struct crsfPayloadLinkstatistics_s
{
    uint8_t uplink_RSSI_1;
    uint8_t uplink_RSSI_2;
    uint8_t uplink_Link_quality;
    int8_t  uplink_SNR;
    uint8_t active_antenna;
    uint8_t rf_Mode;
    uint8_t uplink_TX_Power;
    uint8_t downlink_RSSI;
    uint8_t downlink_Link_quality;
    int8_t  downlink_SNR;
} crsfLinkStatistics_t;

void     Receiver_Init(void);
void     Crsf_Data_Read(uint8_t *data, uint8_t len);
void     Crc8_init(uint8_t poly);
uint8_t  Crc8_calc(uint8_t *data, uint8_t len);
void     CrsfSerial_shiftRxBuffer(uint8_t cnt);
void     CrsfSerial_processPacketIn(uint8_t len);
void     CrsfSerial_packetLinkStatistics(const crsf_header_t *p);
void     CrsfSerial_packetChannelsPacked(const crsf_header_t *p);

#endif
