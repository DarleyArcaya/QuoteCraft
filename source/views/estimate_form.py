import flet as ft
from database import queries
from datetime import datetime
from utils.theme import get_theme

def EstimateForm(page: ft.Page, estimate_id=None):

    # Load theme and internationalization | Cargar tema e internacionalización
    t = get_theme(page.data["theme"])
    i18n = page.data["i18n"]

    # Local state for items and selected client | Estado local para items y cliente seleccionado
    items = []
    selected_client_id = {"id": None}

    # PDF Language selector with descriptive label | Selector de idioma del PDF con label descriptivo
    pdf_lang = ft.Dropdown(
        label=i18n.t("label_pdf_lang"), 
        options=[
            ft.dropdown.Option("es", "Español"),
            ft.dropdown.Option("en", "English"),
        ],
        value="es",
        bgcolor=t["surface2"],
        border_color=t["border"],
        focused_border_color=t["accent"],
        width=140, 
        height=45,
        text_size=14,
        content_padding=ft.padding.only(left=10, bottom=10),
    )

    # Client information fields | Campos de información del cliente
    client_name    = ft.TextField(label=i18n.t("label_client_name"), bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"])
    client_phone   = ft.TextField(label=i18n.t("label_phone"), bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"])
    client_email   = ft.TextField(label=i18n.t("label_email"), bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"])
    client_address = ft.TextField(label=i18n.t("label_address"), bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"])

    # Estimate fields (Title, Description, Notes) | Campos del presupuesto (Título, Descripción, Notas)
    project_title = ft.TextField(
        label=i18n.t("label_project_title"), 
        bgcolor=t["surface2"], 
        border_color=t["border"], 
        focused_border_color=t["accent"],
        width=250 
    )
    description   = ft.TextField(label=i18n.t("label_desc_gen"), bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"], multiline=True, min_lines=3, max_lines=15)
    notes         = ft.TextField(label=i18n.t("label_notes"), bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"], multiline=True, min_lines=2, max_lines=4)

    # Date field logic | Lógica del campo de fecha
    valid_until_label = ft.Text(i18n.t("date_no_limit"), size=13, color=t["text2"])
    valid_until_value = {"date": ""}

    def on_date_picked(e):
        d = date_picker.value
        if d:
            formatted = f"{d.year}-{str(d.month).zfill(2)}-{str(d.day).zfill(2)}"
            valid_until_value["date"] = formatted
            valid_until_label.value = f"{i18n.t('label_valid_until')}: {formatted}"
        else:
            valid_until_value["date"] = ""
            valid_until_label.value = i18n.t("date_no_limit")
        page.update()

    # Date picker configuration | Configuración del selector de fecha
    date_picker = ft.DatePicker(
        on_change=on_date_picked,
        help_text=i18n.t("datepicker_help"),
    )
    page.overlay.append(date_picker)

    def open_date_picker(e):
        date_picker.open = True
        page.update()

    def set_unlimited(e):
        valid_until_value["date"] = "Sin limite"
        valid_until_label.value = i18n.t("date_unlimited")
        page.update()

    # Layout for expiration date | Diseño para la fecha de vencimiento
    valid_until_row = ft.Row([
        ft.ElevatedButton(
            i18n.t("btn_select_date"),
            icon=ft.Icons.CALENDAR_TODAY,
            bgcolor=t["surface2"],
            color=t["accent"],
            on_click=open_date_picker,
        ),
        ft.TextButton(
            i18n.t("btn_unlimited"),
            style=ft.ButtonStyle(color=t["text2"]),
            on_click=set_unlimited,
        ),
        valid_until_label,
    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    # Summary fields (Tax, Subtotal, Total) | Campos de resumen (Impuestos, Subtotal, Total)
    items_column   = ft.Column(spacing=8)
    tax_field      = ft.TextField(label=i18n.t("label_tax"), value="0.0", width=100, bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"], on_change=lambda e: calc_total())
    subtotal_field = ft.Text(f"{i18n.t('subtotal')}: $0.00", size=13, color=t["text2"])
    tax_text       = ft.Text(f"{i18n.t('tax')}: $0.00", size=13, color=t["text2"])
    total_text     = ft.Text(f"{i18n.t('total')}: $0.00", size=16, weight=ft.FontWeight.BOLD, color=t["accent"])

    # Label for currently selected client | Label para el cliente seleccionado actualmente
    selected_client_label = ft.Text("", size=12, color="#22c97a")

    # Search and select existing client dialog | Diálogo para buscar y seleccionar cliente existente
    def show_client_search(e):
        all_clients = queries.get_all_clients()
        search_input = ft.TextField(
            hint_text=i18n.t("search_client_hint"),
            bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"],
        )
        results_column = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=200)

        def build_result_controls(clients):
            controls = []
            for c in clients:
                def select_client(e, client=c):
                    selected_client_id["id"] = client["id"]
                    client_name.value    = client["name"] or ""
                    client_phone.value   = client["phone"] or ""
                    client_email.value   = client["email"] or ""
                    client_address.value = client["address"] or ""
                    selected_client_label.value = f"{i18n.t('client_selected')}: {client['name']}"
                    dlg.open = False
                    page.update()

                controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(c["name"], size=13, weight=ft.FontWeight.W_500, color=t["text"]),
                                ft.Text(c["phone"] or "", size=11, color=t["text2"]),
                            ], spacing=2, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.ARROW_FORWARD_IOS,
                                icon_size=14,
                                icon_color=t["text2"],
                                on_click=lambda e, client=c: select_client(e, client)
                            ),
                        ]),
                        bgcolor=t["surface2"],
                        border=ft.border.all(1, t["border"]),
                        border_radius=8,
                        padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        on_click=lambda e, client=c: select_client(e, client),
                        ink=True,
                    )
                )
            return controls

        results_column.controls = build_result_controls(all_clients)

        def on_search(e):
            q = search_input.value.lower()
            filtered = [c for c in all_clients if
                        q in (c["name"] or "").lower() or
                        q in (c["phone"] or "").lower()]
            results_column.controls = build_result_controls(filtered)
            results_column.update()

        search_input.on_change = on_search

        def cancel(e):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(i18n.t("select_existing_client")),
            content=ft.Column([search_input, results_column], spacing=10, tight=True),
            actions=[ft.TextButton(i18n.t("cancel"), on_click=cancel)],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    # Calculate totals logic | Lógica de cálculo de totales
    def calc_total():
        subtotal = 0.0
        for item in items:
            try:
                qty = float(item["qty"].value)
                price = float(item["price"].value)
                subtotal += qty * price
            except ValueError:
                pass
        try:
            tax_rate = float(tax_field.value) if tax_field.value else 0.0
        except ValueError:
            tax_rate = 0.0
        tax_amount = subtotal * (tax_rate / 100)
        total = subtotal + tax_amount
        subtotal_field.value = f"{i18n.t('subtotal')}: ${subtotal:,.2f}"
        tax_text.value       = f"{i18n.t('tax')}: ${tax_amount:,.2f}"
        total_text.value     = f"{i18n.t('total')}: ${total:,.2f}"
        page.update()

    # Build individual item row for the table | Construir fila de item individual para la tabla
    def build_item_row(item_data=None):
        cat = ft.Dropdown(
            options=[
                ft.dropdown.Option("Mano de obra", text=i18n.t("cat_labor")), 
                ft.dropdown.Option("Materiales", text=i18n.t("cat_materials")), 
                ft.dropdown.Option("Equipo", text=i18n.t("cat_equipment")), 
                ft.dropdown.Option("Otros", text=i18n.t("cat_others"))
            ],
            value=item_data["category"] if item_data else "Mano de obra",
            bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"], width=150,
        )
        desc  = ft.TextField(hint_text=i18n.t("table_desc"), value=item_data["description"] if item_data else "", bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"], expand=True)
        qty   = ft.TextField(hint_text=i18n.t("table_qty"), value=str(item_data["quantity"]) if item_data else "1", bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"], width=70, text_align=ft.TextAlign.CENTER, on_change=lambda e: calc_total())
        unit  = ft.Dropdown(
            options=[ft.dropdown.Option("hr"), ft.dropdown.Option("dia"), ft.dropdown.Option("unidad"), ft.dropdown.Option("pie2"), ft.dropdown.Option("m2"), ft.dropdown.Option("galon"), ft.dropdown.Option("lb")],
            value=item_data["unit"] if item_data else "hr",
            bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"], width=100,
        )
        price = ft.TextField(hint_text=i18n.t("table_price"), value=str(item_data["unit_price"]) if item_data else "", bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"], width=90, text_align=ft.TextAlign.RIGHT, on_change=lambda e: calc_total())

        row_ref = ft.Ref[ft.Row]()

        def delete_row(e):
            items.remove(row_data)
            items_column.controls.remove(row_ref.current)
            items_column.update()

        row_data = {"cat": cat, "desc": desc, "qty": qty, "unit": unit, "price": price}
        items.append(row_data)

        row = ft.Row(
            ref=row_ref,
            controls=[cat, desc, qty, unit, price, ft.IconButton(icon=ft.Icons.CLOSE, icon_color=t["text2"], icon_size=16, on_click=delete_row)],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        return row

    def add_item(e):
        row = build_item_row()
        items_column.controls.append(row)
        items_column.update()

    # Save estimate logic | Lógica para guardar el presupuesto
    def save(e):
        # Validations | Validaciones
        errors = []

        if not client_name.value.strip() and not selected_client_id["id"]:
            client_name.border_color = "#ff5f6d"
            client_name.update()
            errors.append(i18n.t("msg_req_client"))
        else:
            client_name.border_color = t["border"]
            client_name.update()

        if not project_title.value.strip():
            project_title.border_color = "#ff5f6d"
            project_title.update()
            errors.append(i18n.t("msg_req_title"))
        else:
            project_title.border_color = t["border"]
            project_title.update()

        if not items:
            errors.append(i18n.t("msg_req_items"))

        if errors:
            snack = ft.SnackBar(
                content=ft.Text(errors[0], color="white"),
                bgcolor="#ff5f6d",
                duration=3000,
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()
            return

        # Handle Client: Search or Create | Manejar Cliente: Buscar o Crear
        if selected_client_id["id"]:
            client_id = selected_client_id["id"]
        else:
            typed_name = client_name.value.strip()
            all_clients = queries.get_all_clients()
            found_client = next((c for c in all_clients if c["name"].lower() == typed_name.lower()), None)

            if found_client:
                client_id = found_client["id"]
            else:
                queries.create_client(client_name.value, client_phone.value, client_email.value, client_address.value)
                client_id = queries.get_all_clients()[-1]["id"]

        subtotal = 0.0
        for item in items:
            try:
                q = float(item["qty"].value or 0)
                p = float(item["price"].value or 0)
                subtotal += q * p
            except ValueError:
                pass
        try:
            tax_rate = float(tax_field.value or 0) / 100
        except ValueError:
            tax_rate = 0.0
        total = subtotal + (subtotal * tax_rate)

        # Update or Create in DB | Actualizar o Crear en DB
        if estimate_id:
            queries.update_estimate(
                estimate_id=estimate_id,
                client_id=client_id,
                title=project_title.value,
                description=description.value,
                notes=notes.value,
                valid_until=valid_until_value["date"],
                language=pdf_lang.value,
            )
            queries.delete_all_items(estimate_id)
            est_id = estimate_id
            action_msg = i18n.t("msg_updated")
        else:
            est_id = queries.create_estimate(
                client_id=client_id,
                title=project_title.value,
                description=description.value,
                notes=notes.value,
                valid_until=valid_until_value["date"],
                tax_rate=tax_rate,
                subtotal=subtotal,
                total=total,
                language=pdf_lang.value,
            )
            action_msg = i18n.t("msg_saved")

        # Save individual items | Guardar items individuales
        for item in items:
            try:
                queries.add_item(
                    estimate_id=est_id, category=item["cat"].value,
                    description=item["desc"].value, quantity=float(item["qty"].value or 0),
                    unit=item["unit"].value, unit_price=float(item["price"].value or 0),
                )
            except ValueError:
                pass

        from views.home import HomeView
        snack = ft.SnackBar(
            content=ft.Text(action_msg, color="white"),
            bgcolor="#22c97a",
            duration=2000,
        )
        page.overlay.append(snack)
        snack.open = True
        page.controls.clear()
        page.add(HomeView(page))
        page.update()
        
    def go_back(e):
        from views.home import HomeView
        page.controls.clear()
        page.add(HomeView(page))
        page.update()

    # Load data if in edit mode | Cargar datos si es modo edición
    if estimate_id:
        est      = queries.get_estimate(estimate_id)
        client   = queries.get_client(est["client_id"]) if est else None
        items_db = queries.get_items(estimate_id)

        if est and client:
            selected_client_id["id"] = client["id"]
            client_name.value    = client["name"] or ""
            client_phone.value   = client["phone"] or ""
            client_email.value   = client["email"] or ""
            client_address.value = client["address"] or ""
            project_title.value  = est["title"] or ""
            description.value    = est["description"] or ""
            notes.value          = est["notes"] or ""
            tax_field.value      = str((est["tax_rate"] or 0) * 100)
            selected_client_label.value = f"{i18n.t('client_selected')}: {client['name']}"
            pdf_lang.value       = est.get("language", "es")

            saved_date = est["valid_until"] or ""
            valid_until_value["date"] = saved_date
            if saved_date == "Sin limite":
                valid_until_label.value = i18n.t("date_unlimited")
            elif saved_date:
                valid_until_label.value = f"{i18n.t('label_valid_until')}: {saved_date}"

            for item_data in items_db:
                row = build_item_row(item_data)
                items_column.controls.append(row)

    # Interface (Topbar with language and save) | Interfaz (Topbar con idioma y guardar)
    topbar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=t["text2"], on_click=go_back),
                    ft.Text(i18n.t("est_new") if not estimate_id else i18n.t("est_edit"), size=18, weight=ft.FontWeight.W_600, color=t["text"]),
                ]),
                ft.Row([
                    pdf_lang,
                    ft.ElevatedButton(i18n.t("save_button"), bgcolor=t["accent"], color=t["bg"], on_click=save)
                ], spacing=12)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
        bgcolor=t["surface"],
        border=ft.border.only(bottom=ft.BorderSide(1, t["border"])),
    )

    # Main form body | Cuerpo principal del formulario
    body = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(i18n.t("client_section"), size=11, color=t["text2"], weight=ft.FontWeight.W_600),
                ft.Row([
                    ft.TextButton(
                        i18n.t("select_existing_client"),
                        on_click=show_client_search,
                        style=ft.ButtonStyle(color=t["accent"]),
                    ),
                    selected_client_label,
                ]),
                ft.Row([client_name, client_phone], spacing=12),
                ft.Row([client_email, client_address], spacing=12),
                ft.Divider(color=t["border"], height=24),
                ft.Text(i18n.t("project_section"), size=11, color=t["text2"], weight=ft.FontWeight.W_600),
                
                project_title,
                
                description,
                ft.Text(i18n.t("label_valid_until"), size=11, color=t["text2"], weight=ft.FontWeight.W_600),
                valid_until_row,
                ft.Divider(color=t["border"], height=24),
                ft.Text(i18n.t("items_section"), size=11, color=t["text2"], weight=ft.FontWeight.W_600),
                ft.Row(controls=[
                    ft.Text(i18n.t("table_cat"), size=11, color=t["text3"], width=150),
                    ft.Text(i18n.t("table_desc"), size=11, color=t["text3"], expand=True),
                    ft.Text(i18n.t("table_qty"), size=11, color=t["text3"], width=70),
                    ft.Text(i18n.t("table_unit"), size=11, color=t["text3"], width=100),
                    ft.Text(i18n.t("table_price"), size=11, color=t["text3"], width=90),
                    ft.Container(width=40),
                ]),
                items_column,
                ft.TextButton(i18n.t("btn_add_line"), on_click=add_item, style=ft.ButtonStyle(color=t["accent"])),
                ft.Divider(color=t["border"], height=24),
                ft.Text(i18n.t("summary_section"), size=11, color=t["text2"], weight=ft.FontWeight.W_600),
                ft.Row([ft.Text(i18n.t("label_tax"), size=11, color=t["text3"]), tax_field], spacing=12),
                subtotal_field, tax_text, total_text,
                ft.Divider(color=t["border"], height=24),
                ft.Text(i18n.t("notes_section"), size=11, color=t["text2"], weight=ft.FontWeight.W_600),
                notes,
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
        ),
        padding=24,
        expand=True,
    )

    return ft.Column(controls=[topbar, body], spacing=0, expand=True)