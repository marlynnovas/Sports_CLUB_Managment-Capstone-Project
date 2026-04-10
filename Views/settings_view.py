import flet as ft

def SettingsView(page: ft.Page):
    # Header
    header = ft.Row([
        ft.Column([
            ft.Text("Settings", size=32, weight=ft.FontWeight.BOLD),
            ft.Text("Configure your application preferences", color=ft.Colors.ON_SURFACE_VARIANT)
        ], expand=True),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    # Theme settings
    theme_switch = ft.Switch(
        label="Dark Mode",
        value=page.theme_mode == ft.ThemeMode.DARK,
        on_change=lambda e: toggle_theme(e.control.value)
    )
    
    def toggle_theme(is_dark):
        page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        page.update()
    
    # App info
    app_info = ft.Column([
        ft.Text("App Configuration", size=20, weight=ft.FontWeight.BOLD),
        ft.TextField(label="System Name", value="Sports Club Management", width=400),
        ft.TextField(label="Database Path", value="sports_club.db", read_only=True, width=400),
        ft.Divider(),
        ft.Text("Appearance", size=20, weight=ft.FontWeight.BOLD),
        theme_switch,
        ft.Divider(),
        ft.Text("Admin Account", size=20, weight=ft.FontWeight.BOLD),
        ft.Row([
            ft.Text("Current User: Administrator", expand=True),
            ft.ElevatedButton("Change Password", icon=ft.Icons.LOCK_RESET)
        ]),
    ], spacing=15)
    
    main_content = ft.Column([
        header,
        ft.Divider(height=2, color=ft.Colors.TRANSPARENT),
        ft.Container(
            content=app_info,
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            border_radius=10,
            padding=30,
            expand=True
        )
    ], spacing=20, expand=True)
    
    return ft.Container(content=main_content, padding=30, expand=True)
