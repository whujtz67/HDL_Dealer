from common import ArgParser
from enum import Enum

# Comment Type
class CmtType(Enum):
	ORDINARY = 0
	CHAPTER  = 1
	HEAD   = 2

class TextHelper:
	def __init__(self, args:ArgParser) -> None:
		self.args      = args

		# TODO：A list or dictionary is needed to indicate whether all files 
		#       that have appeared have been written to, to prevent them from being overwritten.
		self.def_file  = f"{self.args.out_dir}/{self.args.tbtop_name}.sv" # default file
		self.w_file    = open(self.def_file, "w")

		self.cmt      = "// "
		self.chpt_cmt = "-" * 50
		self.head_cmt = "=" * 50

		self.macro_def_check = \
"""
`ifdef SIM_VERILATOR
	`ifdef SIM_VCS
	  initial begin
	    $error("Both SIM_VERILATOR and SIM_VCS are defined. Only one should be defined.");
	    $finish;
	  end
	`endif
`else
	`ifndef SIM_VCS
	  initial begin
	    $error("Neither SIM_VERILATOR nor SIM_VCS is defined. One must be defined.");
	    $finish;
	  end
	`endif
`endif
"""

	# TODO: Replace the filelist with a file type that contains key-value pairs.
	# write input "file" or default file (be careful with the sep)
	def write_file(self, *args, file = None, sep = ""):
		# print(*args)
		# NOTE: All files should be closed after finish writing
		if file is not None:
			self.w_file = open(file, "w")
			
		print(*args, file = self.w_file, sep = sep)

	# finish writing
	def close_file(self, file = None):
		close_file = open(self.def_file, "w") if (file is None) else open(file, "w") 
		close_file.close()
	
	# write comment
	def write_comment(self, *args, file = None, level = CmtType.ORDINARY):
		if level == CmtType.ORDINARY:
			new_args = self.add_prefix(*args, prefix = self.cmt)
		elif level == CmtType.CHAPTER:
			new_args = self.add_prefix(self.chpt_cmt, *args, self.chpt_cmt, prefix = self.cmt)
		elif level == CmtType.HEAD:
			new_args = self.add_prefix(self.head_cmt, *args, self.head_cmt, prefix = self.cmt)

		self.write_file(*new_args, file = file, sep = "\n")

	# add prefix for string
	def add_prefix(self, *args, prefix=None):
		assert prefix is not None, "should define prefix"
		new_tuple = tuple(f"{prefix}{arg}" for arg in args)
		return new_tuple

		

		
