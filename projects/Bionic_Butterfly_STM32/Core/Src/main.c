/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body - 四驱仿生蝴蝶改造版
  ******************************************************************************
  * @attention
  *
  * 四驱改造说明:
  * 1. 4个磁编码器，4个电机（每个电机独立反馈）
  * 2. 编码器1→M1(左前), 编码器3→M3(右前)
  *    编码器2→M2(左后), 编码器4→M4(右后)
  * 3. 电机1,3是前翼（左右）；电机2,4是后翼（左右）
  *
  * 遥控器通道映射:
  * - 通道1 (右摇杆X): 控制左右差速转向 (右推=左翼幅度大=右转)
  * - 通道2 (右摇杆Y): 控制扑翼幅度 (上推=幅度增大, 范围:45~90度)
  * - 通道3 (左摇杆Y): 控制扑翼频率 (上推=频率增大, 范围:5~15Hz)
  * - 通道4 (左摇杆X): 控制前后差速俯仰 (右推=前翼加速=抬头)
  * - 通道5 (拨杆F): 启动/停止开关 (上=启动, 下=停止)
  * - 通道6 (拨杆B): 模式选择 (上=Mode2扑翼, 中=Mode1立翅, 下=Mode0收翅)
  * 
  * Mode1特殊用途:
  * - 通道2 (右摇杆Y): 微调立翅角度 (范围:±80, 用于调试基准点)
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "adc.h"
#include "dma.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "elrs.h"
#include "AS5600_PWM.h"
#include <stdint.h>
#include <stdbool.h>

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */
/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

// ========================================
// ===== 基准点配置（4个电机独立配置）=====
// ========================================
// 说明：由于编码器机械零点不对齐，每个电机需要独立的基准点
// 调试方法：手动将翅膀调整到目标位置，读取编码器值，填入下面

// ----- Mode1: 立翅基准点（竖直向上，约90度）-----
// 用于静态立翅模式，翅膀竖直向上
int16_t motor_LF_standing = 1444;  // 左前翼立翅位置
int16_t motor_RF_standing = 3244;  // 右前翼立翅位置
int16_t motor_LR_standing = 3144;  // 左后翼立翅位置
int16_t motor_RR_standing = 1344;  // 右后翼立翅位置

// ----- Mode2: 扑翼基准点（水平，约0度）-----
// 用于飞行模式的扑翼中心，翅膀水平位置
int16_t motor_LF_flying = 2144;    // 左前翼扑翼中心
int16_t motor_RF_flying = 2344;    // 右前翼扑翼中心
int16_t motor_LR_flying = 2444;    // 左后翼扑翼中心
int16_t motor_RR_flying = 2544;    // 右后翼扑翼中心

// ----- Mode0: 收翅基准点（收起，约45度）-----
// 用于收翅模式，翅膀收起贴近身体
int16_t motor_LF_folded = 1794;    // 左前翼收翅位置
int16_t motor_RF_folded = 2794;    // 右前翼收翅位置
int16_t motor_LR_folded = 2794;    // 左后翼收翅位置
int16_t motor_RR_folded = 1944;    // 右后翼收翅位置

// 基准点调试方法：
// 1. 进入Mode1立翅模式
// 2. 手动调整翅膀到目标位置（立翅/水平/收翅）
// 3. 读取编码器数值，填入对应的基准点变量
// 4. 重新编译烧录后验证位置是否正确
// 
// 电机布局： M1(左前) M3(右前)
//           M2(左后) M4(右后)
// ========================================

// 前后翼相位差设置（单位：cos表索引，范围：0-8）
// 0 = 无相位差（同步）
// 2 = 后翼落后约40度（默认）
// 4 = 后翼落后约80度
int8_t phase_offset = 2;

// Mode2扑翼开关状态（使用拨杆8控制）
static uint8_t mode2_flapping = 0;  // 0=悬停在水平位置, 1=正在扑翼
static int8_t last_arm_state = 0;   // 上一次拨杆8的状态

// ========================================
// ===== 编码器方向自动检测 =====
// ========================================
// 自动检测各电机编码器方向，适应不同的安装方式
// 立翅 < 水平 → 编码器增大=向下 → 方向系数=-1
// 立翅 > 水平 → 编码器增大=向上 → 方向系数=+1
int8_t motor_LF_direction = 0;  // 左前翼方向系数
int8_t motor_RF_direction = 0;  // 右前翼方向系数
int8_t motor_LR_direction = 0;  // 左后翼方向系数
int8_t motor_RR_direction = 0;  // 右后翼方向系数
// ========================================

// 相位累加器（16位：0..65535 表示一整周期）
static uint16_t g_phase16 = 0;

// 上一次循环的时间戳（ms）
static uint32_t g_last_ms = 0;

// 目标角度变量
int motor_LF_set;  // 左前翼目标角度
int motor_RF_set;  // 右前翼目标角度
int motor_LR_set;  // 左后翼目标角度
int motor_RR_set;  // 右后翼目标角度

// 遥控器通道变量
int Throttle, Amplitude, Roll, Frequency;

long map(long x, long in_min, long in_max, long out_min, long out_max) {
  const long run = in_max - in_min;
  if (run == 0) {
    return -1;  // AVR returns -1, SAM returns 0
  }
  const long rise = out_max - out_min;
  const long delta = x - in_min;
  return (delta * rise) / run + out_min;
}

void motor_disable()  // 翅膀失能
{
	TIM2->CCR1 = 0;   // M1
	TIM2->CCR2 = 0;   // M1
	TIM2->CCR3 = 0;   // M2
	TIM2->CCR4 = 0;   // M2
	TIM3->CCR1 = 0;   // M3
	TIM3->CCR2 = 0;   // M3
	TIM3->CCR3 = 0;   // M4
	TIM3->CCR4 = 0;   // M4
}

void motor_stop()  // 翅膀暂停
{
	TIM2->CCR1 = 19999;   // M1
	TIM2->CCR2 = 19999;   // M1
	TIM2->CCR3 = 19999;   // M2
	TIM2->CCR4 = 19999;   // M2
	TIM3->CCR1 = 19999;   // M3
	TIM3->CCR2 = 19999;   // M3
	TIM3->CCR3 = 19999;   // M4
	TIM3->CCR4 = 19999;   // M4
}

void motor_test()  // 调试：前翅膀水平打开，运行后翅膀向下摆动，即为电机方向正确
{
	Set_Pwm(3000, 3000, 3000, 3000);
	HAL_Delay(100); 
	Set_Pwm(0, 0, 0, 0);
	while(1);
}
/**
 * @brief  编码器方向自动检测初始化
 * @note   根据立翅和水平位置的大小关系，自动计算每个电机的方向系数
 *         立翅 < 水平 → 方向系数 = -1
 *         立翅 > 水平 → 方向系数 = +1
 * @retval None
 */
void Motor_Direction_Init(void)
{
	// 自动检测左前翼方向
	motor_LF_direction = (motor_LF_standing < motor_LF_flying) ? -1 : 1;
	
	// 自动检测右前翼方向
	motor_RF_direction = (motor_RF_standing < motor_RF_flying) ? -1 : 1;
	
	// 自动检测左后翼方向
	motor_LR_direction = (motor_LR_standing < motor_LR_flying) ? -1 : 1;
	
	// 自动检测右后翼方向
	motor_RR_direction = (motor_RR_standing < motor_RR_flying) ? -1 : 1;
}



// 分支消除的 int16 绝对值（两补码）
static inline uint16_t abs16_fast(int16_t x) {
    int16_t m = x >> 15;            // x<0 → -1；x>=0 → 0
    return (uint16_t)((x ^ m) - m); // 等价于 abs(x)
}

// ====== 定点余弦表（Q15），9 点 ======
static const int16_t COS_Q15_9[9] = {
    30784, 25133,  16384,
    11207,     0, -11207,
   -16384,-25133,-30784
};

// Q15 乘法： (a * b) >> 15
static inline int16_t q15_mul(int16_t a, int16_t b) {
    return (int16_t)(((int32_t)a * (int32_t)b) >> 15);
}

#ifndef MIN
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#endif

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
int Take_off_Flag = 0;
/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */
  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_USART1_UART_Init();
  MX_TIM2_Init();
  MX_TIM3_Init();
  MX_TIM1_Init();
  MX_ADC1_Init();
  /* USER CODE BEGIN 2 */
	HAL_ADCEx_Calibration_Start(&hadc1);
	
	// TIM2: M1和M2电机 (PA15, PB3, PA2, PA3)
	HAL_TIM_Base_Start(&htim2);
	HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);  // M1
	HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_2);  // M1
	HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_3);  // M2
	HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_4);  // M2
	

	// 因为ADC_MspInit可能影响GPIOA配置
	GPIO_InitTypeDef GPIO_InitStruct_PA23 = {0};
	GPIO_InitStruct_PA23.Pin = GPIO_PIN_2|GPIO_PIN_3;  // PA2和PA3
	GPIO_InitStruct_PA23.Mode = GPIO_MODE_AF_PP;       // 复用推挽输出
	GPIO_InitStruct_PA23.Pull = GPIO_NOPULL;
	GPIO_InitStruct_PA23.Speed = GPIO_SPEED_FREQ_LOW;
	GPIO_InitStruct_PA23.Alternate = GPIO_AF2_TIM2;    // TIM2复用功能
	HAL_GPIO_Init(GPIOA, &GPIO_InitStruct_PA23);
	
	// TIM3: M3和M4电机
	HAL_TIM_Base_Start(&htim3);
	HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);  // M3
	HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_2);  // M3
	HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_3);  // M4
	HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_4);  // M4
	
	HAL_Delay(1000);		// 等待上电完成
	MX_USART1_UART_Init();	// 开启接收机串口
	ELRS_Init();			// 接收机初始化
	Chassis_PID_Init(); 	// 电机PID初始化
	Motor_Direction_Init();
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
	g_last_ms = HAL_GetTick();  // 初始化时间戳

  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
	StarAndGetResult();  // 读取4个编码器角度（每个电机独立反馈）
	
	uint32_t now = HAL_GetTick();
	(void)now;

    // ============ 启动开关判断 (通道5 - 拨杆F) ============
    if (elrs_data.Switch == 1)
    {
        // ============ 模式选择 (通道6 - 拨杆B) ============
        
        // ======== Mode 2: 飞行模式 - 前后翼独立频率控制 ========
        if (elrs_data.Mode == 2)
        {
        motor_1_pid.Kp = 20;
        motor_2_pid.Kp = 20;
        motor_3_pid.Kp = 20;
        motor_4_pid.Kp = 20;
		
		motor_1_pid.Kd = 3;
		motor_2_pid.Kd = 3;
		motor_3_pid.Kd = 3;
		motor_4_pid.Kd = 3;
			
			// 计算基准角度（使用扫翅基准点）
			// 4个电机使用各自的flying基准点
			const int16_t base_LF = motor_LF_flying;  // 左前翼
			const int16_t base_RF = motor_RF_flying;  // 右前翼
			const int16_t base_LR = motor_LR_flying;  // 左后翼
			const int16_t base_RR = motor_RR_flying;  // 右后翼
			
			// ============ 检测拨杆8的翻转（切换扫翅开关）============
			// 检测拨杆8从-100切换到+100，或从+100切换到-100
			if ((last_arm_state < 0 && elrs_data.Arm > 0) ||   // -100 → +100
				(last_arm_state > 0 && elrs_data.Arm < 0))     // +100 → -100
			{
				// 拨杆8翻转，切换扫翅状态
				mode2_flapping = !mode2_flapping;
			}
			last_arm_state = elrs_data.Arm;
			
			// ============ 根据扫翅开关决定行为 ============
			if (mode2_flapping == 0)
			{
				// ====== 状态1: 悬停在水平位置 ======
				// 缓慢移动并保持在水平位置
				static uint32_t hover_last_time = 0;
				const uint32_t HOVER_INTERVAL = 5;  // 5ms更新一次
				const int16_t MAX_STEP = 50;        // 每步最多移动50
				
				if ((int32_t)(now - hover_last_time) >= HOVER_INTERVAL)
				{
					// 左前翼平滑移动到水平位置
					int16_t current_LF = Wings_Data.Wings_motor[0].Corrective_Angle;
					if (current_LF < base_LF) {
						current_LF += MIN(MAX_STEP, base_LF - current_LF);
					} else if (current_LF > base_LF) {
						current_LF -= MIN(MAX_STEP, current_LF - base_LF);
					}
					Wings_Data.Wings_motor[0].Target_Angle = current_LF;
					
					// 右前翼平滑移动到水平位置
					int16_t current_RF = Wings_Data.Wings_motor[1].Corrective_Angle;
					if (current_RF < base_RF) {
						current_RF += MIN(MAX_STEP, base_RF - current_RF);
					} else if (current_RF > base_RF) {
						current_RF -= MIN(MAX_STEP, current_RF - base_RF);
					}
					Wings_Data.Wings_motor[1].Target_Angle = current_RF;
					
					// 左后翼平滑移动到水平位置
					int16_t current_LR = Wings_Data.Wings_motor[2].Corrective_Angle;
					if (current_LR < base_LR) {
						current_LR += MIN(MAX_STEP, base_LR - current_LR);
					} else if (current_LR > base_LR) {
						current_LR -= MIN(MAX_STEP, current_LR - base_LR);
					}
					Wings_Data.Wings_motor[2].Target_Angle = current_LR;
					
					// 右后翼平滑移动到水平位置
					int16_t current_RR = Wings_Data.Wings_motor[3].Corrective_Angle;
					if (current_RR < base_RR) {
						current_RR += MIN(MAX_STEP, base_RR - current_RR);
					} else if (current_RR > base_RR) {
						current_RR -= MIN(MAX_STEP, current_RR - base_RR);
					}
					Wings_Data.Wings_motor[3].Target_Angle = current_RR;
					
					hover_last_time = now;
				}
				
				StarAndGetResult();
				Motor_PID_Control();
			}
			else
			{
				// ====== 状态2: 正常扑翼 ======
			
			// 遥控器通道映射
			// elrs_data.Throttle  -> 整体频率 (通道3, 左摇杆Y)  范围: 5~15Hz
			// elrs_data.Yaw       -> 前后频率差 (通道4, 左摇杆X)  范围: ±2Hz
			// elrs_data.midpoint  -> 整体幅度 (通道2, 右摇杆Y)  范围: 45~90度
			// elrs_data.Roll      -> 左右幅度差 (通道1, 右摇杆X)  范围: ±25度
			

			// ============ 幅度控制算法（左右差速转向）============
			// Step1: Y轴控制中心幅度 (45~90度)
			int16_t center_amp = 45 + ((elrs_data.midpoint + 80) * 45) / 160;
      if (center_amp < 45) center_amp = 45;
      if (center_amp > 90) center_amp = 90;
			
			// Step2: X轴控制左右差值 (-25~+25度)
			int16_t diff = (elrs_data.Roll * 25) / 400;
			
			// Step3: 计算左右幅度
			int16_t amp_L = center_amp + diff;
			int16_t amp_R = center_amp - diff;
			
			// Step4: 硬限制在40~95度范围内
			if (amp_L < 40) amp_L = 40;
			if (amp_L > 95) amp_L = 95;
			if (amp_R < 40) amp_R = 40;
			if (amp_R > 95) amp_R = 95;
			
			// Step5: 转换为编码器单位
			const int16_t amp_L_encoder = (amp_L * 1138) / 100;
			const int16_t amp_R_encoder = (amp_R * 1138) / 100;
			
			// ============ 频率控制算法（前后差速俯仰）============
			// Step1: 左摇杆Y控制整体频率 (5~15Hz)
			int16_t base_freq = (int16_t)elrs_data.Throttle;
			if (base_freq < 5) base_freq = 5;
			if (base_freq > 15) base_freq = 15;
			
			// Step2: 左摇杆X控制前后频率差 (-2~+2Hz)
			// Yaw: -100(left/down) ~ 0 ~ +100(right/up)
			int16_t freq_diff = (elrs_data.Yaw * 2) / 100;
			
			// Step3: 计算前后翼频率
			int16_t freq_front = base_freq + freq_diff;  // 前翼频率
			int16_t freq_rear = base_freq - freq_diff;   // 后翼频率
			
			// Step4: 硬限制在3~17Hz范围内
			if (freq_front < 3) freq_front = 3;
			if (freq_front > 17) freq_front = 17;
			if (freq_rear < 3) freq_rear = 3;
			if (freq_rear > 17) freq_rear = 17;
			
			// ============ 前后翼独立状态机 ============
			// 前翼状态机
			static uint8_t  sm_idx_front = 0;
			static int8_t   sm_dir_front = 1;
			static uint32_t sm_next_tick_front = 0;
			
			// 后翼状态机
			static uint8_t  sm_idx_rear = 0;
			static int8_t   sm_dir_rear = 1;
			static uint32_t sm_next_tick_rear = 0;
			
			// 计算前后翼的步进时间
			const uint32_t STEPS = 18U;
			uint32_t step_ms_front = (5000U + (STEPS*freq_front/2U)) / (STEPS * freq_front);
			uint32_t step_ms_rear = (5000U + (STEPS*freq_rear/2U)) / (STEPS * freq_rear);
			if (step_ms_front == 0) step_ms_front = 1;
			if (step_ms_rear == 0) step_ms_rear = 1;
			
			uint32_t tick = HAL_GetTick();
			
			// ====== 前翼状态机推进 ======
			if ((int32_t)(tick - sm_next_tick_front) >= 0)
			{
				int16_t c_front = COS_Q15_9[sm_idx_front];
				
				// 前翼目标角度（使用方向系数自动适应）
        Wings_Data.Wings_motor[0].Target_Angle = (int16_t)(base_LF + motor_LF_direction * q15_mul(amp_L_encoder, c_front));  // 左前
        Wings_Data.Wings_motor[1].Target_Angle = (int16_t)(base_RF + motor_RF_direction * q15_mul(amp_R_encoder, c_front));  // 右前
				
				// 安排下一次步进
				sm_next_tick_front += step_ms_front;
				
				// 更新索引与方向
				if (sm_dir_front > 0) {
					if (++sm_idx_front >= 8) { sm_idx_front = 8; sm_dir_front = -1; }
				} else {
					if (sm_idx_front-- == 0) { sm_idx_front = 0; sm_dir_front = +1; }
				}
			}
			
			// ====== 后翼状态机推进 ======
			if ((int32_t)(tick - sm_next_tick_rear) >= 0)
			{
				// 后翼考虑相位差
				int8_t rear_idx;
				if (sm_dir_rear > 0) {
					rear_idx = (int8_t)(sm_idx_rear - phase_offset);
					if (rear_idx < 0) rear_idx = 0;
				} else {
					rear_idx = (int8_t)(sm_idx_rear + phase_offset);
					if (rear_idx > 8) rear_idx = 8;
				}
				int16_t c_rear = COS_Q15_9[rear_idx];
				
				// 后翼目标角度（使用方向系数自动适应）
        Wings_Data.Wings_motor[2].Target_Angle = (int16_t)(base_LR + motor_LR_direction * q15_mul(amp_L_encoder, c_rear));  // 左后
        Wings_Data.Wings_motor[3].Target_Angle = (int16_t)(base_RR + motor_RR_direction * q15_mul(amp_R_encoder, c_rear));  // 右后
				
				// 安排下一次步进
				sm_next_tick_rear += step_ms_rear;
				
				// 更新索引与方向
				if (sm_dir_rear > 0) {
					if (++sm_idx_rear >= 8) { sm_idx_rear = 8; sm_dir_rear = -1; }
				} else {
					if (sm_idx_rear-- == 0) { sm_idx_rear = 0; sm_dir_rear = +1; }
				}
			}
			
			// 更新编码器角度
			StarAndGetResult();
			
			Motor_PID_Control();
			}
			}
			      
			      // ======== Mode 1: 静态立翅模式 ========
			     else if (elrs_data.Mode == 1)
		{
			motor_1_pid.Kp = 10;
			motor_2_pid.Kp = 10;
			motor_3_pid.Kp = 10;
			motor_4_pid.Kp = 10;
			
			// 基准角 (可以通过遥控器调整角度)
			// 使用立翅基准点（4个电机各自使用自己的standing基准点）
			const int16_t target_LF = motor_LF_standing + elrs_data.midpoint;  // 左前翼目标
			const int16_t target_RF = motor_RF_standing + elrs_data.midpoint;  // 右前翼目标
			const int16_t target_LR = motor_LR_standing + elrs_data.midpoint;  // 左后翼目标
			const int16_t target_RR = motor_RR_standing + elrs_data.midpoint;  // 右后翼目标
			
			// 从当前值缓慢移动到目标值
			static uint32_t last_smooth_time = 0;
			const uint32_t SMOOTH_INTERVAL = 5; // 平滑间隔 5ms
			const int16_t MAX_STEP = 70;        // 最大步进值
			
			if ((int32_t)(now - last_smooth_time) >= SMOOTH_INTERVAL)
			{
				// 左前翼平滑移动
				int16_t current_LF = Wings_Data.Wings_motor[0].Corrective_Angle;
				if (current_LF < target_LF) {
					current_LF += MIN(MAX_STEP, target_LF - current_LF);
				} else if (current_LF > target_LF) {
					current_LF -= MIN(MAX_STEP, current_LF - target_LF);
				}
				Wings_Data.Wings_motor[0].Target_Angle = current_LF;
				
				// 右前翼平滑移动
				int16_t current_RF = Wings_Data.Wings_motor[1].Corrective_Angle;
				if (current_RF < target_RF) {
					current_RF += MIN(MAX_STEP, target_RF - current_RF);
				} else if (current_RF > target_RF) {
					current_RF -= MIN(MAX_STEP, current_RF - target_RF);
				}
				Wings_Data.Wings_motor[1].Target_Angle = current_RF;
				
				// 左后翼平滑移动
				int16_t current_LR = Wings_Data.Wings_motor[2].Corrective_Angle;
				if (current_LR < target_LR) {
					current_LR += MIN(MAX_STEP, target_LR - current_LR);
				} else if (current_LR > target_LR) {
					current_LR -= MIN(MAX_STEP, current_LR - target_LR);
				}
				Wings_Data.Wings_motor[2].Target_Angle = current_LR;
				
				// 右后翼平滑移动
				int16_t current_RR = Wings_Data.Wings_motor[3].Corrective_Angle;
				if (current_RR < target_RR) {
					current_RR += MIN(MAX_STEP, target_RR - current_RR);
				} else if (current_RR > target_RR) {
					current_RR -= MIN(MAX_STEP, current_RR - target_RR);
				}
				Wings_Data.Wings_motor[3].Target_Angle = current_RR;
				
				last_smooth_time = now;
			}
		
		StarAndGetResult();
		Motor_PID_Control();
		}
		
        // ======== Mode 0: 收翅模式 ========
        else
		{
			motor_1_pid.Kp = 12;
			motor_2_pid.Kp = 12;
			motor_3_pid.Kp = 12;
			motor_4_pid.Kp = 12;
			
			// 目标角度 (收翅位置，4个电机各自使用自己的folded基准点)
			const int16_t target_LF = motor_LF_folded;  // 左前翼收翅目标
			const int16_t target_RF = motor_RF_folded;  // 右前翼收翅目标
			const int16_t target_LR = motor_LR_folded;  // 左后翼收翅目标
			const int16_t target_RR = motor_RR_folded;  // 右后翼收翅目标

			// 从当前值缓慢移动到目标值
			static uint32_t last_smooth_time_mode0 = 0;
			const uint32_t SMOOTH_INTERVAL = 10; // 平滑间隔10ms
			const int16_t MAX_STEP = 70;         // 最大步进值
			
			if ((int32_t)(now - last_smooth_time_mode0) >= SMOOTH_INTERVAL)
			{
				// 左前翼平滑移动
				int16_t current_LF = Wings_Data.Wings_motor[0].Corrective_Angle;
				if (current_LF < target_LF) {
					current_LF += MIN(MAX_STEP, target_LF - current_LF);
				} else if (current_LF > target_LF) {
					current_LF -= MIN(MAX_STEP, current_LF - target_LF);
				}
				Wings_Data.Wings_motor[0].Target_Angle = current_LF;
				
				// 右前翼平滑移动
				int16_t current_RF = Wings_Data.Wings_motor[1].Corrective_Angle;
				if (current_RF < target_RF) {
					current_RF += MIN(MAX_STEP, target_RF - current_RF);
				} else if (current_RF > target_RF) {
					current_RF -= MIN(MAX_STEP, current_RF - target_RF);
				}
				Wings_Data.Wings_motor[1].Target_Angle = current_RF;

				// 左后翼平滑移动
				int16_t current_LR = Wings_Data.Wings_motor[2].Corrective_Angle;
				if (current_LR < target_LR) {
					current_LR += MIN(MAX_STEP, target_LR - current_LR);
				} else if (current_LR > target_LR) {
					current_LR -= MIN(MAX_STEP, current_LR - target_LR);
				}
				Wings_Data.Wings_motor[2].Target_Angle = current_LR;
				
				// 右后翼平滑移动
				int16_t current_RR = Wings_Data.Wings_motor[3].Corrective_Angle;
				if (current_RR < target_RR) {
					current_RR += MIN(MAX_STEP, target_RR - current_RR);
				} else if (current_RR > target_RR) {
					current_RR -= MIN(MAX_STEP, current_RR - target_RR);
				}
				Wings_Data.Wings_motor[3].Target_Angle = current_RR;
				
				last_smooth_time_mode0 = now;
			}
			
			// 动态调整PID增益（根据左前和左后的距离调整）
			if(abs16_fast(target_LF - Wings_Data.Wings_motor[0].Corrective_Angle) > 200 &&
			   abs16_fast(target_LR - Wings_Data.Wings_motor[2].Corrective_Angle) > 200)
			{
				// 前翼组(motor_1,motor_3)的Kp根据前后距离比例调整
				motor_1_pid.Kp = 12 * (float)abs16_fast(target_LF - Wings_Data.Wings_motor[0].Corrective_Angle) / 
				                      (float)abs16_fast(target_LR - Wings_Data.Wings_motor[2].Corrective_Angle);
				motor_3_pid.Kp = motor_1_pid.Kp;  // motor_3是右前，也是前翼
				
				// 后翼组(motor_2,motor_4)的Kp根据后前距离比例调整
				motor_2_pid.Kp = 12 * (float)abs16_fast(target_LR - Wings_Data.Wings_motor[2].Corrective_Angle) / 
				                      (float)abs16_fast(target_LF - Wings_Data.Wings_motor[0].Corrective_Angle);	
				motor_4_pid.Kp = motor_2_pid.Kp;  // motor_4是右后，也是后翼
			}
			
			StarAndGetResult();
			Motor_PID_Control();
		}
    }
    else
    {
        // 关闭开关，失能所有电机
        motor_disable();
    }
    
    // 离开Mode2时，重置扫翅状态
    if (elrs_data.Mode != 2)
    {
        mode2_flapping = 0;
        last_arm_state = 0;
    }
  }

  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSIDiv = RCC_HSI_DIV1;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = RCC_PLLM_DIV1;
  RCC_OscInitStruct.PLL.PLLN = 8;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = RCC_PLLQ_DIV4;
  RCC_OscInitStruct.PLL.PLLR = RCC_PLLR_DIV2;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */
void HAL_UARTEx_RxEventCallback(UART_HandleTypeDef *huart, uint16_t Size)
{
	if(huart == &huart1)
	{
		ELRS_UARTE_RxCallback(Size);
	}
}

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
