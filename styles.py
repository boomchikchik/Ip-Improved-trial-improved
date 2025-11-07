from colorama import Fore, Style
RESET = Style.RESET_ALL

# Bright Styles
B_G = RESET + Style.BRIGHT + Fore.GREEN
B_R = RESET + Style.BRIGHT + Fore.RED
B_Y = RESET + Style.BRIGHT + Fore.YELLOW
B_B = RESET + Style.BRIGHT + Fore.BLUE
B_C = RESET + Style.BRIGHT + Fore.CYAN
B_M = RESET + Style.BRIGHT + Fore.MAGENTA
B_W = RESET + Style.BRIGHT + Fore.WHITE

# Dim Styles
D_G = RESET + Style.DIM + Fore.GREEN
D_R = RESET + Style.DIM + Fore.RED
D_Y = RESET + Style.DIM + Fore.YELLOW
D_B = RESET + Style.DIM + Fore.BLUE
D_C = RESET + Style.DIM + Fore.CYAN
D_M = RESET + Style.DIM + Fore.MAGENTA
D_W = RESET + Style.DIM + Fore.WHITE

# Normal Styles
N_G = RESET + Style.NORMAL + Fore.GREEN
N_R = RESET + Style.NORMAL + Fore.RED
N_Y = RESET + Style.NORMAL + Fore.YELLOW
N_B = RESET + Style.NORMAL + Fore.BLUE
N_C = RESET + Style.NORMAL + Fore.CYAN
N_M = RESET + Style.NORMAL + Fore.MAGENTA
N_W = RESET + Style.NORMAL + Fore.WHITE

# Keep old names for backward compatibility (optional)
BRIGHT_GREEN = B_G
BRIGHT_RED = B_R
BRIGHT_YELLOW = B_Y
BRIGHT_BLUE = B_B
BRIGHT_CYAN = B_C
BRIGHT_MAGENTA = B_M
BRIGHT_WHITE = B_W

DIM_GREEN = D_G
DIM_RED = D_R
DIM_YELLOW = D_Y
DIM_BLUE = D_B
DIM_CYAN = D_C
DIM_MAGENTA = D_M
DIM_WHITE = D_W

NORMAL_GREEN = N_G
NORMAL_RED = N_R
NORMAL_YELLOW = N_Y
NORMAL_BLUE = N_B
NORMAL_CYAN = N_C
NORMAL_MAGENTA = N_M
NORMAL_WHITE = N_W