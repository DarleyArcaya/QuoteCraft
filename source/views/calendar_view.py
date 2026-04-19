import flet as ft
from database import queries
from datetime import datetime, date
import calendar
from utils.theme import get_theme

def CalendarView(page: ft.Page):
    # Load theme and translations | Carga el tema y las traducciones
    t = get_theme(page.data["theme"])
    i18n = page.data["i18n"]

    # Event type colors | Colores según el tipo de evento
    EVENT_TYPES = {
        "Trabajo":      "#22c97a",
        "Presupuesto":  "#f0a500",
        "Reunion":      "#4f8ef7",
        "Personal":     "#c97a22",
        "Otro":         "#8b8fa8",
    }

    # Internal state for navigation | Estado interno para la navegación
    now = datetime.now()
    state = {"year": now.year, "month": now.month}

    # UI Components | Componentes de la interfaz
    calendar_grid  = ft.Column(spacing=4)
    events_list    = ft.Column(spacing=6)
    month_label    = ft.Text("", size=16, weight=ft.FontWeight.W_600, color=t["text"])

    def get_month_name_i18n(month_index):
        # Uses the keys defined in strings.py | Usa las llaves definidas en strings.py
        return i18n.t(f"month_{month_index}")

    def get_month_events():
        # Fetch events from DB | Obtiene eventos de la DB
        return queries.get_events_by_month(state["year"], state["month"])

    def confirm_delete(event_id, is_dialog=False, current_dlg=None):
        """Confirmation dialog for deleting events | Diálogo de confirmación para borrar eventos"""
        def close_confirmation(e):
            conf_dlg.open = False
            page.update()

        def do_delete(e):
            queries.delete_event(event_id)
            conf_dlg.open = False
            if is_dialog and current_dlg:
                current_dlg.open = False
            
            build_calendar() # Refresh UI | Refresca la interfaz
            page.update()

        conf_dlg = ft.AlertDialog(
            title=ft.Text(i18n.t("delete_event_title")),
            content=ft.Text(i18n.t("delete_event_msg")),
            actions=[
                ft.TextButton(i18n.t("cancel"), on_click=close_confirmation),
                ft.ElevatedButton(i18n.t("delete"), bgcolor="#ff5f6d", color="white", on_click=do_delete),
            ],
        )
        page.overlay.append(conf_dlg)
        conf_dlg.open = True
        page.update()

    def build_calendar():
        """Main logic to render the calendar grid | Lógica principal para renderizar la cuadrícula"""
        calendar_grid.controls.clear()
        events_list.controls.clear()

        year  = state["year"]
        month = state["month"]
        month_label.value = f"{get_month_name_i18n(month)} {year}"

        # Organize events by day for easier rendering | Organiza eventos por día para facilitar el renderizado
        month_events = get_month_events()
        events_by_day = {}
        for ev in month_events:
            day = int(ev["date"].split("-")[2])
            if day not in events_by_day:
                events_by_day[day] = []
            events_by_day[day].append(ev)

        # Draw day headers (Mo, Tu, etc) | Dibuja los encabezados de los días
        day_names = [i18n.t("day_mo"), i18n.t("day_tu"), i18n.t("day_we"), i18n.t("day_th"), i18n.t("day_fr"), i18n.t("day_sa"), i18n.t("day_su")]
        header_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(d, size=11, color=t["text2"], weight=ft.FontWeight.W_600),
                    width=52, alignment=ft.alignment.Alignment.CENTER,
                )
                for d in day_names
            ],
            spacing=4,
        )
        calendar_grid.controls.append(header_row)

        # Generate month matrix | Genera la matriz del mes
        cal = calendar.monthcalendar(year, month)
        today = date.today()

        for week in cal:
            week_row = ft.Row(spacing=4)
            for day in week:
                if day == 0:
                    # Empty space for days outside the month | Espacio vacío para días fuera del mes
                    week_row.controls.append(ft.Container(width=52, height=52))
                else:
                    is_today = (day == today.day and month == today.month and year == today.year)
                    day_events = events_by_day.get(day, [])
                    date_str = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"

                    # Visual dots for events | Puntos visuales para los eventos
                    dots = ft.Row(
                        controls=[
                            ft.Container(width=6, height=6, bgcolor=ev["color"], border_radius=99)
                            for ev in day_events[:3] # Show up to 3 dots | Muestra hasta 3 puntos
                        ],
                        spacing=2,
                        alignment=ft.MainAxisAlignment.CENTER,
                    )

                    # Individual day container | Contenedor del día individual
                    day_cell = ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    str(day),
                                    size=13,
                                    color=t["accent"] if is_today else t["text"],
                                    weight=ft.FontWeight.BOLD if is_today else ft.FontWeight.W_400,
                                ),
                                dots,
                            ],
                            spacing=2,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        width=52,
                        height=52,
                        bgcolor=f"{t['accent']}30" if is_today else t["surface2"],
                        border_radius=8,
                        border=ft.border.all(2, t["accent"]) if is_today else ft.border.all(1, t["border"]),
                        alignment=ft.alignment.Alignment.CENTER,
                        on_click=lambda e, d=date_str: open_day(d),
                        ink=True,
                    )
                    week_row.controls.append(day_cell)
            calendar_grid.controls.append(week_row)

        # List of upcoming events in the month | Lista de próximos eventos en el mes
        if month_events:
            for ev in month_events:
                events_list.controls.append(event_row(ev))
        else:
            events_list.controls.append(
                ft.Text(i18n.t("no_month_events"), size=13, color=t["text2"])
            )

    def event_row(ev):
        """Standard row for the event list | Fila estándar para la lista de eventos"""
        color = ev["color"]
        day   = ev["date"].split("-")[2]
        month_index = int(ev["date"].split("-")[1])
        month_name = get_month_name_i18n(month_index)
        time_str = ev.get("time", "")

        type_map = {"Trabajo": i18n.t("type_work"), "Presupuesto": i18n.t("type_budget"), "Reunion": i18n.t("type_meeting"), "Personal": i18n.t("type_personal"), "Otro": i18n.t("type_other")}
        display_type = type_map.get(ev["type"], ev["type"])

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(width=4, bgcolor=color, border_radius=99),
                    ft.Column(
                        controls=[
                            ft.Text(f"{day} {month_name} {time_str}", size=11, color=t["text2"]),
                            ft.Text(ev["description"], size=13, weight=ft.FontWeight.W_500, color=t["text"]),
                            ft.Container(
                                content=ft.Text(display_type, size=10, color=color, weight=ft.FontWeight.W_600),
                                bgcolor=f"{color}20",
                                border_radius=99,
                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            ),
                        ],
                        spacing=3,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color="#ff5f6d",
                        icon_size=16,
                        on_click=lambda e: confirm_delete(ev["id"]),
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=t["surface"],
            border=ft.border.all(1, t["border"]),
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
        )

    def open_day(date_str):
        """Dialog to manage events for a specific day | Diálogo para gestionar eventos de un día"""
        day_events = queries.get_events_by_date(date_str)

        desc_field = ft.TextField(
            label=i18n.t("event_desc_label"),
            bgcolor=t["surface2"],
            border_color=t["border"],
            focused_border_color=t["accent"],
        )

        # Time selectors | Selectores de hora
        hours_dropdown = ft.Dropdown(
            label=i18n.t("hour_label"),
            options=[ft.dropdown.Option(str(h).zfill(2)) for h in range(1, 13)],
            value="09",
            width=100,
            height=40,
        )

        minutes_dropdown = ft.Dropdown(
            label=i18n.t("minute_label"),
            options=[ft.dropdown.Option(str(m).zfill(2)) for m in range(0, 60, 5)],
            value="00",
            width=100,
            height=40,
        )

        ampm_dropdown = ft.Dropdown(
            label=i18n.t("ampm_label"),
            options=[ft.dropdown.Option("AM"), ft.dropdown.Option("PM")],
            value="AM",
            width=100,
            height=40,
        )

        time_row = ft.Row(
            controls=[hours_dropdown, ft.Text(":", size=16), minutes_dropdown, ampm_dropdown],
            spacing=8,
        )

        type_map = {"Trabajo": i18n.t("type_work"), "Presupuesto": i18n.t("type_budget"), "Reunion": i18n.t("type_meeting"), "Personal": i18n.t("type_personal"), "Otro": i18n.t("type_other")}

        type_dropdown = ft.Dropdown(
            label=i18n.t("type_label"),
            bgcolor=t["surface2"],
            border_color=t["border"],
            focused_border_color=t["accent"],
            options=[ft.dropdown.Option(k, text=type_map[k]) for k in EVENT_TYPES.keys()],
            value="Trabajo",
        )

        existing = ft.Column(spacing=6)
        day_num   = date_str.split("-")[2]
        month_num = int(date_str.split("-")[1])

        def save_event(e):
            desc_field.error_text = None
            if not desc_field.value or not desc_field.value.strip():
                desc_field.error_text = i18n.t("required_field")
                desc_field.update() 
                return
            
            color = EVENT_TYPES.get(type_dropdown.value, "#f0a500")
            time_value = f"{hours_dropdown.value}:{minutes_dropdown.value} {ampm_dropdown.value}"
            queries.add_event(date_str, type_dropdown.value, desc_field.value.strip(), color, time_value)
            dlg.open = False
            page.update()
            build_calendar()
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(f"{day_num} {get_month_name_i18n(month_num)}"),
            actions=[
                ft.TextButton(i18n.t("cancel"), on_click=lambda e: setattr(dlg, 'open', False) or page.update()),
                ft.ElevatedButton(i18n.t("save_button"), bgcolor=t["accent"], color=t["bg"], on_click=save_event),
            ],
        )

        # Render existing events in the dialog | Renderiza eventos existentes en el diálogo
        for ev in day_events:
            display_type = type_map.get(ev["type"], ev["type"])
            existing.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=4, bgcolor=ev["color"], border_radius=99),
                        ft.Text(f"{ev['description']} {ev.get('time', '')}", size=13, color=t["text"], expand=True),
                        ft.Text(display_type, size=11, color=ev["color"]),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE, 
                            icon_color="#ff5f6d", 
                            icon_size=14, 
                            on_click=lambda e, eid=ev["id"]: confirm_delete(eid, is_dialog=True, current_dlg=dlg)
                        ),
                    ], spacing=8),
                    bgcolor=t["surface2"],
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                )
            )

        content_controls = []
        if day_events:
            content_controls.append(ft.Text(i18n.t("day_events_title"), size=11, color=t["text2"], weight=ft.FontWeight.W_600))
            content_controls.append(existing)
            content_controls.append(ft.Divider(color=t["border"]))
        content_controls.append(ft.Text(i18n.t("add_event_title"), size=11, color=t["text2"], weight=ft.FontWeight.W_600))
        content_controls.append(type_dropdown)
        content_controls.append(desc_field)
        content_controls.append(time_row)

        dlg.content = ft.Column(content_controls, spacing=10, tight=True, scroll=ft.ScrollMode.AUTO, height=350)
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    # Navigation logic | Lógica de navegación del calendario
    def prev_month(e):
        if state["month"] == 1:
            state["month"] = 12
            state["year"] -= 1
        else:
            state["month"] -= 1
        build_calendar()
        page.update()

    def next_month(e):
        if state["month"] == 12:
            state["month"] = 1
            state["year"] += 1
        else:
            state["month"] += 1
        build_calendar()
        page.update()

    def go_back(e):
        from views.home import HomeView
        page.controls.clear()
        page.add(HomeView(page))
        page.update()

    # --- TOPBAR ---
    topbar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=t["text2"], on_click=go_back),
                    ft.Text(i18n.t("calendar_title"), size=18, weight=ft.FontWeight.W_600, color=t["text"]),
                ]),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
        bgcolor=t["surface"],
        border=ft.border.only(bottom=ft.BorderSide(1, t["border"])),
    )

    # --- MAIN BODY ---
    month_nav = ft.Row(
        controls=[
            ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, icon_color=t["text2"], on_click=prev_month),
            month_label,
            ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, icon_color=t["text2"], on_click=next_month),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=16,
    )

    type_keys = {"Trabajo": "type_work", "Presupuesto": "type_budget", "Reunion": "type_meeting", "Personal": "type_personal", "Otro": "type_other"}
    legend = ft.Row(
        controls=[
            ft.Row([
                ft.Container(width=10, height=10, bgcolor=color, border_radius=99),
                ft.Text(i18n.t(type_keys[name]), size=11, color=t["text2"]),
            ], spacing=4)
            for name, color in EVENT_TYPES.items()
        ],
        spacing=12,
        wrap=True,
    )

    body = ft.Container(
        content=ft.Column(
            controls=[
                month_nav,
                legend,
                ft.Divider(color=t["border"], height=12),
                calendar_grid,
                ft.Divider(color=t["border"], height=16),
                ft.Text(i18n.t("month_events_title"), size=11, color=t["text2"], weight=ft.FontWeight.W_600),
                events_list,
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
        ),
        padding=24,
        expand=True,
    )

    # Initial build | Construcción inicial
    build_calendar()

    return ft.Column(
        controls=[topbar, body],
        spacing=0,
        expand=True,
    )