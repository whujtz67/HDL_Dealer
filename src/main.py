from common import *
import pyslang

# ===================
# Top Function
# ===================
def HDL_Dealer_top():
    args        = ArgParser()
    file_helper = FileHelper()
    args.arg_parser()
    
    # ---------------------
    # parse design file
    # ---------------------
    # use file
    c = pyslang.Compilation()
    if args.file != None:
        tree = pyslang.SyntaxTree.fromFile(args.file)
        c.addSyntaxTree(tree)
    # use filelist
    if args.filelist != None:
        filelist = file_helper.parse_filelist(args.filelist)
        for file in filelist:
            tree = pyslang.SyntaxTree.fromFile(file)
            c.addSyntaxTree(tree)



if __name__ == '__main__':
    HDL_Dealer_top()