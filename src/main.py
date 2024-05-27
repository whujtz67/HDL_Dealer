from common import *
from tb_generator import TBGenerator
from rtl_info import *
import pyslang

# ===================
# Top Function
# ===================
def HDL_Dealer_top():
    # parse Arguments
    args        = ArgParser()
    args.arg_parser()

    # parse design file
    all_infos = ALLInfo(args)
    
    
    

    # ----------------------
    # All Functions
    # ----------------------
    tb_generator = TBGenerator(args, all_infos)
    tb_generator.tb_gen_top()




if __name__ == '__main__':
    HDL_Dealer_top()