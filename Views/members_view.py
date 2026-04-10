import flet as ft
from services.member_service import MemberService
from services.plan_service import PlanService
from services.membership_service import MembershipService
from datetime import date, timedelta

def MembersView(page: ft.Page):

    # ── stat cards ───────────────────────────────────────────────────────
    def mini_stat(title, val, clr):
        return ft.Container(
            content=ft.Column([
                ft.Text(str(val), size=24, weight=ft.FontWeight.BOLD, color=clr),
                ft.Text(title, size=12, color=ft.Colors.ON_SURFACE_VARIANT),
            ], spacing=2),
            bgcolor=ft.Colors.SURFACE_CONTAINER, border_radius=10, padding=16, expand=True
        )

    def make_stats():
        return ft.Row([
            mini_stat("Total Members",     MemberService.count_members(),             ft.Colors.BLUE),
            mini_stat("Active",            MemberService.count_by_status("active"),   ft.Colors.GREEN),
            mini_stat("Expired",           MemberService.count_by_status("expired"),  ft.Colors.RED),
            mini_stat("No Plan",           MemberService.count_no_plan(),             ft.Colors.GREY),
            mini_stat("Renewals this mo.", MemberService.count_renewals_this_month(), ft.Colors.ORANGE),
        ], spacing=12)

    stats_container = ft.Container(content=make_stats())

    # ── add/edit member dialog ───────────────────────────────────────────
    edit_mode = False
    current_mid = None

    first_name_input = ft.TextField(label="First Name")
    last_name_input  = ft.TextField(label="Last Name")
    email_input      = ft.TextField(label="Email")
    phone_input      = ft.TextField(label="Phone")
    
    plan_dropdown = ft.Dropdown(label="Initial Membership Plan", options=[])

    def load_plans():
        plans = PlanService.get_all_plans()
        plan_dropdown.options = [ft.dropdown.Option(key=str(p["id"]), text=f"{p['name']} (${p['price']})") for p in plans]
        page.update()

    def save_member(e):
        nonlocal edit_mode, current_mid
        if not first_name_input.value or not last_name_input.value or not email_input.value:
            return
        
        if edit_mode:
            MemberService.update_member(current_mid, first_name_input.value, last_name_input.value, email_input.value, phone_input.value)
        else:
            mid = MemberService.create_member(first_name_input.value, last_name_input.value, email_input.value, phone_input.value)
            if mid and plan_dropdown.value:
                pid = int(plan_dropdown.value)
                plan = next((p for p in PlanService.get_all_plans() if p["id"] == pid), None)
                if plan:
                    end = date.today() + timedelta(days=plan["duration_months"] * 30)
                    MembershipService.create_membership(mid, pid, date.today().isoformat(), end.isoformat())

        dialog.open = False
        refresh()
        page.update()

    dialog = ft.AlertDialog(
        title=ft.Text("Member"),
        content=ft.Column([
            first_name_input, last_name_input, email_input, phone_input,
            plan_dropdown
        ], tight=True),
        actions=[
            ft.TextButton("Cancel", on_click=lambda _: setattr(dialog, "open", False)),
            ft.ElevatedButton("Save", on_click=save_member),
        ]
    )
    page.overlay.append(dialog)

    def open_dialog(m=None):
        nonlocal edit_mode, current_mid
        load_plans()
        if m:
            edit_mode = True
            current_mid = m["id"]
            dialog.title.value = f"Edit Member #{m['id']}"
            first_name_input.value = m["first_name"]
            last_name_input.value = m["last_name"]
            email_input.value = m["email"]
            phone_input.value = m["phone"] or ""
            plan_dropdown.value = None
            plan_dropdown.visible = False # Only assign plan on creation here
        else:
            edit_mode = False
            dialog.title.value = "New Member"
            first_name_input.value = ""
            last_name_input.value = ""
            email_input.value = ""
            phone_input.value = ""
            plan_dropdown.value = None
            plan_dropdown.visible = True
            
        dialog.open = True
        page.update()

    # ── data table ───────────────────────────────────────────────────────
    table = ft.DataTable(
        column_spacing=20,
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Full Name")),
            ft.DataColumn(ft.Text("Plan")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Actions")),
        ],
        rows=[],
        expand=True
    )

    def refresh(e=None):
        table.rows.clear()
        members = MemberService.get_all_members()
        for m in members:
            def delete_cb(_, mid=m["id"]):
                MemberService.delete_member(mid)
                refresh()
                page.update()
            
            def edit_cb(_, mem=m):
                open_dialog(mem)

            status = (m["membership_status"] or "none").capitalize()
            table.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(m["id"]))),
                ft.DataCell(ft.Text(f"{m['first_name']} {m['last_name']}", weight=ft.FontWeight.W_500)),
                ft.DataCell(ft.Text(m["plan_name"] or "No Plan")),
                ft.DataCell(ft.Chip(ft.Text(status), bgcolor=ft.Colors.GREEN_100 if status=="Active" else ft.Colors.RED_100)),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.Icons.EDIT, icon_color=ft.Colors.BLUE_400, on_click=edit_cb),
                    ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED_400, on_click=delete_cb),
                ])),
            ]))
        stats_container.content = make_stats()
        page.update()

    refresh()

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Members Management", size=30, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("Add Member", icon=ft.Icons.ADD, on_click=lambda _: open_dialog(),
                                  bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            stats_container,
            ft.Container(
                content=ft.Column([table], scroll=ft.ScrollMode.AUTO, expand=True),
                bgcolor=ft.Colors.SURFACE_CONTAINER, border_radius=12, padding=18, expand=True
            ),
        ], spacing=16, expand=True),
        padding=28, expand=True
    )
