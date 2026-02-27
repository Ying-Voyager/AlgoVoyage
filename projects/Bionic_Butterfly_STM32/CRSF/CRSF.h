#ifndef _CRSF_H__
#define _CRSF_H__

#include "usart.h"
#include "CRC.h"
#include "CRSF_PROTOCOL.h"
#include "stdbool.h"
#include "string.h"

#define PACKED __attribute__((packed))

extern uint8_t RxBuf[CRSF_MAX_PACKET_SIZE];
extern uint8_t RxBuf_Index;
extern int     CrsfChannels[CRSF_NUM_CHANNELS];

typedef struct {
    uint8_t  device_addr;  // 设备地址（crsf_addr_e）
    uint8_t  frame_size;   // 帧长：payload + 2（type + crc）
    uint8_t  type;         // 帧类型（crsf_frame_type_e）
    uint8_t *data;
} PACKED Crsf_Header_t;

typedef struct {
    unsigned ch0:11;  unsigned ch1:11;  unsigned ch2:11;  unsigned ch3:11;
    unsigned ch4:11;  unsigned ch5:11;  unsigned ch6:11;  unsigned ch7:11;
    unsigned ch8:11;  unsigned ch9:11;  unsigned ch10:11; unsigned ch11:11;
    unsigned ch12:11; unsigned ch13:11; unsigned ch14:11; unsigned ch15:11;
} PACKED crsf_channels_t;

void HandleByteReceived(void);
void ShiftRxBuffer(uint8_t cnt);
void ProcessPacketIn(void);
void PacketChannelsPacked(const Crsf_Header_t *p);
void PacketLinkStatistics(const Crsf_Header_t *p);
static void onPacketLinkStatistics(CrsfLinkStatistics_t *link);

#endif
