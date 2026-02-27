#include "CRSF.h"
/**
 * @brief   CRSF协议数据包解析
 * @author  Ying Qichi
 */

uint8_t RxBuf[CRSF_MAX_PACKET_SIZE];
uint8_t RxBuf_Index;

int CrsfChannels[CRSF_NUM_CHANNELS];
CrsfLinkStatistics_t LinkStatistics;

void HandleByteReceived(void)
{
    bool reprocess;
    do
    {
        reprocess = false;
        if (RxBuf_Index > 1)
        {
            uint8_t len = RxBuf[1];
            if (len < 3 || len > (CRSF_MAX_PAYLOAD_LEN + 2))
            {
                ShiftRxBuffer(1);
                reprocess = true;
            }
            else if (RxBuf_Index >= (len + 2))
            {
                uint8_t inCrc = RxBuf[2 + len - 1];
                uint8_t crc   = Calc(&RxBuf[2], len - 1);
                if (crc == inCrc)
                {
                    ProcessPacketIn();
                    ShiftRxBuffer(len + 2);
                }
                else
                {
                    ShiftRxBuffer(1);
                }
                reprocess = true;
            }
        }
    } while (reprocess);
}

void ShiftRxBuffer(uint8_t cnt)
{
    if (cnt >= RxBuf_Index) { RxBuf_Index = 0; return; }
    uint8_t *src = &RxBuf[cnt];
    uint8_t *dst = &RxBuf[0];
    RxBuf_Index -= cnt;
    uint8_t left = RxBuf_Index;
    while (left--)
        *dst++ = *src++;
}

void ProcessPacketIn(void)
{
    const Crsf_Header_t *hdr = (Crsf_Header_t *)RxBuf;
    if (hdr->device_addr == CRSF_ADDRESS_FLIGHT_CONTROLLER)
    {
        switch (hdr->type)
        {
        case CRSF_FRAMETYPE_RC_CHANNELS_PACKED:
            PacketChannelsPacked(hdr);
            break;
        case CRSF_FRAMETYPE_LINK_STATISTICS:
            PacketLinkStatistics(hdr);
            break;
        }
    }
}

void PacketChannelsPacked(const Crsf_Header_t *p)
{
    crsf_channels_t *ch = (crsf_channels_t *)&p->data;
    CrsfChannels[0]  = ch->ch0;  CrsfChannels[1]  = ch->ch1;
    CrsfChannels[2]  = ch->ch2;  CrsfChannels[3]  = ch->ch3;
    CrsfChannels[4]  = ch->ch4;  CrsfChannels[5]  = ch->ch5;
    CrsfChannels[6]  = ch->ch6;  CrsfChannels[7]  = ch->ch7;
    CrsfChannels[8]  = ch->ch8;  CrsfChannels[9]  = ch->ch9;
    CrsfChannels[10] = ch->ch10; CrsfChannels[11] = ch->ch11;
    CrsfChannels[12] = ch->ch12; CrsfChannels[13] = ch->ch13;
    CrsfChannels[14] = ch->ch14; CrsfChannels[15] = ch->ch15;
}

void PacketLinkStatistics(const Crsf_Header_t *p)
{
    const CrsfLinkStatistics_t *link = (CrsfLinkStatistics_t *)p->data;
    memcpy(&LinkStatistics, &link, sizeof(LinkStatistics));
    onPacketLinkStatistics(&LinkStatistics);
}

static void onPacketLinkStatistics(CrsfLinkStatistics_t *link)
{
    // 可在此处添加链路统计回调逻辑
}
