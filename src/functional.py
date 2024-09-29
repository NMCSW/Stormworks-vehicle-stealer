import pymem, struct
import settings as settings
import os
import math as m
from shutil import copy, copytree
from re import sub


# Memory functions
def get_base_address(module_name):
    process = pymem.Pymem(module_name)
    for module in process.list_modules():
        if module.name.lower() == module_name.lower():
            return module.lpBaseOfDll
    raise ValueError(f"Module {module_name} not found in the process.")


def write_bytes_to_address(process, address, data):
    process.write_bytes(address, data, len(data))


def read_bytes_from_address(process, address, size):
    return process.read_bytes(address, size)


def check_process(proc_name):
    try:
        pymem.Pymem(proc_name)
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
    zo = m.floor(i/8)
    return m.floor(x+(m.cos(i*angle)*r)), m.floor(y+(m.sin(i*angle)*r)), z+(zo*30)
    

def patch_save(path):
    vehicle_nums = parse_vehicles(f'{path}\\vehicles')

    veh_pattern = settings.VEH_PATTERN.split("*")
    veh_data_pattern = settings.VEH_DATA_PATTERN.split("*")
    veh_group_data_pattern = settings.VEH_GROUP_DATA_PATTERN.split("*")

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
        veh_data_f = sub(rf"{settings.VEH}", result, scene_f)
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
def steal_vehicle(state):
    base_addr = get_base_address(settings.PROCESS_NAME)
    pm = pymem.Pymem(settings.PROCESS_NAME)
    if state:
        r_data = read_bytes_from_address(pm, base_addr+settings.OFFSET, 4)
        value = struct.unpack('<I', r_data)[0]
        w_data = struct.pack('<I', value+1)
        write_bytes_to_address(pm, base_addr+settings.OFFSET, w_data)
    else:
        r_data = read_bytes_from_address(pm, base_addr+settings.OFFSET, 4)
        value = struct.unpack('<I', r_data)[0]
        w_data = struct.pack('<I', value-1)
        write_bytes_to_address(pm, base_addr+settings.OFFSET, w_data)


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

