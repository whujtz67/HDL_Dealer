from common import ArgParser
from enum import Enum
from rtl_info import ALLInfo

# Comment Type
class CmtType(Enum):
	ORDINARY = 0
	CHAPTER  = 1
	HEAD   = 2

class MacroInfo:
	def __init__(self, macro, body, incl_guard_macro = None, multi_line = False, cmt = None) -> None:
		self.macro    = macro            # macro name 
		self.body     = body
		self.ig_macro = incl_guard_macro # ig: include guard
		self.need_ig  = (incl_guard_macro != None)
		self.mul_line = multi_line       # have multiple lines or not
		self.cmt      = cmt
		self.have_cmt = (cmt != None)


class TextHelper:
	def __init__(self, args:ArgParser) -> None:
		self.args	  = args


		# TODO：A list or dictionary is needed to indicate whether all files 
		#	   that have appeared have been written to, to prevent them from being overwritten.
		self.def_file  = f"{self.args.out_dir}/auto_gen_tb.sv" # default file
		self.w_file	= open(self.def_file, "w")

		self.cmt	  = "// "
		self.chpt_cmt = "-" * 50
		self.head_cmt = "=" * 50


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
	
	# insert content in file
	def insert_content(self, filename, line_number, content):
		assert content is not None
		# Open the file in read and write mode
		with open(filename, 'r+') as file:
			# Move the file pointer to the beginning of the specified line
			for _ in range(line_number - 1):
				file.readline()
			# Record the current position of the file pointer
			pos = file.tell()
			# Read the rest of the file
			rest_of_file = file.read()
			# Move the file pointer back to the specified position
			file.seek(pos)
			# Write the content to be inserted
			file.write(content + '\n')
			# Write the rest of the file
			file.write(rest_of_file)

	# Generate Macros, especially multi_line macros
	def write_macro(self, mcr_info: MacroInfo):
		## need include guard
		if mcr_info.have_cmt:
			self.write_comment(mcr_info.cmt, level = CmtType.CHAPTER)
		if mcr_info.need_ig:
			self.write_file(f"`ifndef {mcr_info.ig_macro}", \
				  		    f"`define {mcr_info.ig_macro}\n", sep="\n")
			
		### multiple line defines, need "\" at the end of the line
		if mcr_info.mul_line:
			self.write_file(f"`define {mcr_info.macro}", *mcr_info.body, "\\\n", sep="\t\\\n")
		else:
			self.write_file(f"`define {mcr_info.macro:<20}{mcr_info.body}")
		
		if mcr_info.need_ig:
			self.write_file(f"`endif\t// {mcr_info.ig_macro}\n")
		

	def gen_intf_conn(self):
		self.write_file("`ifndef GUARD_VIP_WRAPPER_CONN", \
				  		"`define GUARD_VIP_WRAPPER_CONN\n", \
				        "`define GeneratedVIPInterconnectSvWrapperConnections\\", sep="\n")
		for i in range(0, self.args.core_num):
			self.write_file( \
f"""/* Generated Core #{i}: CHI RN-F Link*/ \\
	assign chi_if.ic_rn_if  [{i}].RXSACTIVE                     = cpl2_if.chi_if   [{i}].TXSACTIVE;          \\
	assign chi_if.rn_if     [{i}].TXSACTIVE                     = chi_if.ic_rn_if  [{i}].RXSACTIVE;          \\
	assign cpl2_if.chi_if   [{i}].RXSACTIVE                     = chi_if.ic_rn_if  [{i}].TXSACTIVE;          \\
	assign chi_if.rn_if     [{i}].RXSACTIVE                     = chi_if.ic_rn_if  [{i}].TXSACTIVE;          \\
 \\
	assign chi_if.ic_rn_if  [{i}].RXLINKACTIVEREQ               = cpl2_if.chi_if   [{i}].TXLINKACTIVEREQ;    \\
	assign chi_if.rn_if     [{i}].TXLINKACTIVEREQ               = chi_if.ic_rn_if  [{i}].RXLINKACTIVEREQ;    \\
	assign cpl2_if.chi_if   [{i}].TXLINKACTIVEACK               = chi_if.ic_rn_if  [{i}].RXLINKACTIVEACK;    \\
	assign chi_if.rn_if     [{i}].TXLINKACTIVEACK               = chi_if.ic_rn_if  [{i}].RXLINKACTIVEACK;    \\
	assign chi_if.ic_rn_if  [{i}].TXLINKACTIVEACK               = cpl2_if.chi_if   [{i}].RXLINKACTIVEACK;    \\
	assign chi_if.rn_if     [{i}].RXLINKACTIVEACK               = chi_if.ic_rn_if  [{i}].TXLINKACTIVEACK;    \\
	assign cpl2_if.chi_if   [{i}].RXLINKACTIVEREQ               = chi_if.ic_rn_if  [{i}].TXLINKACTIVEREQ;    \\
	assign chi_if.rn_if     [{i}].RXLINKACTIVEREQ               = chi_if.ic_rn_if  [{i}].TXLINKACTIVEREQ;    \\
 \\
	assign chi_if.ic_rn_if  [{i}].RXREQFLITPEND                 = cpl2_if.chi_if   [{i}].TXREQFLITPEND;      \\
	assign chi_if.rn_if     [{i}].TXREQFLITPEND                 = chi_if.ic_rn_if  [{i}].RXREQFLITPEND;      \\
	assign chi_if.ic_rn_if  [{i}].RXREQFLITV                    = cpl2_if.chi_if   [{i}].TXREQFLITV;         \\
	assign chi_if.rn_if     [{i}].TXREQFLITV                    = chi_if.ic_rn_if  [{i}].RXREQFLITV;         \\
	assign chi_if.ic_rn_if  [{i}].RXREQFLIT                     = cpl2_if.chi_if   [{i}].TXREQFLIT;          \\
	assign chi_if.rn_if     [{i}].TXREQFLIT                     = chi_if.ic_rn_if  [{i}].RXREQFLIT;          \\
	assign cpl2_if.chi_if   [{i}].TXREQLCRDV                    = chi_if.ic_rn_if  [{i}].RXREQLCRDV;         \\
	assign chi_if.rn_if     [{i}].TXREQLCRDV                    = chi_if.ic_rn_if  [{i}].RXREQLCRDV;         \\
 \\
	assign chi_if.ic_rn_if  [{i}].RXRSPFLITPEND                 = cpl2_if.chi_if   [{i}].TXRSPFLITPEND;      \\
	assign chi_if.rn_if     [{i}].TXRSPFLITPEND                 = chi_if.ic_rn_if  [{i}].RXRSPFLITPEND;      \\
	assign chi_if.ic_rn_if  [{i}].RXRSPFLITV                    = cpl2_if.chi_if   [{i}].TXRSPFLITV;         \\
	assign chi_if.rn_if     [{i}].TXRSPFLITV                    = chi_if.ic_rn_if  [{i}].RXRSPFLITV;         \\
	assign chi_if.ic_rn_if  [{i}].RXRSPFLIT                     = cpl2_if.chi_if   [{i}].TXRSPFLIT;          \\
	assign chi_if.rn_if     [{i}].TXRSPFLIT                     = chi_if.ic_rn_if  [{i}].RXRSPFLIT;          \\
	assign cpl2_if.chi_if   [{i}].TXRSPLCRDV                    = chi_if.ic_rn_if  [{i}].RXRSPLCRDV;         \\
	assign chi_if.rn_if     [{i}].TXRSPLCRDV                    = chi_if.ic_rn_if  [{i}].RXRSPLCRDV;         \\
 \\
	assign chi_if.ic_rn_if  [{i}].RXDATFLITPEND                 = cpl2_if.chi_if   [{i}].TXDATFLITPEND;      \\
	assign chi_if.rn_if     [{i}].TXDATFLITPEND                 = chi_if.ic_rn_if  [{i}].RXDATFLITPEND;      \\
	assign chi_if.ic_rn_if  [{i}].RXDATFLITV                    = cpl2_if.chi_if   [{i}].TXDATFLITV;         \\
	assign chi_if.rn_if     [{i}].TXDATFLITV                    = chi_if.ic_rn_if  [{i}].RXDATFLITV;         \\
	assign chi_if.ic_rn_if  [{i}].RXDATFLIT                     = cpl2_if.chi_if   [{i}].TXDATFLIT;          \\
	assign chi_if.rn_if     [{i}].TXDATFLIT                     = chi_if.ic_rn_if  [{i}].RXDATFLIT;          \\
	assign cpl2_if.chi_if   [{i}].TXDATLCRDV                    = chi_if.ic_rn_if  [{i}].RXDATLCRDV;         \\
	assign chi_if.rn_if     [{i}].TXDATLCRDV                    = chi_if.ic_rn_if  [{i}].RXDATLCRDV;         \\
 \\
	assign cpl2_if.chi_if   [{i}].RXRSPFLITPEND                 = chi_if.ic_rn_if  [{i}].TXRSPFLITPEND;      \\
	assign chi_if.rn_if     [{i}].RXRSPFLITPEND                 = chi_if.ic_rn_if  [{i}].TXRSPFLITPEND;      \\
	assign cpl2_if.chi_if   [{i}].RXRSPFLITV                    = chi_if.ic_rn_if  [{i}].TXRSPFLITV;         \\
	assign chi_if.rn_if     [{i}].RXRSPFLITV                    = chi_if.ic_rn_if  [{i}].TXRSPFLITV;         \\
	assign cpl2_if.chi_if   [{i}].RXRSPFLIT                     = chi_if.ic_rn_if  [{i}].TXRSPFLIT;          \\
	assign chi_if.rn_if     [{i}].RXRSPFLIT                     = chi_if.ic_rn_if  [{i}].TXRSPFLIT;          \\
	assign chi_if.ic_rn_if  [{i}].TXRSPLCRDV                    = cpl2_if.chi_if   [{i}].RXRSPLCRDV;         \\
	assign chi_if.rn_if     [{i}].RXRSPLCRDV                    = chi_if.ic_rn_if  [{i}].TXRSPLCRDV;         \\
 \\
	assign cpl2_if.chi_if   [{i}].RXDATFLITPEND                 = chi_if.ic_rn_if  [{i}].TXDATFLITPEND;      \\
	assign chi_if.rn_if     [{i}].RXDATFLITPEND                 = chi_if.ic_rn_if  [{i}].TXDATFLITPEND;      \\
	assign cpl2_if.chi_if   [{i}].RXDATFLITV                    = chi_if.ic_rn_if  [{i}].TXDATFLITV;         \\
	assign chi_if.rn_if     [{i}].RXDATFLITV                    = chi_if.ic_rn_if  [{i}].TXDATFLITV;         \\
	assign cpl2_if.chi_if   [{i}].RXDATFLIT                     = chi_if.ic_rn_if  [{i}].TXDATFLIT;          \\
	assign chi_if.rn_if     [{i}].RXDATFLIT                     = chi_if.ic_rn_if  [{i}].TXDATFLIT;          \\
	assign chi_if.ic_rn_if  [{i}].TXDATLCRDV                    = cpl2_if.chi_if   [{i}].RXDATLCRDV;         \\
	assign chi_if.rn_if     [{i}].RXDATLCRDV                    = chi_if.ic_rn_if  [{i}].TXDATLCRDV;         \\
 \\
	assign cpl2_if.chi_if   [{i}].RXSNPFLITPEND                 = chi_if.ic_rn_if  [{i}].TXSNPFLITPEND;      \\
	assign chi_if.rn_if     [{i}].RXSNPFLITPEND                 = chi_if.ic_rn_if  [{i}].TXSNPFLITPEND;      \\
	assign cpl2_if.chi_if   [{i}].RXSNPFLITV                    = chi_if.ic_rn_if  [{i}].TXSNPFLITV;         \\
	assign chi_if.rn_if     [{i}].RXSNPFLITV                    = chi_if.ic_rn_if  [{i}].TXSNPFLITV;         \\
	assign cpl2_if.chi_if   [{i}].RXSNPFLIT                     = chi_if.ic_rn_if  [{i}].TXSNPFLIT;          \\
	assign chi_if.rn_if     [{i}].RXSNPFLIT                     = chi_if.ic_rn_if  [{i}].TXSNPFLIT;          \\
	assign chi_if.ic_rn_if  [{i}].TXSNPLCRDV                    = cpl2_if.chi_if   [{i}].RXSNPLCRDV;         \\
	assign chi_if.rn_if     [{i}].RXSNPLCRDV                    = chi_if.ic_rn_if  [{i}].TXSNPLCRDV;         \\
\\""")
		self.write_file("`endif\n")




		

		
