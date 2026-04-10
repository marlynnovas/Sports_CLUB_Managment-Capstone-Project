import flet as ft
from services.member_service import MemberService
from services.access_service import AccessService
from services.payment_service import PaymentService
from services.plan_service import PlanService
from services.membership_service import MembershipService
from datetime import date, timedelta

def DashboardView(page: ft.Page):

    # ── helpers ─────────────────────────────────────────────────────────
    def stat_card(title, value, subtitle, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=24, color=ft.Colors.WHITE),
                        bgcolor=color, border_radius=10, padding=10,
                        width=44, height=44
                    ),
                    ft.Column([
                        ft.Text(str(value), size=26, weight=ft.FontWeight.BOLD),
                        ft.Text(title, size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                    ], spacing=0, expand=True),
                ], spacing=12),
                ft.Text(subtitle, size=11, color=ft.Colors.ON_SURFACE_VARIANT),
            ], spacing=6),
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            border_radius=12, padding=18, expand=True
        )

    # ── quick action dialogs ─────────────────────────────────────────────
    # NEW MEMBER DIALOG
    first_name_input = ft.TextField(label="First Name")
    last_name_input  = ft.TextField(label="Last Name")
    email_input      = ft.TextField(label="Email")
    
    def save_member(e):
        mid = MemberService.create_member(first_name_input.value, last_name_input.value, email_input.value, "")
        if mid:
            page.snack_bar = ft.SnackBar(ft.Text(f"Member #{mid} created!"), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
            new_member_dialog.open = False
            page.update()
            # Refresh dashboard in a real app or just tell user to refresh
            
    new_member_dialog = ft.AlertDialog(
        title=ft.Text("Quick Register Member"),
        content=ft.Column([first_name_input, last_name_input, email_input], tight=True),
        actions=[ft.TextButton("Cancel", on_click=lambda _: setattr(new_member_dialog, "open", False)), 
                 ft.ElevatedButton("Create", on_click=save_member)]
    )
    page.overlay.append(new_member_dialog)

    # RECORD PAYMENT DIALOG
    membership_dropdown = ft.Dropdown(label="Select Membership", options=[])
    payment_amount = ft.TextField(label="Amount ($)", keyboard_type=ft.KeyboardType.NUMBER)

    def load_ms_options(e=None):
        ms_list = MembershipService.get_all_memberships()
        membership_dropdown.options = [
            ft.dropdown.Option(key=str(m["id"]), text=f"#{m['id']} - {m['first_name']} {m['last_name']}")
            for m in ms_list
        ]
        page.update()

    def submit_payment(e):
        if membership_dropdown.value and payment_amount.value:
            PaymentService.create_payment(int(membership_dropdown.value), float(payment_amount.value))
            payment_dialog.open = False
            page.update()

    payment_dialog = ft.AlertDialog(
        title=ft.Text("Quick Payment"),
        content=ft.Column([membership_dropdown, payment_amount], tight=True),
        actions=[ft.TextButton("Cancel", on_click=lambda _: setattr(payment_dialog, "open", False)), 
                 ft.ElevatedButton("Register", on_click=submit_payment)]
    )
    page.overlay.append(payment_dialog)

    # MANUAL ACCESS LOG DIALOG
    member_id_log = ft.TextField(label="Member ID", keyboard_type=ft.KeyboardType.NUMBER)
    
    def submit_log(e):
        if member_id_log.value:
            AccessService.log_access(int(member_id_log.value), True, "Manual entry logged from dashboard")
            log_dialog.open = False
            page.update()

    log_dialog = ft.AlertDialog(
        title=ft.Text("Manual Access Log"),
        content=ft.Column([member_id_log], tight=True),
        actions=[ft.TextButton("Cancel", on_click=lambda _: setattr(log_dialog, "open", False)), 
                 ft.ElevatedButton("Log Entry", on_click=submit_log)]
    )
    page.overlay.append(log_dialog)

    # ── quick actions row ────────────────────────────────────────────────
    quick_actions = ft.Container(
        content=ft.Column([
            ft.Text("Quick Actions", size=14, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.ElevatedButton("New Member",     icon=ft.Icons.PERSON_ADD,  bgcolor=ft.Colors.BLUE_700,  color=ft.Colors.WHITE,
                                  on_click=lambda _: setattr(new_member_dialog, "open", True)),
                ft.ElevatedButton("Record Payment", icon=ft.Icons.ADD_CARD,    bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE,
                                  on_click=lambda _: (load_ms_options(), setattr(payment_dialog, "open", True))),
                ft.ElevatedButton("Manual Log",     icon=ft.Icons.LOGIN,       bgcolor=ft.Colors.ORANGE_700,color=ft.Colors.WHITE,
                                  on_click=lambda _: setattr(log_dialog, "open", True)),
            ], spacing=10),
        ]),
        bgcolor=ft.Colors.SURFACE_CONTAINER, border_radius=12, padding=18
    )

    # ── main display content ──────────────────────────────────────────────
    total_m = MemberService.count_members()
    active_m = MemberService.count_by_status("active")
    rev_mtd = PaymentService.revenue_mtd()
    acc_today = AccessService.count_today()
    pend_b = PaymentService.count_by_status("pending")

    stats_row = ft.Row([
        stat_card("Total Members",  total_m,   "All registered",     ft.Icons.PEOPLE,    ft.Colors.BLUE_600),
        stat_card("Active",         active_m,  "Current subs",       ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN_600),
        stat_card("Revenue MTD",    f"${rev_mtd:,.0f}", "Paid bills", ft.Icons.MONEY,     ft.Colors.PURPLE_600),
        stat_card("Entries Today",  acc_today, "Gate logs",          ft.Icons.LOGIN,     ft.Colors.ORANGE_600),
        stat_card("Pending Bills",  pend_b,    "Unpaid items",       ft.Icons.RECEIPT,   ft.Colors.RED_600),
    ], spacing=12)

    # Activity table
    logs = AccessService.get_recent_logs(limit=8)
    activity_table = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("Member")), ft.DataColumn(ft.Text("Time")), ft.DataColumn(ft.Text("Result"))],
        rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(f"{l['first_name']} {l['last_name']}")),
                ft.DataCell(ft.Text(l['access_time'])),
                ft.DataCell(ft.Chip(ft.Text("Granted" if l['granted'] else "Denied"), 
                                    bgcolor=ft.Colors.GREEN_100 if l['granted'] else ft.Colors.RED_100))
            ]) for l in logs
        ],
        expand=True
    )

    return ft.Container(
        content=ft.Column([
            ft.Text("Dashboard Overview", size=32, weight=ft.FontWeight.BOLD),
            stats_row,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            quick_actions,
            ft.Text("Recent Access Activity", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column([activity_table], scroll=ft.ScrollMode.AUTO, expand=True),
                bgcolor=ft.Colors.SURFACE_CONTAINER, border_radius=12, padding=16, expand=True
            ),
        ], spacing=16, expand=True, scroll=ft.ScrollMode.AUTO),
        padding=28, expand=True
    )
