import flet as ft
import functional as func
from settings import PROCESS_NAME, APP_NAME, ON_VEHICLE_PATTERN, OFF_VEHICLE_PATTERN
from tkinter import filedialog


def check_reset(func):
    def wrapper(self, *args, **kwargs):
        if self._reset:
            self._get_process_data()
        return func(self, *args, **kwargs)
    return wrapper


class Offset:
    def __init__(self, name, pattern, additional_static_offset = 0):
        self.name = name
        self.pattern = pattern
        self.offset = 0
        self.calculated = False
        self.additional_static_offset = additional_static_offset
    

    def calculate_offset(self, Process_State_obj):
        self.offset = func.search_offset_by_pattern(Process_State_obj.get_process_object(), Process_State_obj.get_process_module(), Process_State_obj.get_base_address(), self.pattern) + self.additional_static_offset
        self.calculated = True


class ProcessState:
    _instance = None


    def __new__(cls, process_name: str = "", module_name: str = ""):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    

    def __init__(self, process_name: str = "" , module_name: str = ""):
        if not hasattr(self, "_initialized"):
            self._reset = False
            self._process_name = process_name
            self._module_name = module_name
            self._get_process_data()
            self._offsets = {}
            self._initialized = True


    def reset(self):
        self._reset = True


    def _get_process_data(self):
        try:
            self._process_module = func.get_process_module(self._process_name, self._module_name)
            self._process_object = func.get_process_object(self._process_name)
            self._base_address = func.get_base_address(self._process_module)

            for i in self._offsets.keys():
                if not self._offsets[i].calculated:
                    self._offsets[i].calculate_offset(self)

            self._reset = False
        except Exception as e:
            self.reset()


    def change_process(self, process_name: str, module_name: str):
        self._process_name = process_name
        self._module_name = module_name
        self._get_process_data()

    @check_reset
    def add_offset(self, offset: Offset):
        self._offsets[offset.name] = offset

    @check_reset
    def get_offset(self, offset_name):
        if self._offsets[offset_name].calculated == False:
            self._offsets[offset_name].calculate_offset(self)
        return self._offsets[offset_name]
    
    @check_reset    
    def get_process_name(self):
        return self._process_name
    
    @check_reset
    def get_process_object(self):
        return self._process_object
    
    @check_reset
    def get_module_name(self):
        return self._module_name
    
    @check_reset
    def get_base_address(self):
        return self._base_address
    
    @check_reset
    def get_process_module(self):
        return self._process_module
    

def add_patterns():
    try:
        Process_State.add_offset(Offset("vehicle", ON_VEHICLE_PATTERN, 0x4))
        return True, False
    except:
        try:
            Process_State.add_offset(Offset("vehicle", OFF_VEHICLE_PATTERN, 0x4))
            return True, True
        except:
            return False, False

def show_pop_up(text, page: ft.Page):
    page.snack_bar = ft.SnackBar(ft.Text(f"{text}", size=20, color='#B4B4B4'))
    page.snack_bar.bgcolor = '#44506F'
    page.snack_bar.opacity = 0.2
    page.snack_bar.open = True
    page.update()


def main(page: ft.Page):
    global Process_State
    theme = page.theme_mode
    page.clean()
    page.title = APP_NAME
    page.theme_mode = theme
    page.window_width = 700
    page.window_height = 700
    patterns_added, is_off = add_patterns()
    #Refs:
    path_line_ref = ft.Ref[ft.TextField]()
    switch = ft.Ref[ft.Switch]()
    if is_off:
        switch.current.value = True

    if not patterns_added:
        Process_State.reset()
        show_pop_up("Game process not found", page)


    def on_hover(e):
        if e.data == "true": e.control.opacity = 1
        else: e.control.opacity = 0.7
        e.control.update()


    def on_resize_window(e):
        main_frame.height = page.height
        main_frame.width = page.width
        path_line.width = page.width*0.8
        page.update()
    page.on_resized = on_resize_window


    # Buttons
    def save_vehicle():
        try:
            result = func.save_vehicle_from(func.check_newest_file(func.read_file()))
            show_pop_up('Saved to: '+result, page)
        except Exception as e:
            show_pop_up('Error while saving vehicle: '+str(e), page)


    def save_vehicle_from():
        try:
            result = func.save_vehicle_from(filedialog.askdirectory())
            show_pop_up('Saved to: '+result, page)
        except Exception as e:
            show_pop_up('Error while saving vehicle: '+str(e), page)

            
    def change_save_folder(path_line_ref):
        try:
            new_txt = filedialog.askdirectory()
            func.rewrite_file(new_txt)
            path_line_ref.current.value = new_txt
            page.update()
        except Exception as e:
            show_pop_up('Error while changing save folder: '+str(e), page)


    def steal_vehicle(e):
        global Process_State
        try:
            if func.check_process(PROCESS_NAME):
                func.steal_vehicle(Process_State.get_process_object(), Process_State.get_base_address(), Process_State.get_offset('vehicle').offset ,e.control.value)
            else:
                Process_State.reset()
                show_pop_up("Game process not found", page)
                e.control.value = False
        except Exception as e:
            show_pop_up('Error while stealing vehicle: '+str(e), page)

    # Ui


    column_1 = ft.Container(
        opacity=1,
        bgcolor="#212124",
        margin=ft.padding.only(left=20, top=20),
        adaptive=True,
        on_hover=on_hover,
        alignment=ft.alignment.top_center,
        content=ft.Column([
            ft.Switch(
                ref=switch,
                label="Open save menu",
                on_change= steal_vehicle,
                thumb_color="#585660",
                track_color="#000000",
                opacity=0.5,
                focus_color="#585660",
            ),
            ft.Container(
                content=ft.Text("Save vehicle from last save", size=20, color="#ffffff", font_family="Roboto"),
                alignment=ft.alignment.center,
                bgcolor="#212124",
                on_click= lambda e: save_vehicle(),
                opacity=0.5,
                border_radius=6,
                border=ft.border.all(1, "#558bbd"),
                width=400,
                height=40,
                on_hover=on_hover,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=["#212124", "#39393b"],
                    stops=[0.0, 1.0],
                ),
            ),
            ft.Container(
                content=ft.Text("Save vehicle from selected save", size=20, color="#ffffff", font_family="Roboto"),
                alignment=ft.alignment.center,
                bgcolor="#212124",
                on_click= lambda e: save_vehicle_from(),
                opacity=0.5,
                border_radius=6,
                border=ft.border.all(1, "#558bbd"),
                width=400,
                height=40,
                on_hover=on_hover,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=["#212124", "#39393b"],
                    stops=[0.0, 1.0],
                ),
            ),
            ft.Container(
                content=ft.Text("Change saves folder", size=20, color="#ffffff", font_family="Roboto"),
                alignment=ft.alignment.center,
                bgcolor="#212124",
                on_click= lambda e: change_save_folder(path_line_ref),
                opacity=0.5,
                border_radius=6,
                border=ft.border.all(1, "#558bbd"),
                width=400,
                height=40,
                on_hover=on_hover,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=["#212124", "#39393b"],
                    stops=[0.0, 1.0],
                ),
            ),
            ],
            spacing=10,
        ),
        disabled= False
    )


    Top = ft.Container(
        content=ft.Text(APP_NAME, size=30, weight=ft.FontWeight.BOLD, color="#FFFFFF", font_family="Roboto"),
        alignment=ft.alignment.center
    )


    path_line = ft.Container(
        content=ft.Text(ref=path_line_ref,
            value="Saves folder: " + func.read_file(), size=15, color="#ffffff", font_family="Roboto"
        ),
        bgcolor="#1a1a1a",
        border_radius=10,
        width=page.width*0.8,
        alignment=ft.alignment.center,
    )
    

    main_frame = ft.Container(
        content = ft.Column(
            [
            Top,
            ft.Row(
                [column_1],
                spacing=50,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            ft.Container(
                content=path_line,
                alignment=ft.alignment.center
            ),
            ],
        ),
        bgcolor="#212124",
        width=page.width,
        height=page.height,
        alignment=ft.alignment.center
    )


    page.add(main_frame)
    page.update()


if __name__ == "__main__":
    func.create_directory()
    func.auto_fill_file()
    func.read_file()
    Process_State = ProcessState(process_name=PROCESS_NAME,module_name=PROCESS_NAME)
    ft.app(target=main)
