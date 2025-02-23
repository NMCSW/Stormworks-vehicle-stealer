import os
from re import sub
from pymem import Pymem, pymem
from math import floor, cos, sin
from struct import pack, unpack
from shutil import copy, copytree
from settings import VEH, VEH_PATTERN, VEH_DATA_PATTERN, VEH_GROUP_DATA_PATTERN

# Memory functions
def get_process_object(process_name):
    return Pymem(process_name)


def get_process_module(process_name, module_name):
    process_object = get_process_object(process_name)
    return pymem.process.module_from_name(process_object.process_handle, module_name)


def get_base_address(process_module):
    return process_module.lpBaseOfDll


def search_offset_by_pattern(process_object, process_module, base_address, pattern):
    memory = read_bytes_from_address(process_object, process_module.lpBaseOfDll, process_module.SizeOfImage)
    index = memory.find(pattern)
    if index != -1:
        address = process_module.lpBaseOfDll + index
        offset = address - base_address
        return offset
    else:
        raise ValueError("Pattern not found")


def write_bytes_to_address(process_object, address, data):
    process_object.write_bytes(address, data, len(data))


def read_bytes_from_address(process_object, address, size):
    return process_object.read_bytes(address, size)


def check_process(process_name):
    try:
        Pymem(process_name)
        return True
    except:
        return False

# File system functions
def directory_exists(path):
    if not os.path.exists(path):
        return False
    return True


def check_newest_file(path):
    files = [f"{path}\\{_}" for _ in os.listdir(path)]
    ff = []
    for file in files:
        time = os.path.getctime(file)
        ff.append([time, file])
    ff.sort()
    return ff[-1][1]


def create_directory():
    if not directory_exists(f"{os.getenv('APPDATA')}\\xml_stealer"):
        os.makedirs(f"{os.getenv('APPDATA')}\\xml_stealer")


def rewrite_file(content):
    with open(f"{os.getenv('APPDATA')}\\xml_stealer\\xml_stealer.cfg", "a+", encoding="utf-8") as cfg_file:
        cfg_file.truncate(0);cfg_file.seek(0)
        cfg_file.write(content)


def read_file():
    try:
        with open(f"{os.getenv('APPDATA')}\\xml_stealer\\xml_stealer.cfg", "r+", encoding="utf-8") as cfg_file:
            return cfg_file.read()
    except Exception as e:
        print("Read exception", e)
        return ""


def auto_fill_file():
    if read_file() == "":
        rewrite_file(f"{os.getenv('APPDATA')}\\Stormworks\\saves")


def calculate_position(i, x, y, z, r=100, count_in_circle=8):
    angle = 360/count_in_circle
    zo = floor(i/8)
    return floor(x+(cos(i*angle)*r)), floor(y+(sin(i*angle)*r)), z+(zo*30)
    

def patch_save(path):
    vehicle_nums = parse_vehicles(f'{path}\\vehicles')

    veh_pattern = VEH_PATTERN.split("*")
    veh_data_pattern = VEH_DATA_PATTERN.split("*")
    veh_group_data_pattern = VEH_GROUP_DATA_PATTERN.split("*")

    veh_data=""
    veh_group_data=""

    veh = veh_pattern[0]+str(len(vehicle_nums))+veh_pattern[1]+str(len(vehicle_nums))+veh_pattern[2]
    for i in range(len(vehicle_nums)):
        x,y,z = calculate_position(i, 0, 0, 200)
        veh_data = veh_data+'\n'+veh_data_pattern[0]+str(vehicle_nums[i])+veh_data_pattern[1]+str(vehicle_nums[i])+veh_data_pattern[2]+str(x)+veh_data_pattern[3]+str(z)+veh_data_pattern[4]+str(y)+veh_data_pattern[5]
        veh_group_data = veh_group_data+'\n'+veh_group_data_pattern[0]+str(vehicle_nums[i])+veh_group_data_pattern[1]+str(vehicle_nums[i])+veh_group_data_pattern[2]

    veh_data = '\t\t<vehicle_data>'+veh_data+'\n\t\t</vehicle_data>'
    veh_group_data = '\t\t<vehicle_group_data>'+veh_group_data+'\n\t\t</vehicle_group_data>'

    result = veh+'\n'+veh_data+'\n'+veh_group_data+'\n'+'\t</vehicles>'
    os.makedirs(f"{path}\\vehicle_groups")
    for num in vehicle_nums:
        try:
            copy(f"{path}\\vehicles\\{num}.xml.bin", f"{path}\\vehicle_groups\\{num}.xml.bin")
        except Exception as e:
            print('Error while copying vehicle bin: ', e)

    with open(f'{path}\\scene.xml', "a+", encoding="utf-8") as scene:
        scene.seek(0)
        scene_f = scene.read()
        veh_data_f = sub(rf"{VEH}", result, scene_f)
        scene.truncate(0);scene.seek(0)
        scene.write(veh_data_f)


def parse_vehicles(path):
    files = [_ for _ in os.listdir(path)]
    veh_nums = []
    for file in files:
        if not '.bin' in file:
            veh_nums.append(int(file.split("_")[0]))
    veh_nums.sort()
    return veh_nums


# Main functions
def steal_vehicle(process_object, base_address, offset, state):
    if state:
        r_data = read_bytes_from_address(process_object, base_address+offset, 4)
        value = unpack('<I', r_data)[0]
        w_data = pack('<I', value+1)
        write_bytes_to_address(process_object, base_address+offset, w_data)
    else:
        r_data = read_bytes_from_address(process_object, base_address+offset, 4)
        value = unpack('<I', r_data)[0]
        w_data = pack('<I', value-1)
        write_bytes_to_address(process_object, base_address+offset, w_data)


def save_vehicle_from(path):
    path = os.path.normpath(path)
    splited_path = path.split("\\")
    directory = "\\".join(splited_path[:-1])
    c = 0
    while True:
        c += 1
        if not directory_exists(f'{directory}\\new_save_{c}'):
            os.makedirs(f'{directory}\\new_save_{c}')
            files = [_ for _ in os.listdir(path)]
            for file in files:
                if file != 'vehicle_groups':
                    if file.endswith('.bin') or file.endswith('.xml'):
                        copy(f'{path}\\{file}', f'{directory}\\new_save_{c}\\{file}')
                    else:
                        copytree(f'{path}\\{file}', f'{directory}\\new_save_{c}\\{file}')
            print(f"New save: {directory}\\new_save_{c}")
            patch_save(f'{directory}\\new_save_{c}')
            break
    return f'{directory}\\new_save_{c}'

