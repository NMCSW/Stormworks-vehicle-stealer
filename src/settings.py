#Global
PROCESS_NAME = 'stormworks64.exe'

APP_NAME = 'SW stealer'

#Memory offset
OFFSET = 0x7508AF

#Search pattern
VEH = '\t<vehicles>\n\t\t<vehicle_data/>\n\t\t<vehicle_group_data/>\n\t</vehicles>'

#Replace pattern
VEH_PATTERN = '\t<vehicles vehicle_counter="*" group_counter="*">'

VEH_DATA_PATTERN = ('\t\t\t<vehicle id="*" vehicle_group_id="*" is_static="true" player_created="true" on_map="true" is_first_spawn="false"'+
    ' is_no_sleep="true" is_editable="true" parent_mission_component_id="4294967295">\n\t\t\t\t<transform 00="-0.53497" 01="-0.752817"'+
    ' 02="-0.383503" 10="-0.664604" 11="0.655232" 12="-0.359127" 20="0.52164" 21="0.062755" 22="-0.850854" 30="*" 31="*"'+
    ' 32="*"/>\n\t\t\t\t<bounds>\n\t\t\t\t\t<min x="-5.603946" y="-1.658837" z="-7.397019"/>\n\t\t\t\t\t<max x="5.646054"'+
    ' y="2.250373" z="8.842415"/>\n\t\t\t\t</bounds>\n\t\t\t\t<active_transponders/>\n\t\t\t\t<authors/>\n\t\t\t</vehicle>'
)

VEH_GROUP_DATA_PATTERN = ('\t\t\t<group id="*" edit_grid_id="edit1">\n\t\t\t\t<vehicles>\n\t\t\t\t\t<v value="*"/>\n'+
    '\t\t\t\t</vehicles>\n\t\t\t\t<edit_grid_pos x="-27.770796" y="1.391634" z="-4.158787"/>\n\t\t\t\t'+
    '<initial_transform 00="-1" 22="-1" 30="-27.770796" 31="1.391634" 32="-4.158787"/>'+
    '\n\t\t\t</group>'
) 