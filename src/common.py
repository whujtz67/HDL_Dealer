import os
import argparse

class ArgParser:
	def __init__(self):
		self.expect_top   = None # Name of expected top module
		self.file		  = None
		self.filelist	  = None
		self.out_dir	  = os.path.abspath("./tb")
		self.clk_period   = 5
		self.tbtop_name   = "tb_top"
		self.ign_pat_file = None
		self.nodpi		  = False
		self.verbose	  = False
		self.custom_code  = None 
		self.core_num     = None


	def arg_parser(self):
		parser = argparse.ArgumentParser(description='A script used for handling HDL Files.')
		parser.add_argument('--top', '-t', dest="top", type=str, help='expected top module name')
		parser.add_argument('--file', '-f', dest="file", type=str, help='input verilog file')
		parser.add_argument('--filelist', '-fl', dest="filelist", type=str, help='input verilog filelist')
		# parser.add_argument('--ast', '-a', dest="ast", type=str, help='ast json file')
		parser.add_argument('--dir', '-d', dest="dir", type=str, help='output dir')
		parser.add_argument('--period', '-p', dest="period", type=int, help='clock period')
		parser.add_argument('--tbtop', dest="tbtop", type=str, help='testbench top level name')
		parser.add_argument('--ign_pat_file', '-ipat', dest="ign_pat_file", type=str, help='signal patterns (a pattern file) indicated which signal should be ignore while generate port interface functions')
		parser.add_argument('--nodpi', '-nd', dest="nodpi", action='store_true', help='whether generate DPI-C port interface functions or not')
		parser.add_argument('--verbose', '-v', dest="verbose", action='store_true', help='verbose')
		parser.add_argument('--custom-code', '-cc', dest="custom_code", type=str, help='input custom code file, will be inserted in somewhere of the testbench')
		parser.add_argument('--core', '-c', dest="core", type=str, help='core number')
		args = parser.parse_args()


		self.expect_top   = args.top
		self.file		  = args.file
		if args.filelist != None:
			self.filelist = os.path.abspath(args.filelist)
		if args.dir != None:
			self.out_dir  = os.path.abspath(args.dir)
		self.clk_period   = args.period  or self.clk_period
		self.tbtop_name   = args.tbtop   or self.tbtop_name
		self.ign_pat_file = args.ign_pat_file
		self.nodpi		  = args.nodpi   or self.nodpi
		self.verbose	  = args.verbose or self.verbose
		self.custom_code  = args.custom_code
		self.core_num     = int(args.core)
		
		# check arg correctness
		self.check()
			
	# to avoid bug
	def check(self):
		# assertions
		assert self.expect_top != None, "top module name is not specified!"
		assert self.file != None or self.filelist != None, "you should use <-f> to point out the design file or use <-fl> to point out filelist"
		assert not (self.file != None and self.filelist != None), "you should not use a specific file and a filelist at the same time"
		if  self.file != None:
			assert os.path.isfile(self.file), f"input verilog file is not exist ==> {self.file}"
				
		if not os.path.exists(self.out_dir):
			os.makedirs(self.out_dir)

		

# Deal with files and filelists
class FileHelper:
	def __init__(self, verbose = True):
		self.verbose = verbose

	def info_print(self, str = "", name = "[File Helper]\t"):
		if self.verbose:
			print(f"{name}{str}")

	# filelist parser
	def parse_filelist(self, filelist_path):
		include_dirs = []
		source_files = []
		filelist     = []
		
		with open(filelist_path, 'r') as file:
			for line in file:
				line = line.strip()
				if line.startswith('+incdir+'):
					include_dir = line[len('+incdir+'):]
					include_dirs.append(include_dir)
					for root, _, files in os.walk(include_dir):
						for name in files:
							filelist.append(os.path.join(root, name))
				else:
					source_files.append(line)
					filelist.append(os.path.abspath(line))

		if self.verbose:
			self.print_filelist_info(include_dirs, source_files, filelist)
		
		return filelist
	
	# print filelist info
	def print_filelist_info(self, include_dirs, source_files, filelist):
		self.info_print("Include directories:")
		for dir in include_dirs:
			self.info_print(dir)
		
		print("\n")
		self.info_print("Source files:")
		for file in source_files:
			self.info_print(file)

		print("\n")
		self.info_print("FileList:")
		for file in filelist:
		    self.info_print(file)



