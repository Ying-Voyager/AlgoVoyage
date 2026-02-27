#ifndef _CRSF_PROTOCOL_H__
#define _CRSF_PROTOCOL_H__

#define CRSF_BAUDRATE            420000  // 波特率
#define CRSF_NUM_CHANNELS        16      // 通道数
#define CRSF_CHANNEL_VALUE_MIN   172     // 通道最小值（987us）
#define CRSF_CHANNEL_VALUE_1000  191
#define CRSF_CHANNEL_VALUE_MID   992
#define CRSF_CHANNEL_VALUE_2000  1792
#define CRSF_CHANNEL_VALUE_MAX   1811    // 通道最大值（2012us）
#define CRSF_CHANNEL_VALUE_SPAN  (CRSF_CHANNEL_VALUE_MAX - CRSF_CHANNEL_VALUE_MIN)
#define CRSF_MAX_PACKET_SIZE     64      // 最大帧长（62 + DEST + LEN）
#define CRSF_MAX_PAYLOAD_LEN     (CRSF_MAX_PACKET_SIZE - 4)

enum {
    CRSF_FRAME_LENGTH_ADDRESS       = 1,
    CRSF_FRAME_LENGTH_FRAMELENGTH   = 1,
    CRSF_FRAME_LENGTH_TYPE          = 1,
    CRSF_FRAME_LENGTH_CRC           = 1,
    CRSF_FRAME_LENGTH_TYPE_CRC      = 2,
    CRSF_FRAME_LENGTH_EXT_TYPE_CRC  = 4,
    CRSF_FRAME_LENGTH_NON_PAYLOAD   = 4,
};

enum {
    CRSF_FRAME_GPS_PAYLOAD_SIZE            = 15,
    CRSF_FRAME_BATTERY_SENSOR_PAYLOAD_SIZE = 8,
    CRSF_FRAME_LINK_STATISTICS_PAYLOAD_SIZE = 10,
    CRSF_FRAME_RC_CHANNELS_PAYLOAD_SIZE    = 22,  // 11bits × 16ch = 22 bytes
    CRSF_FRAME_ATTITUDE_PAYLOAD_SIZE       = 6,
};

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

typedef enum
{
    CRSF_ADDRESS_BROADCAST          = 0x00,
    CRSF_ADDRESS_USB                = 0x10,
    CRSF_ADDRESS_TBS_CORE_PNP_PRO   = 0x80,
    CRSF_ADDRESS_RESERVED1          = 0x8A,
    CRSF_ADDRESS_CURRENT_SENSOR     = 0xC0,
    CRSF_ADDRESS_GPS                = 0xC2,
    CRSF_ADDRESS_TBS_BLACKBOX       = 0xC4,
    CRSF_ADDRESS_FLIGHT_CONTROLLER  = 0xD5,
    CRSF_ADDRESS_RESERVED2          = 0xCA,
    CRSF_ADDRESS_RACE_TAG           = 0xCC,
    CRSF_ADDRESS_RADIO_TRANSMITTER  = 0xEA,
    CRSF_ADDRESS_CRSF_RECEIVER      = 0xEC,
    CRSF_ADDRESS_CRSF_TRANSMITTER   = 0xEE,
} crsf_addr_e;

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
} CrsfLinkStatistics_t;

#endif
