import flet as ft
from database import queries
from datetime import datetime
from services.finance_pdf import generate_finance_pdf
from utils.theme import get_theme
import os
import sys
import subprocess

# [CHANGE] Cross-platform file opener — replaces os.startfile which is Windows-only.
# Windows → os.startfile | macOS → open | Linux → xdg-open
# [CAMBIO] Abridor de archivos multiplataforma — reemplaza os.startfile que es solo de Windows.
def open_file_cross_platform(path):
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.run(["open", path])
    else:
        subprocess.run(["xdg-open", path])

def FinancesView(page: ft.Page):
    # Load theme and internationalization data
    # Cargar el tema y los datos de internacionalización
    t = get_theme(page.data["theme"])
    i18n = page.data["i18n"]
    
    # Get current year for the initial state
    # Obtener el año actual para el estado inicial
    current_actual_year_int = datetime.now().year
    current_actual_year = str(current_actual_year_int)
    state = {"year": current_actual_year}

    # Fetch initial financial summary from database
    # Obtener el resumen financiero inicial desde la base de datos
    init_summary = queries.get_summary(state["year"])

    # --- Dashboard UI Elements / Elementos de la Interfaz del Dashboard ---
    income_text   = ft.Text(f"${init_summary['total_income']:,.2f}", size=22, weight=ft.FontWeight.BOLD, color="#22c97a")
    expenses_text = ft.Text(f"${init_summary['total_expenses']:,.2f}", size=22, weight=ft.FontWeight.BOLD, color="#ff5f6d")
    net_text      = ft.Text(f"${init_summary['net']:,.2f}", size=22, weight=ft.FontWeight.BOLD, color=t["accent"])
    deduct_text   = ft.Text(f"{i18n.t('deductions')}: ${init_summary['deductions']:,.2f}", size=14, color=t["text2"])

    def transaction_row(item, kind):
        """Creates a visual row for an income or expense record / Crea una fila visual para un registro de ingreso o gasto"""
        
        def delete(e):
            """Initializes the deletion confirmation dialog / Inicializa el diálogo de confirmación de eliminación"""
            confirm_field = ft.TextField(
                hint_text=i18n.t("delete_confirm_hint"),
                bgcolor=t["surface2"],
                border_color=t["border"],
                focused_border_color="#ff5f6d",
            )

            def do_delete(e):
                """Executes the deletion if the confirmation word is correct / Ejecuta la eliminación si la palabra de confirmación es correcta"""
                if confirm_field.value != i18n.t("delete_confirm_word"):
                    confirm_field.border_color = "#ff5f6d"
                    confirm_field.hint_text = i18n.t("delete_confirm_error")
                    confirm_field.update()
                    return
                
                if kind == "income":
                    queries.delete_income(item["id"])
                else:
                    queries.delete_expense(item["id"])
                
                dlg_confirm.open = False
                page.update()
                refresh(state["year"])

            def cancel_delete(e):
                dlg_confirm.open = False
                page.update()

            dlg_confirm = ft.AlertDialog(
                title=ft.Text(i18n.t("delete_record_title")),
                content=ft.Column([
                    ft.Text(f"{i18n.t('delete_record_msg')} '{item['description']}' {i18n.t('by')} ${item['amount']:,.2f}. {i18n.t('delete_warning')}", size=13, color=t["text2"]),
                    confirm_field,
                ], spacing=12, tight=True),
                actions=[
                    ft.TextButton(i18n.t("cancel"), on_click=cancel_delete),
                    ft.ElevatedButton(i18n.t("delete"), bgcolor="#ff5f6d", color="white", on_click=do_delete),
                ],
            )
            page.overlay.append(dlg_confirm)
            dlg_confirm.open = True
            page.update()

        color = "#22c97a" if kind == "income" else "#ff5f6d"

        # Handle sub-items for expenses (materials/services)
        # Manejar sub-elementos para gastos (materiales/servicios)
        sub_items = []
        if kind == "expense":
            expense_items = queries.get_expense_items(item["id"])
            for ei in expense_items:
                sub_items.append(
                    ft.Row(
                        controls=[
                            ft.Text(f"  • {ei['description']}", size=11, color=t["text2"], expand=True),
                            ft.Text(f"${ei['amount']:,.2f}", size=11, color=t["text2"]),
                        ]
                    )
                )

        controls = [
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(item["description"], size=13, weight=ft.FontWeight.W_500, color=t["text"]),
                            ft.Text(item["date"], size=11, color=t["text2"]),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Text(f"${item['amount']:,.2f}", size=14, color=color, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color="#ff5f6d",
                        icon_size=16,
                        on_click=delete,
                    )
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ]

        if sub_items:
            controls.extend(sub_items)

        return ft.Container(
            content=ft.Column(controls=controls, spacing=4),
            bgcolor=t["surface"],
            border=ft.border.all(1, t["border"]),
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
        )

    def build_lists(year):
        """Generates the lists of UI components for a given year / Genera las listas de componentes de interfaz para un año dado"""
        rows_income   = [transaction_row(i, "income") for i in queries.get_all_income(year)]
        rows_expenses = [transaction_row(e, "expense") for e in queries.get_all_expenses(year)]
        return rows_income, rows_expenses

    # Initialize lists and scrollable columns
    # Inicializar listas y columnas con scroll
    init_income, init_expenses = build_lists(state["year"])
    income_list   = ft.Column(controls=init_income, spacing=6, scroll=ft.ScrollMode.AUTO)
    expenses_list = ft.Column(controls=init_expenses, spacing=6, scroll=ft.ScrollMode.AUTO)

    def refresh(year=None):
        """Updates the dashboard and transaction lists / Actualiza el dashboard y las listas de transacciones"""
        summary = queries.get_summary(year)
        income_text.value   = f"${summary['total_income']:,.2f}"
        expenses_text.value = f"${summary['total_expenses']:,.2f}"
        net_text.value      = f"${summary['net']:,.2f}"
        deduct_text.value   = f"{i18n.t('deductions')}: ${summary['deductions']:,.2f}"

        income_list.controls.clear()
        for i in queries.get_all_income(year):
            income_list.controls.append(transaction_row(i, "income"))

        expenses_list.controls.clear()
        for e in queries.get_all_expenses(year):
            expenses_list.controls.append(transaction_row(e, "expense"))

        page.update()

    def show_add_dialog(kind):
        """Shows dialog to add a new income or expense / Muestra el diálogo para añadir un nuevo ingreso o gasto"""
        desc   = ft.TextField(label=i18n.t("label_desc_work"), bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"])
        
        # Set default date based on selected year filter
        # Establecer fecha por defecto basada en el filtro de año seleccionado
        if state["year"] == current_actual_year:
            default_date = datetime.now().strftime("%Y-%m-%d")
        else:
            default_date = f"{state['year']}-01-01"

        date   = ft.TextField(label=i18n.t("label_date_format"), bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"], value=default_date)
        notes  = ft.TextField(label=i18n.t("label_notes_opt"), bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"])
        amount = ft.TextField(label=i18n.t("label_amount"), bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"], keyboard_type=ft.KeyboardType.NUMBER)

        # Expense-specific item logic
        # Lógica de ítems específica para gastos
        expense_items = []
        items_column  = ft.Column(spacing=6)
        total_text    = ft.Text(f"{i18n.t('total')}: $0.00", size=13, weight=ft.FontWeight.BOLD, color="#ff5f6d")

        def calc_expense_total():
            total = 0.0
            for item in expense_items:
                try:
                    total += float(item["amt"].value or 0)
                except ValueError:
                    pass
            total_text.value = f"{i18n.t('total')}: ${total:,.2f}"
            total_text.update()

        def build_item_row():
            """Creates a sub-row for expense materials / Crea una sub-fila para materiales de gasto"""
            item_desc = ft.TextField(hint_text=i18n.t("label_material_service"), bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"], expand=True)
            item_amt  = ft.TextField(hint_text="$0.00", bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"], width=80, keyboard_type=ft.KeyboardType.NUMBER, on_change=lambda e: calc_expense_total())
            row_data  = {"desc": item_desc, "amt": item_amt}
            expense_items.append(row_data)
            row_ref = ft.Ref[ft.Row]()

            def delete_item(e):
                expense_items.remove(row_data)
                items_column.controls.remove(row_ref.current)
                items_column.update()
                calc_expense_total()

            row = ft.Row(
                ref=row_ref,
                controls=[item_desc, item_amt, ft.IconButton(icon=ft.Icons.CLOSE, icon_color=t["text2"], icon_size=14, on_click=delete_item)],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
            return row

        def add_item_row(e):
            row = build_item_row()
            items_column.controls.append(row)
            items_column.update()

        def save(e):
            """Saves the data to DB / Guarda los datos en la base de datos"""
            desc.error_text = None
            if not desc.value or not desc.value.strip():
                desc.error_text = i18n.t("required_field")
                desc.update()
                return

            if kind == "income":
                if not amount.value: return
                try:
                    amt = float(amount.value)
                except ValueError: return
                queries.add_income(desc.value, amt, date.value, notes.value)
            else:
                total = 0.0
                valid_items = []
                for item in expense_items:
                    try:
                        amt = float(item["amt"].value or 0)
                        if item["desc"].value and amt > 0:
                            valid_items.append((item["desc"].value, amt))
                            total += amt
                    except ValueError: pass
                
                if not valid_items: return
                expense_id = queries.add_expense(desc.value, total, date.value, notes.value)
                for item_desc, item_amt in valid_items:
                    queries.add_expense_item(expense_id, item_desc, item_amt)

            dlg.open = False
            page.update()
            refresh(state["year"])

        def cancel(e):
            dlg.open = False
            page.update()

        # Build dynamic content based on transaction type
        # Construir contenido dinámico basado en el tipo de transacción
        if kind == "income":
            content_controls = [desc, amount, date, notes]
        else:
            content_controls = [
                desc, date, notes,
                ft.Divider(color=t["border"]),
                ft.Text(i18n.t("materials_services_section"), size=11, color=t["text2"], weight=ft.FontWeight.W_600),
                ft.Row(controls=[
                    ft.Text(i18n.t("table_desc"), size=11, color=t["text3"], expand=True),
                    ft.Text(i18n.t("table_amount") if "table_amount" in (i18n.translations.get(i18n.lang, {})) else "Amount", size=11, color=t["text3"], width=80),
                    ft.Container(width=36),
                ]),
                items_column,
                ft.TextButton(i18n.t("btn_add_material"), style=ft.ButtonStyle(color=t["accent"]), on_click=add_item_row),
                total_text,
            ]

        title = i18n.t("add_income_title") if kind == "income" else i18n.t("add_expense_title")
        dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Column(content_controls, spacing=10, tight=True, scroll=ft.ScrollMode.AUTO, height=400),
            actions=[
                ft.TextButton(i18n.t("cancel"), on_click=cancel),
                ft.ElevatedButton(i18n.t("save_button"), bgcolor=t["accent"], color=t["bg"], on_click=save),
            ],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def filter_year(e):
        state["year"] = e.control.value 
        refresh(state["year"])

    def show_export_dialog(e):
        """Displays language selection for PDF report / Muestra la selección de idioma para el reporte PDF"""
        def start_export(lang_code):
            dlg.open = False
            page.update()
            path = generate_finance_pdf(state["year"], lang_code)
            if path:
                # [CHANGE] Replaced os.startfile with cross-platform opener
                # [CAMBIO] Reemplazado os.startfile con abridor multiplataforma
                open_file_cross_platform(path)

        prompt_text = i18n.t("select_pdf_language")
        
        # Translation patch for missing keys
        # Parche de traducción para claves faltantes
        if prompt_text == "select_pdf_language":
            if i18n.t("finances_title") == "Finanzas":
                prompt_text = "Seleccione el idioma del reporte"
            else:
                prompt_text = "Select report language"

        dlg = ft.AlertDialog(
            title=ft.Text(i18n.t("btn_export_pdf")),
            content=ft.Text(prompt_text),
            actions=[
                ft.TextButton("Español", on_click=lambda _: start_export("es")),
                ft.TextButton("English", on_click=lambda _: start_export("en")),
            ],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def go_back(e):
        from views.home import HomeView
        page.controls.clear()
        page.add(HomeView(page))
        page.update()

    # Dropdown options for year filtering
    # Opciones de desplegable para filtrado de año
    year_options = [
        ft.dropdown.Option(str(y)) 
        for y in range(current_actual_year_int + 5, current_actual_year_int - 3, -1)
    ]
    
    year_dropdown = ft.Dropdown(
        label=i18n.t("label_year"),
        value=state["year"],
        options=year_options,
        width=120,
        bgcolor=t["surface2"],
        border_color=t["border"],
        focused_border_color=t["accent"],
        on_select=filter_year
    )

    # --- Header and Main Layout / Cabecera y Diseño Principal ---
    topbar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=t["text2"], on_click=go_back),
                    ft.Text(i18n.t("finances_title"), size=18, weight=ft.FontWeight.W_600, color=t["text"]),
                ]),
                ft.Row([
                    year_dropdown,
                    ft.ElevatedButton(
                        i18n.t("btn_export_pdf"), 
                        bgcolor=t["accent"], 
                        color=t["bg"], 
                        on_click=show_export_dialog
                    ),
                ])
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
        bgcolor=t["surface"],
        border=ft.border.only(bottom=ft.BorderSide(1, t["border"])),
    )

    dashboard = ft.Container(
        content=ft.Row(
            controls=[
                # Income Card / Tarjeta de Ingresos
                ft.Container(
                    content=ft.Column([
                        ft.Text(i18n.t("income_label"), size=11, color=t["text2"]),
                        income_text,
                    ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=t["surface"], border=ft.border.all(1, t["border"]),
                    border_radius=12, padding=20, expand=True,
                ),
                # Expenses Card / Tarjeta de Gastos
                ft.Container(
                    content=ft.Column([
                        ft.Text(i18n.t("expenses_label"), size=11, color=t["text2"]),
                        expenses_text,
                    ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=t["surface"], border=ft.border.all(1, t["border"]),
                    border_radius=12, padding=20, expand=True,
                ),
                # Net Balance Card / Tarjeta de Saldo Neto
                ft.Container(
                    content=ft.Column([
                        ft.Text(i18n.t("net_label"), size=11, color=t["text2"]),
                        net_text,
                        deduct_text,
                    ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=t["surface"], border=ft.border.all(1, t["border"]),
                    border_radius=12, padding=20, expand=True,
                ),
            ],
            spacing=12,
        ),
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
    )

    body = ft.Container(
        content=ft.Column(
            controls=[
                dashboard,
                ft.Container(
                    content=ft.Column([
                        # Income Section Header / Encabezado de Sección de Ingresos
                        ft.Row([
                            ft.Text(i18n.t("income_label"), size=13, weight=ft.FontWeight.W_600, color="#22c97a", expand=True),
                            ft.TextButton(i18n.t("btn_add"), style=ft.ButtonStyle(color="#22c97a"), on_click=lambda e: show_add_dialog("income")),
                        ]),
                        income_list,
                        ft.Divider(color=t["border"], height=24),
                        # Expense Section Header / Encabezado de Sección de Gastos
                        ft.Row([
                            ft.Text(i18n.t("expenses_label"), size=13, weight=ft.FontWeight.W_600, color="#ff5f6d", expand=True),
                            ft.TextButton(i18n.t("btn_add"), style=ft.ButtonStyle(color="#ff5f6d"), on_click=lambda e: show_add_dialog("expense")),
                        ]),
                        expenses_list,
                    ]),
                    padding=24,
                )
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
    )

    return ft.Column(
        controls=[topbar, body],
        spacing=0,
        expand=True,
    )