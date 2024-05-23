# to analyse all infos of the RTL code
import pyslang
import fnmatch
from common import FileHelper
from common import ArgParser

CLOCK_PATTERNS = ["clock", "clock_i", "clk", "clk_i", "enq_clock"]
RESET_PATTERNS = ["reset", "reset_i", "rst", "rst_i", "enq_reset"]

REG_STR  = "reg"
WIRE_STR = "wire"

class PortInfo:
	def __init__(self, name, width, dir, array_size = 0, is_disable=False):
		assert name    != None
		assert width   != None
		assert dir     != None
		self.name       = name
		self.width      = width
		self.array_size = array_size
		self.dir        = dir
		self.is_disable = is_disable

	def is_array(self):
		return self.array_size != 0
	
	def is_input(self):
		return self.dir == "In"

	def is_output(self):
		return self.dir == "Out"
	
	def is_clock(self):
		return self.name in CLOCK_PATTERNS and self.width == 1
	
	def is_reset(self):
		return self.name in RESET_PATTERNS and self.width == 1

	def is_settable(self):
		return self.is_input()

class ALLInfo:
	def __init__(self, args: ArgParser) -> None:
		self.args = args
		# Use to parse filelist
		self.file_helper = FileHelper()
		# parse design file
		self.tree, self.c = self.design_parser()

		# common infomations
		self.top_name  = self.c.getRoot().topInstances[0].name
		self.root      = self.c.getRoot().find(args.expect_top)
		self.port_list = self.root.body.portList

		assert self.top_name == args.expect_top, f"parsed_top_name != expected top name: {self.top_name} != {args.expect_top}"
		assert self.root != None, "root not found!"

		self.ignore_pats = self.get_ignore_pattern()

		self.port_infos = self.port_info_parser()



	def info_print(self, str = "" , prefix = "", name = "RTL Parser"):
		if self.args.verbose:
			print(f"[{name}/{prefix}]\t{str}")
		

	def design_parser(self):
		# ---------------------
		# parse design file
		# ---------------------
		# use file
		c = pyslang.Compilation()
		if self.args.file != None:
			tree = pyslang.SyntaxTree.fromFile(self.args.file)
			c.addSyntaxTree(tree)
		# use filelist
		if self.args.filelist != None:
			filelist = self.file_helper.parse_filelist(self.args.filelist)
			for file in filelist:
				tree = pyslang.SyntaxTree.fromFile(file)
				c.addSyntaxTree(tree)
		return tree, c
	
	def port_info_parser(self):
		ports = []
		port_max_len = 0
		for i, port in enumerate(self.port_list):
			assert port.isAnsiPort
			name       = port.name
			direction  = port.direction.name
			ptype      = port.type.__str__()
			self.info_print(f"[{i}]\tname: {name}\tport_type: {ptype}\tdirection: {direction}", "Port Parser")

			if isinstance(port.type, pyslang.FixedSizeUnpackedArrayType):
				# FixedSizeArray, e.g. logic[31:0]$[0:59] => 60 elements, ecach element has bit width of 32
				# logic [arrayElementType_width]$[fixedRange_width]
				arrayElementType_width = port.type.arrayElementType.getBitVectorRange().width
				fixedRange_width = port.type.fixedRange.width

				width = arrayElementType_width
				array_size = fixedRange_width

				ports.append(PortInfo(name, width, direction, array_size, is_disable))

				self.args.verbose and self.info_print(f"find \033[38;5;208marray port\033[0m({type(port.type).__name__}) => name: {name:<30} type: {ptype:<15} width: {width:<5} array_size: {array_size:<5} direction: {direction:<4} is_disable: {is_disable}", "Port Parser")

				# assert False, f"TODO: [{i}] " + f"name: {name} " + f"ptype: {ptype} " + f"arrayElement_width: {arrayElementType_width} " + f"fixedRange_width: {fixedRange_width}"
			elif isinstance(port.type, pyslang.ScalarType) or isinstance(port.type, pyslang.PackedArrayType):
				width	  = port.type.getBitVectorRange().width
				is_disable = self.check_disable(name)

				if port_max_len < len(name):
					port_max_len = len(name)

				self.args.verbose and self.info_print(f"find port(\033[34m{type(port.type).__name__}\033[0m) => name: {name:<30} type: {ptype:<15} width: {width:<5} direction: {direction:<4} is_disable: {is_disable}", "Port Parser")
				ports.append(PortInfo(name, width, direction, 0, is_disable))
			else:
				assert False, f"Unknown type => {type(port.type)}"

		return ports

	def get_ignore_pattern(self):
		ignore_patterns = []
		if self.args.ign_pat_file != None:
			with open(self.args.ign_pat_file, 'r') as file:
				for i, line in enumerate(file.readlines()):
					print(i, line)
					if fnmatch.fnmatch(line, "//*") or fnmatch.fnmatch(line, '#*'):
						continue
					ignore_patterns.append(line.strip("\n"))
		return ignore_patterns
	
	def check_disable(self, port_name):
		if len(self.ignore_pats) == 0:
			return False
		else:
			for p in self.ignore_pats:
				match = fnmatch.fnmatch(port_name, p)
				if match:
					self.args.verbose and self.info_print(f"disable match => {p} {port_name}", "Port Parser")
					return True
			return False

	
