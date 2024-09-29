import flet as ft
import functional as func
import settings as settings
from tkinter import filedialog

def clamp(x, xmin, xmax):
    return max(min(x, xmax),xmin)


def show_pop_up(text, page):
    page.snack_bar = ft.SnackBar(ft.Text(f"{text}", size=20, color='#B4B4B4'))
    page.snack_bar.bgcolor = '#44506F'
    page.snack_bar.opacity = 0.2
    page.snack_bar.open = True
    page.update()


def main(page: ft.Page):
    theme = page.theme_mode
    page.clean()
    page.title = settings.APP_NAME
    page.theme_mode = theme
    page.window.width = 700
    page.window.height = 400


    def on_hover(e):
        if e.data == "true": e.control.opacity = 1
        else: e.control.opacity = 0.7
        e.control.update()


    def on_resize_window(e):
        main_frame.height = page.window.height
        main_frame.width = page.window.width
        path_line.width = page.window.width*0.8
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
        try:
            if func.check_process(settings.PROCESS_NAME):
                func.steal_vehicle(e.control.value)
            else:
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
        content=ft.Text(settings.APP_NAME, size=30, weight=ft.FontWeight.BOLD, color="#FFFFFF", font_family="Roboto"),
        alignment=ft.alignment.center
    )

    path_line_ref = ft.Ref[ft.TextField]()

    path_line = ft.Container(
        content=ft.Text(ref=path_line_ref,
            value="Saves folder: " + func.read_file(), size=15, color="#ffffff", font_family="Roboto"
        ),
        bgcolor="#1a1a1a",
        border_radius=10,
        width=page.window.width*0.8,
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
        width=page.window.width,
        height=page.window.height,
        alignment=ft.alignment.center
    )


    page.add(main_frame)
    page.update()

if __name__ == "__main__":
    func.create_directory()
    func.auto_fill_file()
    func.read_file()
    ft.app(target=main)
