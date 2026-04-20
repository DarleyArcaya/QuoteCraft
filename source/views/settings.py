import flet as ft
from database import queries
from utils.theme import get_theme
import shutil
import os
from datetime import datetime
from database.connection import BASE_DIR, save_user_language

# [CHANGE] Import pathlib for robust cross-platform path handling when copying logo files
# [CAMBIO] Importamos pathlib para manejo robusto de rutas al copiar el archivo del logo
import pathlib as pl


def SettingsView(page: ft.Page):
    t = get_theme(page.data["theme"])
    # Retrieve the translator from page.data | Recuperamos el traductor de page.data
    i18n = page.data["i18n"]

    user = queries.get_user()

    # --- LANGUAGE CHANGE FUNCTION | FUNCIÓN PARA CAMBIAR IDIOMA ---
    def change_language(e):
        selected_lang = e.control.data
        page.data["i18n"].set_lang(selected_lang)
        save_user_language(selected_lang)
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

    # [CHANGE] Save button moved to topbar — same style as the rest of the app's action buttons
    # [CAMBIO] Botón de guardar movido al topbar — mismo estilo que los demás botones de acción de la app
    # [CHANGE] Read current logo_path from DB before saving so it's never overwritten
# [CAMBIO] Leer logo_path actual de la DB antes de guardar para que nunca se sobreescriba
    def save_company(e):
        current_logo = queries.get_logo_path()  # preserve existing logo | preservar logo existente
        queries.save_user(
            name=company_name.value,
            phone=company_phone.value,
            email=company_email.value,
            address=company_address.value,
            estimate_prefix=estimate_prefix.value or "EST",
            theme=page.data["theme"],
            logo_path=current_logo,  # pass it back so it's not lost | pasarlo para que no se pierda
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

    # Logo section setup | Configuración de la sección de logo
    current_logo_path = queries.get_logo_path()
    logo_status = ft.Text("", size=12, color=t["text2"])
    _has_logo = bool(current_logo_path and os.path.exists(current_logo_path))

    logo_preview = ft.Image(
        src=current_logo_path if _has_logo else None,
        width=120,
        height=80,
        fit=ft.BoxFit.CONTAIN,
        visible=_has_logo,
    )

    logo_placeholder = ft.Icon(
        ft.Icons.IMAGE_OUTLINED,
        size=48,
        color=t["text3"],
        visible=not _has_logo,
    )

    logo_preview_container = ft.Container(
        content=ft.Stack(controls=[logo_placeholder, logo_preview]),
        width=160,
        height=100,
        border=ft.border.all(1, t["border"]),
        border_radius=10,
        bgcolor=t["surface2"],
        alignment=ft.Alignment(0, 0),
    )

    async def open_logo_picker(e):
        files = await ft.FilePicker().pick_files(
            dialog_title=i18n.t("select_logo"),
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["png", "jpg", "jpeg", "webp"],
            allow_multiple=False,
        )
        if not files:
            logo_status.value = i18n.t("no_file")
            page.update()
            return
        src_path = pl.Path(files[0].path)
        try:
            logos_dir = BASE_DIR / "assets" / "logos"
            logos_dir.mkdir(parents=True, exist_ok=True)
            dst_path = logos_dir / src_path.name
            shutil.copy2(src_path, dst_path)
            queries.save_logo_path(str(dst_path))
            logo_preview.src = str(dst_path)
            logo_preview.visible = True
            logo_placeholder.visible = False
            logo_status.value = f"✓ {src_path.name}"
            logo_status.color = "#22c97a"
        except Exception as ex:
            logo_status.value = f"Error: {str(ex)}"
            logo_status.color = "#ff5f6d"
        page.update()

    def remove_logo(e):
        queries.save_logo_path(None)
        logo_preview.src = None
        logo_preview.visible = False
        logo_placeholder.visible = True
        logo_status.value = ""
        page.update()

    async def open_file_picker(e):
        backup_dir = BASE_DIR / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        files = await ft.FilePicker().pick_files(
            dialog_title=i18n.t("select_backup"),
            initial_directory=str(backup_dir),
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["db"],
            allow_multiple=False,
        )
        if not files:
            restore_label.value = i18n.t("no_file")
            page.update()
            return
        selected = files[0]
        restore_label.value = f"{i18n.t('selected')}: {selected.name}"
        restore_label.color = t["accent"]
        page.update()

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

    logo_section = ft.Column(
        controls=[
            ft.Text(i18n.t("logo_section"), size=11, color=t["text2"], weight=ft.FontWeight.W_600),
            ft.Text(i18n.t("logo_hint"), size=12, color=t["text3"]),
            ft.Row(
                controls=[
                    logo_preview_container,
                    ft.Column(
                        controls=[
                            ft.ElevatedButton(
                                i18n.t("choose_logo"),
                                icon=ft.Icons.UPLOAD_FILE_OUTLINED,
                                bgcolor=t["surface2"],
                                color=t["accent"],
                                on_click=open_logo_picker,
                            ),
                            ft.TextButton(
                                i18n.t("remove_logo"),
                                style=ft.ButtonStyle(color=t["text3"]),
                                on_click=remove_logo,
                            ),
                            logo_status,
                        ],
                        spacing=6,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        spacing=8,
    )

    # ─────────────────────────────────────────────────────────────────
    # [CHANGE] Topbar now includes the Save button on the right side.
    # It uses ElevatedButton with the accent color to match the app style.
    # The body no longer contains a standalone Save button.
    #
    # [CAMBIO] El topbar ahora incluye el botón Guardar en el lado derecho.
    # Usa ElevatedButton con el color accent para coincidir con el estilo
    # de la app. El body ya no contiene un botón Guardar independiente.
    # ─────────────────────────────────────────────────────────────────
    topbar = ft.Container(
        content=ft.Row(
            controls=[
                # Left side — back button + title | Lado izquierdo — botón atrás + título
                ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=t["text2"], on_click=go_back),
                    ft.Text(i18n.t("settings"), size=18, weight=ft.FontWeight.W_600, color=t["text"]),
                ]),
                # [CHANGE] Right side — Save button in the appbar
                # [CAMBIO] Lado derecho — botón Guardar en el appbar
                ft.ElevatedButton(
                    i18n.t("save_button"),
                    bgcolor=t["accent"],
                    color=t["bg"],
                    on_click=save_company,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=24, vertical=12),
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

                # Logo Section | Sección de Logo
                logo_section,
                ft.Divider(color=t["border"], height=24),

                # Estimates Configuration | Configuración de Presupuestos
                ft.Text(i18n.t("estimates_section"), size=11, color=t["text2"], weight=ft.FontWeight.W_600),
                ft.Text(i18n.t("prefix_info"), size=12, color=t["text2"]),
                ft.Row([
                    estimate_prefix,
                    ft.Text(f"{(estimate_prefix.value or 'EST').upper()}-0001", size=13, color=t["text2"]),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                ft.Divider(color=t["border"], height=24),

                # Backup Section | Sección de Respaldo
                ft.Text(i18n.t("backup_title"), size=11, color=t["text2"], weight=ft.FontWeight.W_600),
                ft.Row([
                    ft.ElevatedButton(i18n.t("create_backup"), icon=ft.Icons.SAVE, bgcolor=t["surface2"], color=t["accent"], on_click=do_backup),
                    ft.TextButton(i18n.t("view_folder"), style=ft.ButtonStyle(color=t["text2"]), on_click=open_backup_folder),
                ], spacing=8),
                backup_status,
                ft.Divider(color=t["border"], height=24),

                # Restore Section | Sección de Restauración
                ft.Text(i18n.t("restore_title"), size=11, color=t["text2"], weight=ft.FontWeight.W_600),
                ft.Row([
                    ft.ElevatedButton(
                        i18n.t("select_backup"),
                        icon=ft.Icons.RESTORE,
                        bgcolor=t["surface2"],
                        color=t["accent"],
                        on_click=open_file_picker,
                    ),
                ], spacing=8),
                restore_label,
                restore_status,
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
                ft.Text(f"{i18n.t('version')} 1.1.2", size=13, color=t["text2"]),
                ft.Text(f"{i18n.t('developed_by')} Darley Silot Arcaya", size=12, color=t["text3"]),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
        ),
        padding=24,
        expand=True,
    )

    return ft.Column(controls=[topbar, body], spacing=0, expand=True)