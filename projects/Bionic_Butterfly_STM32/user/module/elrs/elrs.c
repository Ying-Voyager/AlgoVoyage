#include "elrs.h"
#include "usart.h"
#include <string.h>  // 添加memset支持
/**
************************************************************************************************
* @brief    遥控器接收机通道函数 - 四驱改造版
* @param    None
* @return   None
* @author   Ying Qichi 2026.3.19
************************************************************************************************
**/
float float_Map(float input_value, float input_min, float input_max, float output_min, float output_max)
{
    float output_value;
    if (input_value < input_min)
    {
        output_value = output_min;
    }
    else if (input_value > input_max)
    {
        output_value = output_max;
    }
    else
    {
        output_value = output_min + (input_value - input_min) * (output_max - output_min) / (input_max - input_min);
    }
    return output_value;
}

float float_Map_with_median(float input_value, float input_min, float input_max, float median, float output_min, float output_max)
{
    float output_median = (output_max - output_min) / 2 + output_min;
    if (input_min >= input_max || output_min >= output_max || median <= input_min || median >= input_max)
    {
        return output_min;
    }

    if (input_value < median)
    {
        return float_Map(input_value, input_min, median, output_min, output_median);
    }
    else
    {
        return float_Map(input_value, median, input_max, output_median, output_max);
    }
}

/**
 * 高速 int16_t 线性映射（带上下限钳位）
 */
static inline int16_t int16_Map(uint16_t x,
                                uint16_t in_min, uint16_t in_max,
                                int16_t out_min, int16_t out_max)
{
    if (in_max <= in_min) return out_min;  // 避免除零和参数错误

    // 钳位输入值
    if (x < in_min) x = in_min;
    else if (x > in_max) x = in_max;

    // 用 32 位防溢出
    int32_t num   = (int32_t)(x - in_min) * (out_max - out_min);
    int32_t denom = (int32_t)(in_max - in_min);

    return (int16_t)(out_min + num / denom);
}

/**
 * 带中位点的高速 int16_t 版本
 */
static inline int16_t int16_Map_with_median(uint16_t x,
                                            uint16_t in_min, uint16_t in_max, uint16_t median,
                                            int16_t out_min, int16_t out_max)
{
    if (in_max <= in_min || median <= in_min || median >= in_max)
        return out_min;

    int16_t out_mid = (int16_t)(((int32_t)out_min + out_max) / 2);

    if (x < median)
        return int16_Map(x, in_min, median, out_min, out_mid);
    else
        return int16_Map(x, median, in_max, out_mid, out_max);
}

// ----------------------------------------------------------

/**
 * 高速 int8_t 线性映射（带钳位）
 */
static inline uint8_t int8_Map(uint16_t x,
                              uint16_t in_min, uint16_t in_max,
                              uint8_t out_min, uint8_t out_max)
{
    if (in_max <= in_min) return out_min;

    if (x < in_min) x = in_min;
    else if (x > in_max) x = in_max;

    int16_t num   = (int16_t)(x - in_min) * (out_max - out_min);
    int16_t denom = (int16_t)(in_max - in_min);

    return (uint8_t)(out_min + num / denom);
}

static inline uint8_t int8_Map_with_median(uint16_t x,
                                          uint16_t in_min, uint16_t in_max, uint16_t median,
                                          uint8_t out_min, uint8_t out_max)
{
    if (in_max <= in_min || median <= in_min || median >= in_max)
        return out_min;

    uint8_t out_mid = (uint8_t)(((int16_t)out_min + out_max) / 2);

    if (x < median)
        return int8_Map(x, in_min, median, out_min, out_mid);
    else
        return int8_Map(x, median, in_max, out_mid, out_max);
}

// 分支消除的 int16 绝对值（两补码）
static inline uint16_t abs16_fast(int16_t x) {
    int16_t m = x >> 15;            // x<0 → -1；x>=0 → 0
    return (uint16_t)((x ^ m) - m); // 等价于 abs(x)
}

extern DMA_HandleTypeDef hdma_usart1_rx;

uint8_t elrs_data_temp[36] = {0};
void ELRS_Init(void)
{
    HAL_UARTEx_ReceiveToIdle_DMA(&huart1, elrs_data_temp, MAX_FRAME_SIZE); // 启用空闲中断接收
    __HAL_DMA_DISABLE_IT(&hdma_usart1_rx, DMA_IT_HT);                      // 关闭DMA传输过半中断
}

ELRS_Data elrs_data;
void ELRS_UARTE_RxCallback(uint16_t Size)
{
	uint8_t date_i = 0;

    if (elrs_data_temp[date_i+0] == CRSF_ADDRESS_FLIGHT_CONTROLLER)
    {
        if (0)
        {
        }
        else if (elrs_data_temp[date_i+2] == CRSF_FRAMETYPE_RC_CHANNELS_PACKED) // 数据帧类型为RC通道数据
        {
            // 解析16个通道数据
            elrs_data.channels[0] = ((uint16_t)elrs_data_temp[date_i+3] >> 0 | ((uint16_t)elrs_data_temp[date_i+4] << 8)) & 0x07FF;
            elrs_data.channels[1] = ((uint16_t)elrs_data_temp[date_i+4] >> 3 | ((uint16_t)elrs_data_temp[date_i+5] << 5)) & 0x07FF;
            elrs_data.channels[2] = ((uint16_t)elrs_data_temp[date_i+5] >> 6 | ((uint16_t)elrs_data_temp[date_i+6] << 2) | ((uint16_t)elrs_data_temp[date_i+7] << 10)) & 0x07FF;
            elrs_data.channels[3] = ((uint16_t)elrs_data_temp[date_i+7] >> 1 | ((uint16_t)elrs_data_temp[date_i+8] << 7)) & 0x07FF;
            elrs_data.channels[4] = ((uint16_t)elrs_data_temp[date_i+8] >> 4 | ((uint16_t)elrs_data_temp[date_i+9] << 4)) & 0x07FF;
            elrs_data.channels[5] = ((uint16_t)elrs_data_temp[date_i+9] >> 7 | ((uint16_t)elrs_data_temp[date_i+10] << 1) | ((uint16_t)elrs_data_temp[date_i+11] << 9)) & 0x07FF;
            elrs_data.channels[6] = ((uint16_t)elrs_data_temp[date_i+11] >> 2 | ((uint16_t)elrs_data_temp[date_i+12] << 6)) & 0x07FF;
            elrs_data.channels[7] = ((uint16_t)elrs_data_temp[date_i+12] >> 5 | ((uint16_t)elrs_data_temp[date_i+13] << 3)) & 0x07FF;
            
            // ==================== 四驱改造版通道映射 ====================
            // 【修改点】将 channels[0] (右摇杆X) 映射到 Roll 用于转向控制
            elrs_data.Roll      = int16_Map_with_median(elrs_data.channels[0], 174, 1811, 992, -400, 400);  // 右摇杆X → 转向
            
            // 左摇杆Y → 频率控制 (5~15Hz)
            // 注意：CH3范围是0~100（不是-100~100），对应CRSF值174~992
            elrs_data.Throttle  = int16_Map(elrs_data.channels[2], 174, 992, 5, 15);
            
            // 右摇杆Y → 幅度控制 (-80~80)
            elrs_data.midpoint  = int16_Map_with_median(elrs_data.channels[1], 174, 1808, 992, -80, 80);
            if((-5 < elrs_data.midpoint) && (elrs_data.midpoint < 5)) {
                elrs_data.midpoint = 0;  // 死区处理
            }
            
            // 原来的Yaw不再使用，但保留以防万一需要
            elrs_data.Yaw = int16_Map_with_median(elrs_data.channels[3], 174, 1808, 992, -100, 100);  // 左摇杆X (备用)
            elrs_data.midpoint_1 = int16_Map_with_median(abs16_fast(elrs_data.Yaw), 0, 100, 50, 0, 30);
            
            // 拨杆F → 启动开关 (0/1)
            elrs_data.Switch = (elrs_data.channels[4] < 1050) ? 0 : (elrs_data.channels[4] > 1700) ? 1 : 0;
            
            // 拨杆B → 模式选择 (0: 收翅 / 1: 立翅 / 2: 飞行)
            elrs_data.Mode = (elrs_data.channels[5] > 1700) ? 2 : ((elrs_data.channels[5] > 900 && elrs_data.channels[5] < 1100) ? 1 : 0);
            
            // 拨杆8 → 扫翅开关 (-100/+100)
            // 拨杆8是两位拨杆，只有两个位置
            elrs_data.Arm = int16_Map_with_median(elrs_data.channels[7], 174, 1811, 992, -100, 100);
        }
        else
        {
            // 其他帧类型暂不处理
        }
    }

    memset(elrs_data_temp, 0, sizeof(elrs_data_temp));
    ELRS_Init();
}
