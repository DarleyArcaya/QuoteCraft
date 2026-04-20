import flet as ft
from database import queries
from views.estimate_form import EstimateForm
from services.estimate_pdf import generate_pdf
import webbrowser
import os
import sys
import subprocess
from views.finances import FinancesView
from views.settings import SettingsView
from views.clients import ClientsView
from views.calendar_view import CalendarView
from utils.theme import get_theme

# [CHANGE] Cross-platform file opener function — replaces os.startfile which is Windows-only.
# Windows → os.startfile | macOS → open | Linux → xdg-open
# [CAMBIO] Función multiplataforma para abrir archivos — reemplaza os.startfile que es solo de Windows.
def open_file_cross_platform(path):
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.run(["open", path])
    else:
        subprocess.run(["xdg-open", path])

def HomeView(page: ft.Page):
    # Load visual theme and internationalization (i18n) | Carga de tema visual e internacionalización (i18n)
    t = get_theme(page.data["theme"])
    i18n = page.data["i18n"]
    state = {"search": ""}

    # Top bar construction: Logo and main navigation | Construcción de la barra superior: Logo y navegación principal
    def build_topbar():
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("QuoteCraft", size=22, weight=ft.FontWeight.BOLD, color=t["accent"]),
                    ft.Row([
                        # Button to create a new estimate | Botón para crear un nuevo presupuesto
                        ft.ElevatedButton(
                            i18n.t("new_estimate"),
                            icon=ft.Icons.ADD,
                            bgcolor=t["accent"],
                            color=t["bg"],
                            on_click=lambda e: (
                                page.controls.clear(),
                                page.add(EstimateForm(page)),
                                page.update()
                            )
                        ),
                        # Access to Finances view | Acceso a la vista de Finanzas
                        ft.IconButton(
                            icon=ft.Icons.ACCOUNT_BALANCE_WALLET,
                            icon_color=t["text2"],
                            tooltip=i18n.t("finances"),
                            on_click=lambda e: (
                                page.controls.clear(),
                                page.add(FinancesView(page)),
                                page.update()
                            )
                        ),
                        # Access to Clients management | Acceso a la gestión de Clientes
                        ft.IconButton(
                            icon=ft.Icons.PEOPLE,
                            icon_color=t["text2"],
                            tooltip=i18n.t("clients"),
                            on_click=lambda e: (
                                page.controls.clear(),
                                page.add(ClientsView(page)),
                                page.update()
                            )
                        ),
                        # Access to Calendar | Acceso al Calendario
                        ft.IconButton(
                            icon=ft.Icons.CALENDAR_MONTH,
                            icon_color=t["text2"],
                            tooltip=i18n.t("calendar"),
                            on_click=lambda e: (
                                page.controls.clear(),
                                page.add(CalendarView(page)),
                                page.update()
                            )
                        ),
                        # App settings | Configuración de la aplicación
                        ft.IconButton(
                            icon=ft.Icons.SETTINGS,
                            icon_color=t["text2"],
                            tooltip=i18n.t("settings"),
                            on_click=lambda e: (
                                page.controls.clear(),
                                page.add(SettingsView(page)),
                                page.update()
                            )
                        ),
                    ]),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            bgcolor=t["surface"],
            border=ft.border.only(bottom=ft.BorderSide(1, t["border"])),
        )

    def build_update_banner():
        if not page.data.get("update_available"):
            return ft.Container(visible=False)

        version      = page.data.get("update_version", "")
        download_url = page.data.get("update_url", "")
        banner_ref   = ft.Ref[ft.Container]()

        def open_download(e):
            webbrowser.open(download_url)

        def dismiss_banner(e):
            banner_ref.current.visible = False
            banner_ref.current.update()

        return ft.Container(
            ref=banner_ref,
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SYSTEM_UPDATE_ALT, color="#0d0f14", size=18),
                    ft.Text(
                        f"Nueva versión disponible: v{version}",
                        color="#0d0f14",
                        size=13,
                        weight=ft.FontWeight.W_600,
                        expand=True,
                    ),
                    ft.TextButton(
                        "Descargar",
                        on_click=open_download,
                        style=ft.ButtonStyle(color="#0d0f14"),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_color="#0d0f14",
                        icon_size=16,
                        tooltip="Cerrar",
                        on_click=dismiss_banner,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#f0a500",
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            visible=True,
        )

    # Filtering logic for the search bar | Lógica de filtrado para la barra de búsqueda
    def get_filtered_estimates():
        all_estimates = queries.get_all_estimates()
        q = state["search"].lower()
        if not q:
            return all_estimates
        return [e for e in all_estimates if
                q in (e["title"] or "").lower() or
                q in (e["description"] or "").lower() or
                q in (e["estimate_number"] or "").lower()]

    # Visual card generation for each estimate | Generación de la tarjeta visual para cada presupuesto
    def estimate_card(estimate):
        status_colors = {
            "draft":     ("#555870", i18n.t("status_draft")),
            "sent":      ("#4f8ef7", i18n.t("status_sent")),
            "accepted":  ("#22c97a", i18n.t("status_accepted")),
            "rejected":  ("#ff5f6d", i18n.t("status_rejected")),
        }
        color, label = status_colors.get(estimate["status"], ("#555870", i18n.t("status_draft")))

        def refresh_home():
            page.controls.clear()
            page.add(HomeView(page))
            page.update()

        def confirm_delete(e):
            confirm_field = ft.TextField(
                hint_text=i18n.t("DELETE_WORD"),
                bgcolor=t["surface2"],
                border_color=t["border"],
                focused_border_color="#ff5f6d",
            )

            def do_delete(e):
                if confirm_field.value != i18n.t("DELETE_WORD"):
                    confirm_field.hint_text = i18n.t("delete_confirm_error")
                    confirm_field.update()
                    return
                queries.archive_estimate(estimate["id"])
                dlg_confirm.open = False
                page.update()
                refresh_home()

            def cancel_delete(e):
                dlg_confirm.open = False
                page.update()

            dlg_confirm = ft.AlertDialog(
                title=ft.Text(i18n.t("delete_title")),
                content=ft.Column([
                    ft.Text(i18n.t("delete_estimate_msg").format(num=estimate['estimate_number']),
                            size=13, color=t["text2"]),
                    confirm_field,
                ], spacing=12, tight=True),
                actions=[
                    ft.TextButton(i18n.t("cancel"), on_click=cancel_delete),
                    ft.ElevatedButton(i18n.t("delete"), bgcolor="#ff5f6d", color="white", on_click=do_delete),
                ],
            )
            page.overlay.append(dlg_confirm)
            confirm_field.focus()
            dlg_confirm.open = True
            page.update()

        def change_status(e):
            def set_status(status):
                dlg.open = False
                page.update()
                queries.update_estimate_status(estimate["id"], status)

                if status == "accepted":
                    def add_to_income(e):
                        title_text = str(estimate["title"] or estimate["description"] or i18n.t("no_title"))
                        queries.add_income(
                            description=f"{estimate['estimate_number']} - {title_text}",
                            amount=estimate["total"],
                            date=estimate["created_at"],
                        )
                        dlg2.open = False
                        page.update()
                        refresh_home()

                    def skip(e):
                        dlg2.open = False
                        page.update()
                        refresh_home()

                    dlg2 = ft.AlertDialog(
                        title=ft.Text(i18n.t("accepted_title")),
                        content=ft.Text(i18n.t("add_to_income_question").format(amount=estimate['total'])),
                        actions=[
                            ft.TextButton(i18n.t("not_now"), on_click=skip),
                            ft.ElevatedButton(i18n.t("yes_add"), bgcolor="#22c97a", color="white", on_click=add_to_income),
                        ],
                    )
                    page.overlay.append(dlg2)
                    dlg2.open = True
                    page.update()
                else:
                    refresh_home()

            def cancel(e):
                dlg.open = False
                page.update()

            dlg = ft.AlertDialog(
                title=ft.Text(i18n.t("change_status")),
                content=ft.Column([
                    ft.TextButton(i18n.t("status_draft"),    on_click=lambda e: set_status("draft")),
                    ft.TextButton(i18n.t("status_sent"),     on_click=lambda e: set_status("sent")),
                    ft.TextButton(i18n.t("status_accepted"), on_click=lambda e: set_status("accepted")),
                    ft.TextButton(i18n.t("status_rejected"), on_click=lambda e: set_status("rejected")),
                ], tight=True, spacing=4),
                actions=[ft.TextButton(i18n.t("cancel"), on_click=cancel)],
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()

        def open_estimate(e):
            path = generate_pdf(estimate["id"])

            def open_pdf_file(e):
                dlg.open = False
                page.update()
                # [CHANGE] Replaced os.startfile with cross-platform opener
                # [CAMBIO] Reemplazado os.startfile con abridor multiplataforma
                open_file_cross_platform(path)

            def send_whatsapp(e):
                dlg.open = False
                page.update()
                client = queries.get_client(estimate["client_id"])
                phone = client["phone"].replace("-", "").replace(" ", "") if client else ""
                msg = i18n.t("whatsapp_msg").format(num=estimate['estimate_number'], total=estimate['total'])
                webbrowser.open(f"https://wa.me/{phone}?text={msg}")

            def cancel(e):
                dlg.open = False
                page.update()

            dlg = ft.AlertDialog(
                title=ft.Text(f"{i18n.t('send')} {estimate['estimate_number']}"),
                content=ft.Column([
                    ft.Text(f"Total: ${estimate['total']:,.2f}", color=t["accent"], size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(i18n.t("send_method_question"), size=13, color=t["text2"]),
                ], tight=True, spacing=8),
                actions=[
                    ft.TextButton(i18n.t("open_pdf"), on_click=open_pdf_file),
                    ft.TextButton("WhatsApp", on_click=send_whatsapp),
                    ft.TextButton(i18n.t("cancel"), on_click=cancel),
                ],
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(estimate["estimate_number"], size=13, color=t["accent"]),
                            ft.Text(str(estimate["title"] or estimate["description"] or i18n.t("no_title")),
                                    size=15, weight=ft.FontWeight.W_500, color=t["text"]),
                            ft.Text(estimate["created_at"], size=12, color=t["text2"]),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Text(i18n.t("edit"), size=11, color=t["accent"], weight=ft.FontWeight.W_600),
                        bgcolor=f"{t['accent']}20",
                        border_radius=99,
                        padding=ft.padding.symmetric(horizontal=12, vertical=4),
                        on_click=lambda e, eid=estimate["id"]: (
                            page.controls.clear(),
                            page.add(EstimateForm(page, estimate_id=eid)),
                            page.update()
                        ),
                        ink=True,
                    ),
                    ft.Container(
                        content=ft.Text(label, size=11, color=color, weight=ft.FontWeight.W_600),
                        bgcolor=f"{color}20",
                        border_radius=99,
                        padding=ft.padding.symmetric(horizontal=12, vertical=4),
                        on_click=change_status,
                        ink=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color="#ff5f6d",
                        icon_size=18,
                        tooltip=i18n.t("delete"),
                        on_click=confirm_delete,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ARROW_FORWARD_IOS,
                        icon_size=16,
                        icon_color=t["text3"],
                        on_click=open_estimate,
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=t["surface"],
            border=ft.border.all(1, t["border"]),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=20, vertical=16),
            ink=True,
        )

    initial_estimates = get_filtered_estimates()
    estimates_list = ft.Column(
        controls=[estimate_card(e) for e in initial_estimates],
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
    )

    def on_search(e):
        state["search"] = e.control.value
        filtered = get_filtered_estimates()
        estimates_list.controls.clear()
        for est in filtered:
            estimates_list.controls.append(estimate_card(est))
        estimates_list.update()

    search_field = ft.TextField(
        hint_text=i18n.t("search_hint"),
        bgcolor=t["surface2"],
        border_color=t["border"],
        focused_border_color=t["accent"],
        prefix_icon=ft.Icons.SEARCH,
        on_change=on_search,
    )

    def build_body():
        all_estimates = queries.get_all_estimates()

        if not all_estimates:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, size=64, color=t["text3"]),
                        ft.Text(i18n.t("no_estimates_yet"), size=18, color=t["text2"]),
                        ft.Text(i18n.t("press_new_to_start"), size=13, color=t["text3"]),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
                alignment=ft.alignment.Alignment.CENTER,
                expand=True,
            )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(content=search_field, padding=ft.padding.only(bottom=16)),
                    estimates_list,
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=24,
            expand=True,
        )

    return ft.Column(
        controls=[
            build_topbar(),
            build_update_banner(),
            build_body(),
        ],
        spacing=0,
        expand=True,
    )