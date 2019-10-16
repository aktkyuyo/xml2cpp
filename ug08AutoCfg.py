import xlrd
import re
import os
from xml.dom.minidom import parse
import xml.dom.minidom

# 使用minidom解析器打开 XML 文档
DOMTree = xml.dom.minidom.parse("xlspath.xml")
collection = DOMTree.documentElement
 
# 
xlsdata_path = collection.getElementsByTagName("xlsdata_path")[0].childNodes[0].data
xlsname = collection.getElementsByTagName("xlsname")[0].childNodes[0].data

#################################################################################
#################################################################################
#xlsdata_path = ''
#xlsname = ''

xls_complete_path = xlsdata_path + '\\' + xlsname
print (xls_complete_path)
workbook = xlrd.open_workbook(xls_complete_path)

sheet2 = workbook.sheets()[0] #第一个表
row_2 = sheet2.row_values(1) # 获取第2行内容
name_xml = row_2[0]
path_xml = row_2[1]
start_crow = row_2[2] - 1
start_key_row = start_crow
start_xml_row = start_crow + 2
names_sheet = row_2[3:]
#print(name_xml)
#print (names_sheet)
#################################################################################

#################################################################################
#################class#############
class FuncItem:
	def __init__(self):
		self.index = 'index'
		self.pre_decorate = ''
		self.symbol = ''
		self.name_func = ''
		self.name_get = ''
		self.name_init = ''
		self.name_member = ''
		self.name_class = ''
		self.name_struct = ''
################func##############


def DoNameBy_(string_):
	tmp_list = re.split('_', string_)
	tmp_name = ''
	for v in tmp_list:
		tmp_name += v.capitalize()
	return tmp_name

def GrepValueNameByComma(string_):
	return re.split(',', string_)[0]

def FindIndexByStr(struct_name):
	if struct_name.find('Level') >= 0 or struct_name.find('level') >= 0:
		return 'level'
	elif struct_name.find('Grade') >= 0 or struct_name.find('grade') >= 0:
		return 'grade'
	else:
		return 'index'

def GetFuncItem(func_name, class_name):
	func_item = FuncItem()
	func_item.name_class = class_name
	func_item.name_struct = class_name.replace('Config', '') + func_name
	func_item.name_func = func_name
	func_item.index = FindIndexByStr(func_name);
	func_item.name_init = 'Init' + func_name + '(PugiXmlNode root_element, std::string& err)'
	if func_name  == ('OtherConfig'):
		func_item.pre_decorate = func_item.name_struct + ' '
		func_item.symbol = ' & '
		func_item.name_member = 'm_' + name_cur_sheet + '_cfg'
		func_item.name_get = 'Get' + func_item.name_struct + '() const'
	else:
		func_item.pre_decorate = 'std::vector<' + func_item.name_struct + '> '
		func_item.symbol = ' * '
		func_item.name_member = 'm_' + name_cur_sheet + '_cfg_list'
		func_item.name_get = 'Get' + func_item.name_func + '(int ' + func_item.index + ') const'
	return func_item

def FindCppGetContent(func_item):
	func_content = 'const ' + func_item.name_struct + func_item.symbol +  func_item.name_class + '::' + func_item.name_get
	func_content += '\n{\n'
	if func_item.name_func == ('OtherConfig'):
		func_content += '	return ' + func_item.name_member + ';\n'
	else:
		func_content += '''	if ({0} < 0 || {0} >= GetStlArrayLen({1})'''.format(func_item.index, func_item.name_member)
		func_content += '\n	{\n' + '		return nullptr;\n' + "	}\n\n" 
		func_content +=	'	auto &cfg = ' + func_item.name_member + '[' + func_item.index + '];\n'
		func_content += '''	if (cfg.{0} != {0})'''.format(func_item.index);
		func_content += '\n	{\n' + '		return nullptr;\n' + "	}\n\n"
		func_content += '	return &cfg;\n'
	func_content += "}\n\n"
	return func_content;

def DoCppInitPre(func_item):
	func_content = 'bool ' + func_item.name_class + '::' + func_item.name_init + '\n{'

	func_content += '''
	PugiXmlNode data_element = root_element.child("data");
	if (data_element.empty())
	{
		return false;
	}

	while (!data_element.empty())
	{
	'''

	if func_item.name_func == ('OtherConfig'):
		func_content += '	' + func_item.name_struct + ' &cfg = ' + func_item.name_member + ';\n'
	else:
		func_content += '	' + func_item.name_struct + ' cfg;\n'
	return func_content
#################################################################################

#################################################################################
pre_class_name = DoNameBy_(name_xml)
pre_class_name = pre_class_name.replace('Cfg', '').replace('cfg', '').replace('Config', '').replace('config', '')
#print(pre_class_name)

#类名
pos_name = "Config"
class_name = pre_class_name + pos_name
file_name = class_name.lower()
#print(file_name)
#################################################################################


counts_sheet= len(workbook.sheets())
counts_xml_names = len(names_sheet)
counts_xml_name = 0
#print (names_sheet)
#print (counts_sheet)
#print (counts_xml_names)
#################################################################################

#################################################################################
#################file
const = 'const'
file_struct_list = ''
file_class = "class " + class_name + "\n{\n" + 'public:\n'
file_hpp_func_get = '	bool Init(const std::string &path, std::string &err);\n\n'
file_hpp_func_init = ''
file_hpp_func_mem = ''
file_cpp_func_load = ''
file_cpp_func_get = ''
file_cpp_func_init = ''
##
file_cpp_func_load = '''bool {0}::Init(const std::string &path, std::string &err)
{1}
	PRE_LOAD_CONFIG_AUTO("{2}");

'''.format(class_name, '{', name_xml)
#################################################################################

#################################################################################
##########################start##################################################
#################################################################################
for index in range(1, counts_sheet):
	++counts_xml_name;
	#print (counts_sheet)
	if counts_xml_name > counts_xml_names: 
		break
		
	#print (counts_xml_name)
	sheet_tmp = workbook.sheets()[index]
	name_cur_st = sheet_tmp.name
	name_cur_sheet = GrepValueNameByComma(names_sheet[index - 1])
	names_tag = 0
	
	#print (name_cur_st)
	#print (name_cur_sheet)
	#print (name_cur_st)
	#################################################################################
	#结构名
	func_name = DoNameBy_(name_cur_sheet) + pos_name
	
	#################################################################################
	rows_cs_name = sheet_tmp.row_values(int(start_crow))
	rows_func_name = sheet_tmp.row_values(int(start_xml_row))
	rows_key = sheet_tmp.row_values(int(start_key_row))
	#cols = sheet2.col_values(1,1) # 获取第二列内容
	
	#################################################################################
	func_item = GetFuncItem(func_name, class_name)
	
	#################################################################################
	file_cpp_func_init_single = DoCppInitPre(func_item)
	file_struct_single = ''
	find_count = 0;
	#一个表一个分页的所有变量
	for index  in range(0, len(rows_cs_name)):
		value_cs = rows_cs_name[index][0:2]
		value_flag = rows_key[index]
		value_name = rows_func_name[index]
		if value_cs.find("s") < 0 or len(value_name) <= 0:
			continue
		
		find_count += 1
		value_name = GrepValueNameByComma(value_name)
		
		####main to cpp init
		if value_flag.find('item_list') >= 0:
			file_cpp_func_init_single += '''		if (!ReadItemListConfig(data_element, "{0}", cfg.{0}))'''.format(value_name)
			file_struct_single += '	std::vector<ItemConfigData> ' + value_name + "_list;\n"

		elif value_flag.find('item_id') >= 0:
			file_cpp_func_init_single += '''		if (!GetSubNodeValue(data_element, "{0}", !ITEMPOOL->GetItem(cfg.{0}))'''.format(value_name)
		elif value_flag.find('item') >= 0:
			file_cpp_func_init_single += '''		if (!ReadItemConfig(data_element, "{0}", cfg.{0});'''.format(value_name)
			file_struct_single += '	ItemConfigData ' + value_name + ";\n"

		else:
			file_cpp_func_init_single += '''		if (!GetSubNodeValue(data_element, "{0}", cfg.{0}) || cfg.{0} < 0)'''.format(value_name)
			file_struct_single += '	int ' + value_name + " = 0;\n"
		
		###main 
		file_cpp_func_init_single += '\n' + '		{\n'
		file_cpp_func_init_single += '''			err = "load [{0}] err -> " + std::to_string(cfg.{0});\n'''.format(value_name)
		file_cpp_func_init_single += '			return false;'
		file_cpp_func_init_single += '\n' + '		}\n\n'

	if find_count <= 0:
		continue
	
	#################################################################################
	#####to hpp struct
	file_struct_list += "struct " + func_item.name_struct + "\n{\n";
	file_struct_list += file_struct_single + "};\n" + '\n';
	#print (file_struct_single)
	###################################hpp##############################################
	######to hpp get
	file_hpp_func_get += '	const ' + func_item.name_struct + func_item.symbol + func_item.name_get + ';\n'
	#####to hpp init
	file_hpp_func_init += '	bool ' + func_item.name_init + ';\n' + '\n'
	#####to hpp name_member
	file_hpp_func_mem += '	' + func_item.pre_decorate + func_item.name_member + ';\n';

	####################################cpp#############################################
	###to cpp load
	file_cpp_func_load += '''	LOAD_CONFIG_AUTO("{0}", Init{1});'''.format(name_cur_sheet, func_item.name_func) + '\n';
	#################################################################################
	###to cpp get
	file_cpp_func_get += FindCppGetContent(func_item);
	#################################################################################
	###to do cpp init
	if func_item.name_func == ('OtherConfig'):
		file_cpp_func_init_single += '\n'
	else:
		file_cpp_func_init_single += '		' + func_item.name_member +'.emplace_back(cfg);\n'
	file_cpp_func_init_single += '		data_element = data_element.next_sibling();\n'
	file_cpp_func_init_single += '	}\n\n'
	file_cpp_func_init_single += '	return true;\n'
	file_cpp_func_init += file_cpp_func_init_single + '}\n\n'
	#################################################################################
	#print ('##########################')
	#print (cols)
####do end
#print (file_cpp_func_get)
file_cpp_func_load += "	return true;\n}\n\n"
#################################################################################
##########################end####################################################
#################################################################################

#################################################################################
#########################write###################################################
#################################################################################
dir = os.path.dirname(os.path.realpath(__file__))
cfg_dir = dir + "\\"

##hpp
file_hpp = open(cfg_dir + file_name + ".hpp", "w+")
head_hpp = '''#ifndef __{0}_HPP__
#define __{0}_HPP__

#include "servercommon/configcommon.h"
#include "servercommon/struct/itemlistparam.h"
#include <vector>
#include "common/pugixml/pugixmluser.hpp"

'''.format(name_xml.upper())

file_hpp.write(head_hpp)
file_hpp.write(file_struct_list)

file_hpp.write(file_class)
file_hpp.write(file_hpp_func_get)
file_hpp.write('\nprivate:\n')
file_hpp.write(file_hpp_func_init)
file_hpp.write('\n')
file_hpp.write(file_hpp_func_mem)
file_hpp.write('};\n')
file_hpp.write('\n#endif')
file_hpp.close()
##hpp
#################################################################################
##cpp
file_cpp = open(cfg_dir + file_name + ".cpp", "w+")
head_cpp = '''#include "{0}.hpp"
#include "servercommon/configcommon.h"
#include "item/itempool.h"

{1}::{1}() 
{2}
{3}

{1}::~{1}()
{2}
{3}

'''.format(file_name, class_name, '{', '}')

file_cpp.write(head_cpp)
file_cpp.write(file_cpp_func_load)
file_cpp.write(file_cpp_func_get)
file_cpp.write(file_cpp_func_init)
file_cpp.close()
##cpp
#################################################################################

#print(head_cpp)
#print (file_struct_list)
#print (file_hpp_func_get)
#print (file_hpp_func_init)
#print (file_hpp_func_mem)
#print (file_cpp_func_load)

print('succ')
os.system("pause")