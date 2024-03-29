#!/usr/bin/python3

# DeviceId
DeviceId_CORE = b'\x00'
DeviceId_BOOTLOADER = b'\x01'
DeviceId_SPHERO = b'\x02'

# CoreCommandId
CoreCommandId_PING = b'\x01'
CoreCommandId_VERSION = b'\x02'
CoreCommandId_CONTROL_UART_TX = b'\x03'
CoreCommandId_SET_BT_NAME = b'\x10'
CoreCommandId_GET_BT_NAME = b'\x11'
CoreCommandId_SET_AUTO_RECONNECT = b'\x12'
CoreCommandId_GET_AUTO_RECONNECT = b'\x13'
CoreCommandId_GET_PWR_STATE = b'\x20'
CoreCommandId_SET_PWR_NOTIFY = b'\x21'
CoreCommandId_SLEEP = b'\x22'
CoreCommandId_GET_POWER_TRIPS = b'\x23'
CoreCommandId_SET_POWER_TRIPS = b'\x24'
CoreCommandId_SET_INACTIVE_TIMER = b'\x25'
CoreCommandId_GOTO_BL = b'\x30'
CoreCommandId_RUN_L1_DIAGS = b'\x40'
CoreCommandId_RUN_L2_DIAGS = b'\x41'
CoreCommandId_CLEAR_COUNTERS = b'\x42'
CoreCommandId_ASSIGN_TIME = b'\x50'
CoreCommandId_POLL_TIMES = b'\x51'

# BootloaderCommandId
BootloaderCommandId_BEGIN_REFLASH = b'\x02'
BootloaderCommandId_HERE_IS_PAGE = b'\x03'
BootloaderCommandId_LEAVE_BOOTLOADER = b'\x04'
BootloaderCommandId_IS_PAGE_BLANK = b'\x05'
BootloaderCommandId_CMD_ERASE_USER_CONFIG = b'\x06'

# SpheroCommandId
SpheroCommandId_SET_CAL = b'\x01'
SpheroCommandId_SET_STABILIZ = b'\x02'
SpheroCommandId_SET_ROTATION_RATE = b'\x03'
SpheroCommandId_SET_CREATION_DATE = b'\x04'
SpheroCommandId_GET_BALL_REG_WEBSITE = b'\x05'
SpheroCommandId_REENABLE_DEMO = b'\x06'
SpheroCommandId_GET_CHASSIS_ID = b'\x07'
SpheroCommandId_SET_CHASSIS_ID = b'\x08'
SpheroCommandId_SELF_LEVEL = b'\x09'
SpheroCommandId_SET_VDL = b'\x0A'
SpheroCommandId_SET_DATA_STREAMING = b'\x11'
SpheroCommandId_SET_COLLISION_DET = b'\x12'
SpheroCommandId_LOCATOR = b'\x13'
SpheroCommandId_SET_ACCELERO = b'\x14'
SpheroCommandId_READ_LOCATOR = b'\x15'
SpheroCommandId_SET_RGB_LED = b'\x20'
SpheroCommandId_SET_BACK_LED = b'\x21'
SpheroCommandId_GET_RGB_LED = b'\x22'
SpheroCommandId_ROLL = b'\x30'
SpheroCommandId_BOOST = b'\x31'
SpheroCommandId_MOVE = b'\x32'
SpheroCommandId_SET_RAW_MOTORS = b'\x33'
SpheroCommandId_SET_MOTION_TO = b'\x34'
SpheroCommandId_SET_OPTIONS_FLAG = b'\x35'
SpheroCommandId_GET_OPTIONS_FLAG = b'\x36'
SpheroCommandId_SET_TEMP_OPTIONS_FLAG = b'\x37'
SpheroCommandId_GET_TEMP_OPTIONS_FLAG = b'\x38'
SpheroCommandId_GET_CONFIG_BLK = b'\x40'
SpheroCommandId_SET_SSB_PARAMS = b'\x41'
SpheroCommandId_SET_DEVICE_MODE = b'\x42'
SpheroCommandId_SET_CFG_BLOCK = b'\x43'
SpheroCommandId_GET_DEVICE_MODE = b'\x44'
SpheroCommandId_GET_SSB = b'\x46'
SpheroCommandId_SET_SSB = b'\x47'
SpheroCommandId_SSB_REFILL = b'\x48'
SpheroCommandId_SSB_BUY = b'\x49'
SpheroCommandId_SSB_USE_CONSUMEABLE = b'\x4A'
SpheroCommandId_SSB_GRANT_CORES = b'\x4B'
SpheroCommandId_SSB_ADD_XP = b'\x4C'
SpheroCommandId_SSB_LEVEL_UP_ATTR = b'\x4D'
SpheroCommandId_GET_PW_SEED = b'\x4E'
SpheroCommandId_SSB_ENABLE_ASYNC = b'\x4F'
SpheroCommandId_RUN_MACRO = b'\x50'
SpheroCommandId_SAVE_TEMP_MACRO = b'\x51'
SpheroCommandId_SAVE_MACRO = b'\x52'
SpheroCommandId_REINIT_MACRO_EXECUTIVE = b'\x54'
SpheroCommandId_ABORT_MACRO = b'\x55'
SpheroCommandId_GET_MACRO_STATUS = b'\x56'
SpheroCommandId_SET_MACRO_PARAMETER = b'\x57'
SpheroCommandId_APPEND_MACRO_CHUNK = b'\x58'
SpheroCommandId_ERASE_ORBBASIC_STORAGE = b'\x60'
SpheroCommandId_APPEND_ORBBASIC_FRAGMENT = b'\x61'
SpheroCommandId_EXECUTE_ORBBASIC_PROGRAM = b'\x62'
SpheroCommandId_ABORT_ORBBASIC_PROGRAM = b'\x63'
SpheroCommandId_SUBMIT_VALUE_TO_INPUT_STATEMENT = b'\x64'
SpheroCommandId_COMMIT_RAM_PROGRAM_TO_FLASH = b'\x65'
