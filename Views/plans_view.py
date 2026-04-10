import flet as ft
from services.plan_service import PlanService

def PlansView(page: ft.Page):
    # Header area
    header = ft.Row([
        ft.Column([
            ft.Text("Membership Plans", size=32, weight=ft.FontWeight.BOLD),
            ft.Text("Manage and create subscription plans for the club", 
                    color=ft.Colors.ON_SURFACE_VARIANT)
        ], expand=True),
        ft.ElevatedButton("Create New Plan", icon=ft.Icons.ADD, 
                          bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE,
                          on_click=lambda _: open_add_dialog())
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # ── State ──────────────────────────────────────────────────
    edit_mode = False
    current_plan_id = None

    # ── Dialogs ───────────────────────────────────────────────
    dialog_title = ft.Text("Plan")
    name_input     = ft.TextField(label="Plan Name")
    price_input    = ft.TextField(label="Price ($)", keyboard_type=ft.KeyboardType.NUMBER)
    months_input   = ft.TextField(label="Duration (months)", keyboard_type=ft.KeyboardType.NUMBER)
    desc_input     = ft.TextField(label="Description", multiline=True)

    def open_add_dialog():
        nonlocal edit_mode
        edit_mode = False
        dialog_title.value = "Add New Plan"
        name_input.value = ""
        price_input.value = ""
        months_input.value = ""
        desc_input.value = ""
        dialog.open = True
        page.update()

    def open_edit_dialog(p):
        nonlocal edit_mode, current_plan_id
        edit_mode = True
        current_plan_id = p["id"]
        dialog_title.value = f"Edit Plan #{p['id']}"
        name_input.value = p["name"]
        price_input.value = str(p["price"])
        months_input.value = str(p["duration_months"])
        desc_input.value = p["description"] or ""
        dialog.open = True
        page.update()

    def save_plan(e):
        nonlocal edit_mode, current_plan_id
        if not name_input.value or not price_input.value: return
        
        try:
            price = float(price_input.value)
            mos = int(months_input.value)
        except: return

        if edit_mode:
            PlanService.update_plan(current_plan_id, name_input.value, price, mos, desc_input.value)
        else:
            PlanService.create_plan(name_input.value, price, mos, desc_input.value)
            
        dialog.open = False
        refresh_table()
        page.update()

    dialog = ft.AlertDialog(
        title=dialog_title,
        content=ft.Column([name_input, price_input, months_input, desc_input], tight=True),
        actions=[
            ft.TextButton("Cancel", on_click=lambda _: setattr(dialog, "open", False)),
            ft.ElevatedButton("Save", on_click=save_plan)
        ]
    )
    page.overlay.append(dialog)

    # ── Table ────────────────────────────────────────────────
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Name")),
            ft.DataColumn(ft.Text("Price")),
            ft.DataColumn(ft.Text("Duration")),
            ft.DataColumn(ft.Text("Actions")),
        ],
        rows=[],
        expand=True
    )

    def refresh_table(e=None):
        table.rows.clear()
        plans = PlanService.get_all_plans()
        for p in plans:
            def delete_cb(_, pid=p["id"]):
                PlanService.delete_plan(pid)
                refresh_table()
                page.update()
            
            def edit_cb(_, plan=p):
                open_edit_dialog(plan)

            table.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(p["id"]))),
                ft.DataCell(ft.Text(p["name"], weight=ft.FontWeight.W_500)),
                ft.DataCell(ft.Text(f"${p['price']:,.2f}")),
                ft.DataCell(ft.Text(f"{p['duration_months']} mo.")),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.Icons.EDIT, icon_color=ft.Colors.BLUE_400, on_click=edit_cb),
                    ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED_400, on_click=delete_cb),
                ])),
            ]))
        page.update()

    refresh_table()

    # Visual elements
    def plan_card(title, price, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=32, color=color),
                ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                ft.Text(f"From ${price}"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20, border_radius=12, bgcolor=ft.Colors.SURFACE_CONTAINER, expand=True
        )

    summary_cards = ft.Row([
        plan_card("Basic", "1,500", ft.Icons.FITNESS_CENTER, ft.Colors.BLUE_400),
        plan_card("Standard", "4,000", ft.Icons.LIST, ft.Colors.PURPLE_400),
        plan_card("Premium", "15,000", ft.Icons.STAR, ft.Colors.AMBER_400),
    ], spacing=20)

    return ft.Container(content=ft.Column([
        header,
        summary_cards,
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        ft.Container(
            content=ft.Column([table], scroll=ft.ScrollMode.AUTO, expand=True),
            bgcolor=ft.Colors.SURFACE_CONTAINER, border_radius=12, padding=10, expand=True
        )
    ], spacing=16, expand=True), padding=28, expand=True)
