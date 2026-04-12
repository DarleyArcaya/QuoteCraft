import flet as ft
from database import queries
from utils.theme import get_theme
import shutil
import os
from datetime import datetime
from database.connection import BASE_DIR, save_user_language 

def SettingsView(page: ft.Page):
    t = get_theme(page.data["theme"])
    # Retrieve the translator from page.data | Recuperamos el traductor de page.data
    i18n = page.data["i18n"]

    user = queries.get_user()

    # --- LANGUAGE CHANGE FUNCTION | FUNCIÓN PARA CAMBIAR IDIOMA ---
    def change_language(e):
        selected_lang = e.control.data
        
        # 1. Update the global i18n object | Actualizamos el objeto i18n global de la página
        page.data["i18n"].set_lang(selected_lang)
        
        # 2. Save to database (Persistence) | Guardamos en la base de datos (Persistencia real)
        save_user_language(selected_lang) 
        
        # 3. Refresh view to apply visual changes | Refrescamos la vista completa para aplicar los cambios visuales
        page.controls.clear()
        page.add(SettingsView(page))
        page.update()

    # --- TRANSLATED TEXT FIELDS | CAMPOS DE TEXTO TRADUCIDOS ---
    company_name    = ft.TextField(label=i18n.t("company_name"), bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"], value=user["name"] if user else "")
    company_phone   = ft.TextField(label=i18n.t("phone"), bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"], value=user["phone"] if user else "")
    company_email   = ft.TextField(label=i18n.t("email"), bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"], value=user["email"] if user else "")
    company_address = ft.TextField(label=i18n.t("address"), bgcolor=t["surface2"], border_color=t["border"], focused_border_color=t["accent"], value=user["address"] if user else "")
    estimate_prefix = ft.TextField(
        label=i18n.t("prefix_label"),
        hint_text="ej: EST, SC, JR",
        bgcolor=t["surface2"],
        border_color=t["border"],
        focused_border_color=t["accent"],
        value=user["estimate_prefix"] if user and user["estimate_prefix"] else "EST",
        width=160,
        max_length=6,
    )

    # Save company profile information | Guardar información del perfil de empresa
    def save_company(e):
        queries.save_user(
            name=company_name.value,
            phone=company_phone.value,
            email=company_email.value,
            address=company_address.value,
            estimate_prefix=estimate_prefix.value or "EST",
            theme=page.data["theme"],
        )
        snack = ft.SnackBar(content=ft.Text(i18n.t("save_data"), color="white"), bgcolor="#22c97a", duration=2000)
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def go_back(e):
        from views.home import HomeView
        page.controls.clear()
        page.add(HomeView(page))
        page.update()

    # Toggle between Light and Dark mode | Alternar entre modo Claro y Oscuro
    def toggle_theme(e):
        if page.data["theme"] == "dark":
            page.data["theme"] = "light"
            page.bgcolor = "#f5f5f5"
            page.theme_mode = ft.ThemeMode.LIGHT
        else:
            page.data["theme"] = "dark"
            page.bgcolor = "#0d0f14"
            page.theme_mode = ft.ThemeMode.DARK
        
        u = queries.get_user()
        if u:
            queries.save_user(
                name=u["name"] or "",
                phone=u["phone"] or "",
                email=u["email"] or "",
                address=u["address"] or "",
                estimate_prefix=u["estimate_prefix"] or "EST",
                theme=page.data["theme"],
            )
        page.controls.clear()
        page.add(SettingsView(page))
        page.update()

    theme_btn = ft.TextButton(
        i18n.t("light_mode") if page.data["theme"] == "dark" else i18n.t("dark_mode"),
        on_click=toggle_theme,
        style=ft.ButtonStyle(color=t["accent"]),
    )

    backup_status  = ft.Text("", size=12, color=t["text2"])
    restore_status = ft.Text("", size=12, color=t["text2"])
    restore_label  = ft.Text(i18n.t("no_file"), size=12, color=t["text2"])

    # Database backup logic | Lógica de respaldo de la base de datos
    def do_backup(e):
        try:
            backup_dir = BASE_DIR / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%I-%M%p")
            src = BASE_DIR / "data" / "estimate.db"
            dst = backup_dir / f"estimate_backup_{timestamp}.db"
            shutil.copy2(src, dst)
            backup_status.value = f"{i18n.t('backup_done')}: {dst.name}"
            backup_status.color = "#22c97a"
        except Exception as ex:
            backup_status.value = f"Error: {str(ex)}"
            backup_status.color = "#ff5f6d"
        page.update()

    def open_backup_folder(e):
        backup_dir = BASE_DIR / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        if os.name == 'nt':
            os.startfile(str(backup_dir))

    # File picker for database restoration | Selector de archivos para restauración de BD
    async def open_file_picker(e):
        picker = ft.FilePicker(on_result=lambda res: process_picker_result(res))
        page.overlay.append(picker)
        page.update()
        
        backup_dir = BASE_DIR / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        picker.pick_files(
            dialog_title=i18n.t("select_backup"),
            initial_directory=str(backup_dir),
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["db"],
        )

    # Process file picker result — type annotation removed for flet build compatibility
    # Procesa el resultado del selector de archivos — anotación de tipo removida para compatibilidad con flet build
    def process_picker_result(res):
        if not res.files:
            restore_label.value = i18n.t("no_file")
            page.update()
            return
        
        selected = res.files[0]
        restore_label.value = f"{i18n.t('selected')}: {selected.name}"
        restore_label.color = t["accent"]
        
        def confirm_restore(ev):
            try:
                dst = BASE_DIR / "data" / "estimate.db"
                shutil.copy2(selected.path, dst)
                restore_status.value = i18n.t("restore_success")
                restore_status.color = "#22c97a"
                dlg_restore.open = False
                page.update()
            except Exception as ex:
                restore_status.value = f"Error: {str(ex)}"
                restore_status.color = "#ff5f6d"
                page.update()

        dlg_restore = ft.AlertDialog(
            title=ft.Text(i18n.t("restore_title")),
            content=ft.Text(f"{i18n.t('restore_warning')} '{selected.name}'.", size=13, color=t["text2"]),
            actions=[
                ft.TextButton(i18n.t("cancel"), on_click=lambda _: setattr(dlg_restore, "open", False)),
                ft.ElevatedButton(i18n.t("restore_btn"), bgcolor="#ff5f6d", color="white", on_click=confirm_restore),
            ],
        )
        page.overlay.append(dlg_restore)
        dlg_restore.open = True
        page.update()

    # --- INTERFACE LAYOUT | INTERFAZ ---
    topbar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=t["text2"], on_click=go_back),
                    ft.Text(i18n.t("settings"), size=18, weight=ft.FontWeight.W_600, color=t["text"]),
                ]),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
        bgcolor=t["surface"],
        border=ft.border.only(bottom=ft.BorderSide(1, t["border"])),
    )

    body = ft.Container(
        content=ft.Column(
            controls=[
                # Company Section | Sección de Empresa
                ft.Text(i18n.t("company"), size=11, color=t["text2"], weight=ft.FontWeight.W_600),
                company_name,
                ft.Row([company_phone, company_email], spacing=12),
                company_address,
                ft.Divider(color=t["border"], height=24),
                
                # Estimates Configuration | Configuración de Presupuestos
                ft.Text(i18n.t("estimates_section"), size=11, color=t["text2"], weight=ft.FontWeight.W_600),
                ft.Text(i18n.t("prefix_info"), size=12, color=t["text2"]), 
                ft.Row([
                    estimate_prefix,
                    ft.Text(f"{(estimate_prefix.value or 'EST').upper()}-0001", size=13, color=t["text2"]),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                ft.ElevatedButton(i18n.t("save_button"), bgcolor=t["accent"], color=t["bg"], on_click=save_company),
                ft.Divider(color=t["border"], height=24),
                
                # Backup Section | Sección de Respaldo
                ft.Text(i18n.t("backup_title"), size=11, color=t["text2"], weight=ft.FontWeight.W_600),
                ft.Row([
                    ft.ElevatedButton(i18n.t("create_backup"), icon=ft.Icons.SAVE, bgcolor=t["surface2"], color=t["accent"], on_click=do_backup),
                    ft.TextButton(i18n.t("view_folder"), style=ft.ButtonStyle(color=t["text2"]), on_click=open_backup_folder),
                ], spacing=8),
                backup_status,
                ft.Divider(color=t["border"], height=24),
                
                # Appearance and Language | Apariencia e Idioma
                ft.Text(i18n.t("appearance"), size=11, color=t["text2"], weight=ft.FontWeight.W_600),
                theme_btn,
                ft.Divider(color=t["border"], height=24),
                ft.Text(i18n.t("language"), size=11, color=t["text2"], weight=ft.FontWeight.W_600),
                ft.Row([
                    ft.TextButton("Español", data="es", on_click=change_language, 
                                  style=ft.ButtonStyle(color=t["accent"] if i18n.lang == "es" else t["text2"])),
                    ft.TextButton("English", data="en", on_click=change_language, 
                                  style=ft.ButtonStyle(color=t["accent"] if i18n.lang == "en" else t["text2"])),
                ]),
                ft.Divider(color=t["border"], height=24),
                
                # App Info | Información de la App
                ft.Text(i18n.t("about"), size=11, color=t["text2"], weight=ft.FontWeight.W_600),
                ft.Text("QuoteCraft", size=20, weight=ft.FontWeight.BOLD, color=t["accent"]),
                ft.Text(f"{i18n.t('version')} 1.0.0", size=13, color=t["text2"]),
                ft.Text(f"{i18n.t('developed_by')} Darley Silot Arcaya", size=12, color=t["text3"]),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
        ),
        padding=24,
        expand=True,
    )

    return ft.Column(controls=[topbar, body], spacing=0, expand=True)