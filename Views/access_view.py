import flet as ft
from services.access_service import AccessService


def AccessLogView(page: ft.Page):

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
        today   = AccessService.count_today()
        granted = AccessService.count_granted_today()
        denied  = AccessService.count_denied_today()
        active  = AccessService.count_active_now()
        peak    = AccessService.peak_hour_today()
        return ft.Row([
            mini_stat("Total Today",  today,   ft.Colors.BLUE),
            mini_stat("Granted",      granted, ft.Colors.GREEN),
            mini_stat("Denied",       denied,  ft.Colors.RED),
            mini_stat("Active Now",   active,  ft.Colors.PURPLE),
            mini_stat("Peak Hour",    peak,    ft.Colors.ORANGE),
        ], spacing=12)

    stats_container = ft.Container(content=make_stats())

    # ── hourly traffic chart ─────────────────────────────────────────────
    def make_traffic():
        hourly  = AccessService.hourly_traffic_today()
        hr_max  = max((v for _, v in hourly), default=1) or 1

        def hr_bar(label, val):
            h   = max(4, int(70 * val / hr_max))
            clr = ft.Colors.BLUE_600 if val == hr_max else ft.Colors.BLUE_300
            return ft.Column([
                ft.Text(str(val), size=10, weight=ft.FontWeight.BOLD),
                ft.Container(bgcolor=clr, width=20, height=h, border_radius=4),
                ft.Text(label, size=8, color=ft.Colors.ON_SURFACE_VARIANT),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3)

        return ft.Container(
            content=ft.Column([
                ft.Text("Hourly Traffic (Today)", size=14, weight=ft.FontWeight.BOLD),
                ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                ft.Row(
                    [hr_bar(l, v) for l, v in hourly] if any(v for _, v in hourly)
                    else [ft.Text("No data today", color=ft.Colors.ON_SURFACE_VARIANT, size=12)],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    vertical_alignment=ft.CrossAxisAlignment.END
                )
            ]),
            bgcolor=ft.Colors.SURFACE_CONTAINER, border_radius=12, padding=18, expand=True
        )

    traffic_container = ft.Container(content=make_traffic(), expand=True)

    # ── weekly outcome ───────────────────────────────────────────────────
    def make_outcome():
        granted, denied, total = AccessService.week_outcome_counts()
        g_pct = int(granted * 100 / total)
        d_pct = 100 - g_pct
        return ft.Container(
            content=ft.Column([
                ft.Text("Access Outcomes (7 days)", size=14, weight=ft.FontWeight.BOLD),
                ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                *[
                    ft.Row([
                        ft.Text(lbl, expand=True, size=12),
                        ft.Container(bgcolor=clr, width=max(4, int(pct * 0.9)), height=14, border_radius=6),
                        ft.Text(f"{cnt}", size=12, width=40, text_align=ft.TextAlign.RIGHT),
                    ])
                    for lbl, cnt, pct, clr in [
                        ("Granted", granted, g_pct, ft.Colors.GREEN_400),
                        ("Denied",  denied,  d_pct, ft.Colors.RED_400),
                    ]
                ]
            ], spacing=10),
            bgcolor=ft.Colors.SURFACE_CONTAINER, border_radius=12, padding=18, expand=True
        )

    outcome_container = ft.Container(content=make_outcome(), expand=True)

    # ── log table ────────────────────────────────────────────────────────
    table = ft.DataTable(
        column_spacing=20,
        columns=[
            ft.DataColumn(ft.Text("Date & Time")),
            ft.DataColumn(ft.Text("Member")),
            ft.DataColumn(ft.Text("Result")),
            ft.DataColumn(ft.Text("Message")),
        ],
        rows=[],
        expand=True
    )

    def refresh(e=None):
        stats_container.content  = make_stats()
        traffic_container.content = make_traffic()
        outcome_container.content = make_outcome()

        table.rows.clear()
        logs = AccessService.get_recent_logs(limit=50)
        if logs:
            for log in logs:
                granted = bool(log["granted"])
                chip_c  = ft.Colors.GREEN if granted else ft.Colors.RED
                chip_bg = ft.Colors.GREEN_100 if granted else ft.Colors.RED_100
                label   = "Granted" if granted else "Denied"
                table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(log["access_time"])),
                    ft.DataCell(ft.Text(f"{log['first_name']} {log['last_name']}",
                                        weight=ft.FontWeight.W_500)),
                    ft.DataCell(ft.Chip(ft.Text(label), bgcolor=chip_bg,
                                        label_text_style=ft.TextStyle(color=chip_c))),
                    ft.DataCell(ft.Text(log["message"] or "—")),
                ]))
        else:
            table.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text("No access logs found", color=ft.Colors.ON_SURFACE_VARIANT)),
                *[ft.DataCell(ft.Text("")) for _ in range(3)],
            ]))
        page.update()

    refresh()

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("Access Logs", size=30, weight=ft.FontWeight.BOLD),
                    ft.Text("Real-time access monitoring and history",
                            color=ft.Colors.ON_SURFACE_VARIANT, size=13),
                ], expand=True),
                ft.IconButton(ft.Icons.REFRESH, on_click=refresh),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            stats_container,
            ft.Row([traffic_container, outcome_container], spacing=12),
            ft.Text("Access History", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column([table], scroll=ft.ScrollMode.AUTO, expand=True),
                bgcolor=ft.Colors.SURFACE_CONTAINER, border_radius=12, padding=10, expand=True
            ),
        ], spacing=16, expand=True, scroll=ft.ScrollMode.AUTO),
        padding=28, expand=True
    )
