import flet as ft
from database import queries
from utils.theme import get_theme

def ClientsView(page: ft.Page):

    # Get current theme and translations | Obtener el tema actual y las traducciones
    t = get_theme(page.data["theme"])
    i18n = page.data["i18n"]
    # Internal state for search filter | Estado interno para el filtro de búsqueda
    state = {"search": ""}

    # ── NEW DIALOG FIELDS | NUEVOS CAMPOS PARA EL DIÁLOGO ──
    # Fields to capture new client data | Campos para capturar datos del nuevo cliente
    name_tf = ft.TextField(label=i18n.t("label_fullname"), border_color=t["accent"], focused_border_color=t["accent"])
    phone_tf = ft.TextField(label=i18n.t("label_phone"))
    email_tf = ft.TextField(label=i18n.t("label_email"))
    address_tf = ft.TextField(label=i18n.t("label_address"), multiline=True, min_lines=2)

    def get_filtered_clients():
        # Get clients and filter them by name or phone | Obtener clientes y filtrarlos por nombre o teléfono
        all_clients = queries.get_all_clients()
        search = state["search"].lower()
        if not search:
            return all_clients
        return [c for c in all_clients if
                search in (c["name"] or "").lower() or
                search in (c["phone"] or "").lower()]

    def get_client_stats(client_id):
        # Calculate totals from accepted estimates | Calcular totales de presupuestos aceptados
        conn = queries.get_connection()
        estimates = conn.execute(
            "SELECT * FROM items WHERE client_id = ? AND status IN ('accepted', 'archived_accepted')", (client_id,)
        ).fetchall()
        conn.close()
        total = sum(e["total"] or 0 for e in estimates)
        return len(estimates), total

    # Column to hold the client list items | Columna para contener los ítems de la lista de clientes
    clients_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)

    # ── SAVE NEW CLIENT LOGIC | LÓGICA PARA GUARDAR NUEVO CLIENTE ──
    def save_new_client(e):
        # Validate that name is not empty | Validar que el nombre no esté vacío
        if not name_tf.value:
            name_tf.error_text = i18n.t("name_required")
            name_tf.update()
            return
        
        # Save client to database | Guardar cliente en la base de datos
        queries.create_client(
            name=name_tf.value,
            phone=phone_tf.value,
            email=email_tf.value,
            address=address_tf.value
        )

        # Clear form and close dialog | Limpiar formulario y cerrar diálogo
        name_tf.value = ""
        phone_tf.value = ""
        email_tf.value = ""
        address_tf.value = ""
        add_dlg.open = False
        
        refresh_list()
        page.update()

    # ── NEW CLIENT DIALOG | DIÁLOGO DE NUEVO CLIENTE ──
    # UI component for adding a client | Componente de interfaz para añadir un cliente
    add_dlg = ft.AlertDialog(
        title=ft.Text(i18n.t("add_client_title"), weight=ft.FontWeight.BOLD),
        content=ft.Column([
            name_tf,
            phone_tf,
            email_tf,
            address_tf,
        ], tight=True, spacing=10, width=400),
        actions=[
            ft.TextButton(i18n.t("btn_cancel"), on_click=lambda _: setattr(add_dlg, "open", False) or page.update()),
            ft.ElevatedButton(i18n.t("btn_save_client"), bgcolor=t["accent"], color=t["bg"], on_click=save_new_client),
        ],
    )
    page.overlay.append(add_dlg)

    def build_client_card(client):
        # Build a visual card for each client | Construir una tarjeta visual para cada cliente
        count, total = get_client_stats(client["id"])

        def open_client(e):
            # Change view to client details | Cambiar vista a los detalles del cliente
            page.controls.clear()
            page.add(ClientDetailView(page, client["id"]))
            page.update()

        def confirm_delete(e):
            # Dialog to prevent accidental deletion | Diálogo para prevenir eliminación accidental
            confirm_field = ft.TextField(
                hint_text=i18n.t("delete_confirm_hint"),
                bgcolor=t["surface2"],
                border_color=t["border"],
                focused_border_color="#ff5f6d",
            )

            def do_delete(e):
                # Only delete if confirmation word is correct | Solo borrar si la palabra de confirmación es correcta
                if confirm_field.value != i18n.t("delete_confirm_word"):
                    confirm_field.border_color = "#ff5f6d"
                    confirm_field.hint_text = i18n.t("delete_confirm_error")
                    confirm_field.update()
                    return
                queries.delete_client(client["id"])
                dlg_confirm.open = False
                page.update()
                refresh_list()

            def cancel_delete(e):
                dlg_confirm.open = False
                page.update()

            dlg_confirm = ft.AlertDialog(
                title=ft.Text(i18n.t("delete_client_title")),
                content=ft.Column([
                    ft.Text(f"{i18n.t('delete_client_msg')} {client['name']} {i18n.t('delete_client_history')}", size=13, color=t["text2"]),
                    confirm_field,
                ], spacing=12, tight=True),
                actions=[
                    ft.TextButton(i18n.t("btn_cancel"), on_click=cancel_delete),
                    ft.ElevatedButton(i18n.t("delete_button"), bgcolor="#ff5f6d", color="white", on_click=do_delete),
                ],
            )
            page.overlay.append(dlg_confirm)
            dlg_confirm.open = True
            page.update()

        # Handle pluralization of labels | Manejar el plural de las etiquetas
        job_label = i18n.t("jobs_accepted") + (i18n.t("jobs_accepted_plural") if count != 1 else "")
        status_label = i18n.t("accepted_word") + (i18n.t("accepted_word_plural") if count != 1 else "")

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(client["name"], size=15, weight=ft.FontWeight.W_600, color=t["text"]),
                            ft.Text(client["phone"] or i18n.t("no_phone"), size=12, color=t["text2"]),
                            ft.Text(client["address"] or i18n.t("no_address"), size=12, color=t["text2"]),
                        ],
                        spacing=3,
                        expand=True,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(f"{count} {job_label} {status_label}", size=12, color=t["text2"]),
                            ft.Text(f"${total:,.2f}", size=14, weight=ft.FontWeight.BOLD, color=t["accent"]),
                        ],
                        spacing=3,
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color="#ff5f6d",
                        icon_size=18,
                        tooltip=i18n.t("delete_button"),
                        on_click=confirm_delete,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ARROW_FORWARD_IOS,
                        icon_size=16,
                        icon_color=t["text2"],
                        on_click=open_client,
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
            on_click=open_client,
        )

    def refresh_list():
        # Clear and update the UI list | Limpiar y actualizar la lista en la interfaz
        clients_list.controls.clear()
        clients = get_filtered_clients()
        if not clients:
            clients_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=64, color=t["text3"]),
                            ft.Text(i18n.t("no_clients"), size=18, color=t["text2"]),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    alignment=ft.alignment.Alignment.CENTER,
                    expand=True,
                    padding=40,
                )
            )
        else:
            for client in clients:
                clients_list.controls.append(build_client_card(client))
        try:
            clients_list.update()
        except:
            pass

    def on_search(e):
        # Update search state and refresh | Actualizar estado de búsqueda y refrescar
        state["search"] = e.control.value
        refresh_list()

    def go_back(e):
        # Navigation to home | Navegación al inicio
        from views.home import HomeView
        page.controls.clear()
        page.add(HomeView(page))
        page.update()

    # ── SEARCH BAR + NEW CLIENT BUTTON | BARRA DE BÚSQUEDA + BOTÓN NUEVO CLIENTE ──
    search_field = ft.TextField(
        hint_text=i18n.t("search_hint"),
        bgcolor=t["surface2"],
        border_color=t["border"],
        focused_border_color=t["accent"],
        prefix_icon=ft.Icons.SEARCH,
        on_change=on_search,
        expand=True,
        text_size=14,
    )

    search_section = ft.Row([
        search_field,
        ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=t["accent"],
            content=ft.Text(i18n.t("btn_new"), color=t["bg"], weight="bold"),
            width=100,
            height=40,
            on_click=lambda _: setattr(add_dlg, "open", True) or page.update()
        )
    ], spacing=10)

    # ── TOPBAR | BARRA SUPERIOR ──
    topbar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=t["text2"], on_click=go_back),
                    ft.Text(i18n.t("clients_title"), size=18, weight=ft.FontWeight.W_600, color=t["text"]),
                ]),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
        bgcolor=t["surface"],
        border=ft.border.only(bottom=ft.BorderSide(1, t["border"])),
    )

    # ── BODY | CUERPO ──
    body = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=search_section,
                    padding=ft.padding.symmetric(horizontal=24, vertical=12),
                ),
                ft.Container(
                    content=clients_list,
                    padding=ft.padding.symmetric(horizontal=24),
                    expand=True,
                )
            ],
        ),
        expand=True,
    )

    refresh_list()

    return ft.Column(
        controls=[topbar, body],
        spacing=0,
        expand=True,
    )


def ClientDetailView(page: ft.Page, client_id: int):

    t = get_theme(page.data["theme"])
    i18n = page.data["i18n"]
    client = queries.get_client(client_id)

    # Load client estimates from DB | Cargar presupuestos del cliente desde la DB
    conn = queries.get_connection()
    estimates = conn.execute(
        "SELECT * FROM items WHERE client_id = ? ORDER BY created_at DESC", (client_id,)
    ).fetchall()
    conn.close()

    def go_back(e):
        page.controls.clear()
        page.add(ClientsView(page))
        page.update()

    def show_job_details(estimate_id):
        # Fetch and display estimate details | Buscar y mostrar detalles del presupuesto
        est, items = queries.get_full_estimate_details(estimate_id)
        
        items_list = ft.Column(spacing=10, tight=True)
        for item in items:
            items_list.controls.append(
                ft.Row([
                    ft.Column([
                        ft.Text(item["description"], size=14, weight="w500", color=t["text"]),
                        ft.Text(f"{item['quantity']} {item['unit']} x ${item['unit_price']:,.2f}", 
                                size=12, color=t["text2"]),
                    ], expand=True, spacing=2),
                    ft.Text(f"${(item['quantity'] * item['unit_price']):,.2f}", 
                            size=14, weight="bold", color=t["text"]),
                ])
            )

        details_dlg = ft.AlertDialog(
            title=ft.Text(f"{i18n.t('client_detail_title')} {est['estimate_number']}", weight="bold"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(est["title"] or i18n.t("no_title"), size=16, weight="bold", color=t["accent"]),
                    ft.Divider(color=t["border"]),
                    items_list,
                    ft.Divider(color=t["border"]),
                    ft.Row([
                        ft.Text(i18n.t("total_upper"), weight="bold"),
                        ft.Text(f"${est['total']:,.2f}", size=18, weight="bold", color=t["accent"])
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ], tight=True, scroll=ft.ScrollMode.AUTO),
                width=400
            ),
            actions=[
                ft.TextButton(i18n.t("btn_close"), on_click=lambda _: setattr(details_dlg, "open", False) or page.update())
            ]
        )
        page.overlay.append(details_dlg)
        details_dlg.open = True
        page.update()
        

    def open_edit_dialog(e):
        # Setup fields with current values | Configurar campos con valores actuales
        name_field = ft.TextField(label=i18n.t("label_fullname"), value=client["name"], bgcolor=t["surface2"], border_color=t["border"])
        phone_field = ft.TextField(label=i18n.t("label_phone"), value=client["phone"], bgcolor=t["surface2"], border_color=t["border"])
        email_field = ft.TextField(label=i18n.t("label_email"), value=client["email"], bgcolor=t["surface2"], border_color=t["border"])
        address_field = ft.TextField(label=i18n.t("label_address"), value=client["address"], bgcolor=t["surface2"], border_color=t["border"], multiline=True)

        def save_edit(e):
            # Update info in database | Actualizar info en la base de datos
            queries.update_client(
                client_id,
                name_field.value,
                phone_field.value,
                email_field.value,
                address_field.value
            )
            dlg_edit.open = False
            page.controls.clear()
            page.add(ClientDetailView(page, client_id))
            page.update()

        # Component for editing client info | Componente para editar info del cliente
        dlg_edit = ft.AlertDialog(
            title=ft.Text(i18n.t("edit_client_title"), weight=ft.FontWeight.BOLD),
            content=ft.Column([
                name_field,
                phone_field,
                email_field,
                address_field,
            ], spacing=10, tight=True, width=400),
            actions=[
                ft.TextButton(i18n.t("btn_cancel"), on_click=lambda _: setattr(dlg_edit, "open", False) or page.update()),
                ft.ElevatedButton(i18n.t("btn_save_changes"), bgcolor=t["accent"], color="white", on_click=save_edit),
            ],
        )
        page.overlay.append(dlg_edit)
        dlg_edit.open = True
        page.update()

    # ── DETAIL TOPBAR | BARRA SUPERIOR DE DETALLE ──
    topbar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=t["text2"], on_click=go_back),
                    ft.Text(client["name"] if client else i18n.t("clients_title"), size=18, weight=ft.FontWeight.W_600, color=t["text"]),
                ]),
                ft.IconButton(
                    icon=ft.Icons.EDIT_OUTLINED,
                    icon_color=t["accent"],
                    tooltip=i18n.t("edit_client_title"),
                    on_click=open_edit_dialog
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
        bgcolor=t["surface"],
        border=ft.border.only(bottom=ft.BorderSide(1, t["border"])),
    )

    # ── INFO CARD | TARJETA DE INFORMACIÓN ──
    info_card = ft.Container(
        content=ft.Row( 
            controls=[
                ft.Column([
                    ft.Text(i18n.t("label_phone"), size=11, color=t["text2"]),
                    ft.Text(client["phone"] or i18n.t("no_phone"), size=13, color=t["text"]),
                ], spacing=4),
                ft.Column([
                    ft.Text(i18n.t("label_email"), size=11, color=t["text2"]),
                    ft.Text(client["email"] or i18n.t("no_email"), size=13, color=t["text"]),
                ], spacing=4),
                ft.Column([
                    ft.Text(i18n.t("label_address"), size=11, color=t["text2"]),
                    ft.Text(client["address"] or i18n.t("no_address"), size=13, color=t["text"]),
                ], spacing=4),
            ],
            spacing=40,
        ),
        bgcolor=t["surface"],
        border=ft.border.all(1, t["border"]),
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
    )

    def estimate_row(est):
        # Configure status colors and labels | Configurar colores y etiquetas de estado
        status_colors = {
            "draft": ("#555870", i18n.t("status_draft")),
            "sent": ("#4f8ef7", i18n.t("status_sent")),
            "accepted": ("#22c97a", i18n.t("status_accepted")),
            "rejected": ("#ff5f6d", i18n.t("status_rejected")),
            "archived_accepted": ("#22c97a", i18n.t("status_accepted")),
        }
        color, label = status_colors.get(est["status"], ("#555870", i18n.t("status_draft")))

        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(est["estimate_number"], size=12, color=t["accent"]),
                    ft.Text(str(est["title"] or est["description"] or i18n.t("no_title")), size=14, weight=ft.FontWeight.W_500, color=t["text"]),
                    ft.Text(est["created_at"], size=11, color=t["text2"]),
                ], spacing=3, expand=True),
                ft.Column([
                    ft.Container(
                        content=ft.Text(label, size=10, color=color, weight=ft.FontWeight.W_600),
                        bgcolor=f"{color}20", border_radius=99, padding=ft.padding.symmetric(horizontal=8, vertical=3),
                    ),
                    ft.Text(f"${est['total']:,.2f}", size=13, weight=ft.FontWeight.BOLD, color=t["text"]),
                ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.END),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=t["surface"],
            border=ft.border.all(1, t["border"]),
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            ink=True,
            on_click=lambda _: show_job_details(est["id"])
        )

    # ── WORK HISTORY LIST | LISTA DE HISTORIAL DE TRABAJO ──
    work_history = ft.Column(
        controls=[estimate_row(e) for e in estimates] if estimates else [
            ft.Text(i18n.t("no_works"), size=13, color=t["text2"])
        ],
        spacing=8,
    )

    # ── DETAIL BODY | CUERPO DE DETALLE ──
    body = ft.Container(
        content=ft.Column([
            info_card,
            ft.Text(i18n.t("work_history_title"), size=11, color=t["text2"], weight=ft.FontWeight.W_600),
            work_history,
        ], scroll=ft.ScrollMode.AUTO, spacing=16),
        padding=24,
        expand=True,
    )

    return ft.Column(controls=[topbar, body], spacing=0, expand=True)