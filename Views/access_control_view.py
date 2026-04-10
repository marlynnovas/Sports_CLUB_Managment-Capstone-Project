import flet as ft
from services.access_service import AccessService
from services.member_service import MemberService
from database.connection import get_connection

def AccessControlView(page: ft.Page):
    # Banner area to show success or fail
    status_banner = ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.LOCK, size=64, color=ft.Colors.GREY_400),
            ft.Text("Waiting for validation...", size=18, color=ft.Colors.ON_SURFACE_VARIANT)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=40, border_radius=15, bgcolor=ft.Colors.SURFACE_CONTAINER, 
        width=500, alignment=ft.Alignment(0, 0)
    )

    member_id_field = ft.TextField(
        label="Enter Member ID", 
        width=300, 
        keyboard_type=ft.KeyboardType.NUMBER,
        on_submit=lambda e: validate_access(e)
    )

    def validate_access(e):
        if not member_id_field.value:
            return
        
        mid = int(member_id_field.value)
        # Fetch status
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.first_name || ' ' || m.last_name as full_name, 
                   ms.status, ms.end_date, p.name as plan_name
            FROM members m
            LEFT JOIN memberships ms ON m.id = ms.member_id
            LEFT JOIN plans p ON ms.plan_id = p.id
            WHERE m.id = ?
            ORDER BY ms.id DESC LIMIT 1
        """, (mid,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            update_banner(False, "Member Not Found", ft.Icons.ERROR, ft.Colors.RED)
            AccessService.log_access(mid, False, "Member not found")
        else:
            name, status, end_date, plan = row
            import datetime
            today = datetime.date.today().isoformat()
            
            if status == "active" and end_date and end_date >= today:
                update_banner(True, f"Welcome, {name}!", ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN)
                AccessService.log_access(mid, True, f"Granted - Plan: {plan}")
            else:
                reason = "Membership Expired" if status == "active" else "No Active Plan"
                update_banner(False, f"Access Denied: {reason}", ft.Icons.BLOCK, ft.Colors.RED)
                AccessService.log_access(mid, False, f"Denied - {reason}")
        
        member_id_field.value = ""
        page.update()

    def update_banner(success, message, icon, color):
        status_banner.bgcolor = ft.Colors.GREEN_400 if success else ft.Colors.RED_400
        status_banner.content = ft.Column([
            ft.Icon(icon, size=80, color=ft.Colors.WHITE),
            ft.Text(message, size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Text("Valid as of today" if success else "Contact support", color=ft.Colors.WHITE70)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        page.update()

    # Layout construction
    main_layout = ft.Column([
        ft.Row([
            ft.Column([
                ft.Text("Gate Access Control", size=32, weight=ft.FontWeight.BOLD),
                ft.Text("Validate arrivals in real-time", color=ft.Colors.ON_SURFACE_VARIANT)
            ], expand=True),
        ]),
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        ft.Container(
            content=ft.Column([
                ft.Text("Real-Time Validation Terminal", size=22, weight=ft.FontWeight.BOLD),
                ft.Text("Enter member ID manually to simulate card scan", 
                        color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Row([
                    member_id_field,
                    ft.ElevatedButton("Validate", icon=ft.Icons.PLAY_ARROW, 
                                      on_click=validate_access, height=50)
                ], spacing=10),
                status_banner
            ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            padding=40, border_radius=20, alignment=ft.Alignment(0, 0)
        ),
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        ft.Text("Gate Operations Log", size=20, weight=ft.FontWeight.BOLD),
    ], spacing=16, expand=True, scroll=ft.ScrollMode.AUTO)

    return ft.Container(content=main_layout, padding=28, expand=True)
