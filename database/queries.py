from database.connection import get_connection

# ─────────────────────────────
# CLIENTS | CLIENTES
# ─────────────────────────────

def save_client(name, phone, email, address, logo_path=None):
    # Saves or updates the main business info | Guarda o actualiza la info principal del negocio
    conn = get_connection()
    existing = conn.execute('SELECT * FROM clients WHERE id = 1').fetchone()
    if existing:
        conn.execute('''
            UPDATE clients
            SET name = ?, phone = ?, email = ?, address = ?, logo_path = ?
            WHERE id = 1
        ''', (name, phone, email, address, logo_path))
    else:
        conn.execute('''
            INSERT INTO clients (name, phone, email, address, logo_path)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, phone, email, address, logo_path))
    conn.commit()
    conn.close()

def get_all_clients():
    # Retrieves all clients sorted by name | Obtiene todos los clientes ordenados por nombre
    conn = get_connection()
    clients = conn.execute('SELECT * FROM clients ORDER BY name').fetchall()
    conn.close()
    return clients

def get_client(client_id):
    # Gets a specific client by ID | Obtiene un cliente específico por ID
    conn = get_connection()
    client = conn.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()
    conn.close()
    return client

def create_client(name, phone, email, address):
    # Adds a new client and returns its ID | Agrega un nuevo cliente y retorna su ID
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO clients (name, phone, email, address) VALUES (?, ?, ?, ?)', 
        (name, phone, email, address)
    )
    conn.commit()
    client_id = cursor.lastrowid
    conn.close()
    return client_id

def update_client(client_id, name, phone, email, address):
    # Updates existing client details | Actualiza los detalles de un cliente existente
    conn = get_connection()
    conn.execute('''
        UPDATE clients
        SET name = ?, phone = ?, email = ?, address = ?
        WHERE id = ?
    ''', (name, phone, email, address, client_id))
    conn.commit()
    conn.close()

def delete_client(client_id):
    # Removes a client from the database | Elimina un cliente de la base de datos
    conn = get_connection()
    conn.execute('DELETE FROM clients WHERE id = ?', (client_id,))
    conn.commit()
    conn.close()

# ─────────────────────────────
# USER SETTINGS | AJUSTES DE USUARIO
# ─────────────────────────────

def get_user():
    # Gets the main user profile | Obtiene el perfil del usuario principal
    conn = get_connection()
    user = conn.execute('SELECT * FROM users WHERE id = 1').fetchone()
    conn.close()
    return user

def save_user(name, phone, email, address, logo_path=None, estimate_prefix="EST", theme="dark", lang="es"):
    # Saves or updates user profile and preferences | Guarda o actualiza el perfil y preferencias
    conn = get_connection()
    existing = conn.execute('SELECT id FROM users WHERE id = 1').fetchone()
    if existing:
        conn.execute('''
            UPDATE users
            SET name = ?, phone = ?, email = ?, address = ?, logo_path = ?, estimate_prefix = ?, theme = ?, lang = ?
            WHERE id = 1
        ''', (name, phone, email, address, logo_path, estimate_prefix, theme, lang))
    else:
        conn.execute('''
            INSERT INTO users (id, name, phone, email, address, logo_path, estimate_prefix, theme, lang)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, phone, email, address, logo_path, estimate_prefix, theme, lang))
    conn.commit()
    conn.close()

def get_estimate_prefix():
    # Gets the prefix for quotes (e.g., EST) | Obtiene el prefijo para presupuestos (ej: EST)
    conn = get_connection()
    user = conn.execute('SELECT * FROM users WHERE id = 1').fetchone()
    conn.close()
    if user and user["estimate_prefix"]:
        return user["estimate_prefix"].strip().upper()
    return "EST"

def get_theme_preference():
    # Gets saved theme (dark/light) | Obtiene el tema guardado (oscuro/claro)
    conn = get_connection()
    user = conn.execute('SELECT theme FROM users WHERE id = 1').fetchone()
    conn.close()
    if user and user["theme"]:
        return user["theme"]
    return "dark"

def get_lang_preference():
    # Gets saved language (en/es) | Obtiene el idioma guardado (en/es)
    conn = get_connection()
    user = conn.execute('SELECT lang FROM users WHERE id = 1').fetchone()
    conn.close()
    if user and "lang" in user.keys() and user["lang"]:
        return user["lang"]
    return "es"

# [CHANGE] Save the company logo path to the database (users table, id=1)
# Allows SettingsView to persist the selected logo path without rewriting the full user record.
# [CAMBIO] Guarda la ruta del logo de la empresa en la base de datos (tabla users, id=1)
# Permite que SettingsView persista la ruta del logo sin reescribir el registro completo del usuario.
def save_logo_path(path):
    conn = get_connection()
    conn.execute("UPDATE users SET logo_path = ? WHERE id = 1", (path,))
    conn.commit()
    conn.close()

# [CHANGE] Retrieves the saved company logo path from the database (users table, id=1)
# Returns None if no logo has been saved yet or if an error occurs.
# [CAMBIO] Recupera la ruta del logo guardada en la base de datos (tabla users, id=1)
# Retorna None si no se ha guardado ningún logo aún o si ocurre un error.
def get_logo_path():
    try:
        conn = get_connection()
        user = conn.execute("SELECT logo_path FROM users WHERE id = 1").fetchone()
        conn.close()
        return user["logo_path"] if user and user["logo_path"] else None
    except:
        return None

# ─────────────────────────────
# ESTIMATES | PRESUPUESTOS
# ─────────────────────────────

def get_next_estimate_number():
    # Generates the next sequential quote number | Genera el siguiente número secuencial de presupuesto
    conn = get_connection()
    count = conn.execute('SELECT COUNT(*) as total FROM items').fetchone()["total"]
    conn.close()
    prefix = get_estimate_prefix()
    return f"{prefix}-{str(count + 1).zfill(4)}"

def get_all_estimates():
    # Retrieves all active (non-archived) estimates | Obtiene todos los presupuestos activos
    conn = get_connection()
    estimates = conn.execute(
        """SELECT * FROM items 
        WHERE status NOT IN ('archived_draft', 'archived_sent', 'archived_accepted', 'archived_rejected')
        ORDER BY created_at DESC"""
    ).fetchall()
    conn.close()
    return estimates

def get_all_estimates_by_client(client_id):
    # Gets all quotes belonging to a specific client | Obtiene presupuestos de un cliente específico
    conn = get_connection()
    estimates = conn.execute(
        "SELECT * FROM items WHERE client_id = ? ORDER BY created_at DESC", (client_id,)
    ).fetchall()
    conn.close()
    return estimates

def get_estimate(estimate_id):
    # Gets a quote with client basic info joined | Obtiene presupuesto con info básica del cliente
    conn = get_connection()
    estimate = conn.execute('''
        SELECT i.*, c.name as client_name, c.phone as client_phone,
                c.email as client_email, c.address as client_address
        FROM items i
        JOIN clients c ON i.client_id = c.id
        WHERE i.id = ?
    ''', (estimate_id,)).fetchone()
    conn.close()
    return estimate

def get_full_estimate_details(estimate_id):
    # Gets quote info and all its line items | Obtiene el presupuesto y todos sus artículos
    conn = get_connection()
    estimate = conn.execute('''
        SELECT i.*, c.name as client_name, c.phone as client_phone,
                c.email as client_email, c.address as client_address
        FROM items i
        JOIN clients c ON i.client_id = c.id
        WHERE i.id = ?
    ''', (estimate_id,)).fetchone()
    items = conn.execute('''
        SELECT * FROM estimate_items 
        WHERE estimate_id = ?
    ''', (estimate_id,)).fetchall()
    conn.close()
    return estimate, items

def create_estimate(client_id, title="", description="", notes="", valid_until="", tax_rate=0.0, subtotal=0.0, total=0.0, language="es"):
    # Creates a new quote record | Crea un nuevo registro de presupuesto
    conn = get_connection()
    estimate_number = get_next_estimate_number()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO items (estimate_number, client_id, title, description, notes, valid_until, tax_rate, subtotal, total, language)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (estimate_number, client_id, title, description, notes, valid_until, tax_rate, subtotal, total, language))
    conn.commit()
    estimate_id = cursor.lastrowid
    conn.close()
    return estimate_id

def update_estimate(estimate_id, client_id, title="", description="", notes="", valid_until="", language="es"):
    # Updates general quote information | Actualiza la información general del presupuesto
    conn = get_connection()
    conn.execute('''
        UPDATE items
        SET client_id = ?, title = ?, description = ?, notes = ?, valid_until = ?, language = ?
        WHERE id = ?
    ''', (client_id, title, description, notes, valid_until, language, estimate_id))
    conn.commit()
    conn.close()

def update_estimate_status(estimate_id, status):
    # Changes quote status (draft, sent, etc.) | Cambia el estado (borrador, enviado, etc.)
    conn = get_connection()
    conn.execute('UPDATE items SET status = ? WHERE id = ?', (status, estimate_id))
    conn.commit()
    conn.close()

def archive_estimate(estimate_id):
    # Moves quote to archive by changing status prefix | Archiva el presupuesto cambiando el prefijo del estado
    conn = get_connection()
    est = conn.execute("SELECT status FROM items WHERE id = ?", (estimate_id,)).fetchone()
    if est:
        original_status = est["status"]
        conn.execute(
            "UPDATE items SET status = ? WHERE id = ?",
            (f"archived_{original_status}", estimate_id)
        )
    conn.commit()
    conn.close()

def delete_estimate(estimate_id):
    # Deletes a quote permanently | Elimina un presupuesto permanentemente
    conn = get_connection()
    conn.execute('DELETE FROM items WHERE id = ?', (estimate_id,))
    conn.commit()
    conn.close()

def get_items(estimate_id):
    # Gets all items inside a quote | Obtiene todos los artículos de un presupuesto
    conn = get_connection()
    items = conn.execute('SELECT * FROM estimate_items WHERE estimate_id = ?', (estimate_id,)).fetchall()
    conn.close()
    return items

def add_item(estimate_id, category, description, quantity, unit, unit_price):
    # Adds a single item to a quote | Agrega un artículo individual a un presupuesto
    conn = get_connection()
    conn.execute('''
        INSERT INTO estimate_items (estimate_id, category, description, quantity, unit, unit_price)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (estimate_id, category, description, quantity, unit, unit_price))
    conn.commit()
    conn.close()

def delete_all_items(estimate_id):
    # Clears all items from a quote | Limpia todos los artículos de un presupuesto
    conn = get_connection()
    conn.execute("DELETE FROM estimate_items WHERE estimate_id = ?", (estimate_id,))
    conn.commit()
    conn.close()

# ─────────────────────────────
# INCOME | INGRESOS
# ─────────────────────────────

def get_all_income(year=None):
    # Retrieves all income records, optionally by year | Obtiene ingresos, opcionalmente por año
    conn = get_connection()
    if year:
        income = conn.execute(
            "SELECT * FROM income WHERE strftime('%Y', date) = ? ORDER BY date DESC",
            (str(year),)
        )
    else:
        income = conn.execute("SELECT * FROM income ORDER BY date DESC")
    
    results = income.fetchall()
    conn.close()
    return results

def add_income(description, amount, date, notes=""):
    # Adds a new income record | Agrega un nuevo registro de ingreso
    conn = get_connection()
    conn.execute(
        "INSERT INTO income (description, amount, date, notes) VALUES (?, ?, ?, ?)",
        (description, amount, date, notes)
    )
    conn.commit()
    conn.close()

def delete_income(income_id):
    # Deletes an income record | Elimina un registro de ingreso
    conn = get_connection()
    conn.execute("DELETE FROM income WHERE id = ?", (income_id,))
    conn.commit()
    conn.close()

# ─────────────────────────────
# EXPENSES | GASTOS
# ─────────────────────────────

def get_all_expenses(year=None):
    # Retrieves all expense records, optionally by year | Obtiene gastos, opcionalmente por año
    conn = get_connection()
    if year:
        expenses = conn.execute(
            "SELECT * FROM expenses WHERE strftime('%Y', date) = ? ORDER BY date DESC",
            (str(year),)
        )
    else:
        expenses = conn.execute("SELECT * FROM expenses ORDER BY date DESC")
    
    results = expenses.fetchall()
    conn.close()
    return results

def add_expense(description, amount, date, notes=""):
    # Adds a new expense and returns its ID | Agrega un nuevo gasto y retorna su ID
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (description, amount, date, notes) VALUES (?, ?, ?, ?)",
        (description, amount, date, notes)
    )
    conn.commit()
    expense_id = cursor.lastrowid
    conn.close()
    return expense_id

def delete_expense(expense_id):
    # Deletes an expense record | Elimina un registro de gasto
    conn = get_connection()
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

def get_summary(year=None):
    # Calculates financial totals (Income, Expenses, Net) | Calcula totales financieros (Ingresos, Gastos, Neto)
    income = get_all_income(year)
    expenses = get_all_expenses(year)
    total_income = sum(i["amount"] for i in income)
    total_expenses = sum(e["amount"] for e in expenses)
    net = total_income - total_expenses
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net": net,
        "deductions": total_expenses,
    }

# ─────────────────────────────
# EXPENSE ITEMS | DETALLES DE GASTOS
# ─────────────────────────────

def get_expense_items(expense_id):
    # Gets items linked to a specific expense | Obtiene artículos ligados a un gasto específico
    conn = get_connection()
    items = conn.execute("SELECT * FROM expense_items WHERE expense_id = ?", (expense_id,)).fetchall()
    conn.close()
    return items

def add_expense_item(expense_id, description, amount):
    # Adds a detail item to an expense | Agrega un artículo de detalle a un gasto
    conn = get_connection()
    conn.execute(
        "INSERT INTO expense_items (expense_id, description, amount) VALUES (?, ?, ?)",
        (expense_id, description, amount)
    )
    conn.commit()
    conn.close()

def delete_expense_item(item_id):
    # Deletes a specific expense detail item | Elimina un artículo de detalle de gasto específico
    conn = get_connection()
    conn.execute("DELETE FROM expense_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def get_expense_with_items(expense_id):
    # Gets expense info and all its details | Obtiene info del gasto y todos sus detalles
    conn = get_connection()
    expense = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    items = conn.execute("SELECT * FROM expense_items WHERE expense_id = ?", (expense_id,)).fetchall()
    conn.close()
    return expense, items

# ─────────────────────────────
# EVENTS | EVENTOS (CALENDARIO)
# ─────────────────────────────

def get_events_by_month(year, month):
    # Gets all events for a specific month | Obtiene todos los eventos de un mes específico
    conn = get_connection()
    month_str = f"{year}-{str(month).zfill(2)}"
    events = conn.execute(
        "SELECT * FROM events WHERE date LIKE ? ORDER BY date ASC",
        (f"{month_str}%",)
    ).fetchall()
    conn.close()
    return events

def get_events_by_date(date):
    # Gets all events for a specific day | Obtiene todos los eventos de un día específico
    conn = get_connection()
    events = conn.execute("SELECT * FROM events WHERE date = ? ORDER BY id ASC", (date,)).fetchall()
    conn.close()
    return events

def add_event(date, event_type, description, color="#f0a500", time=""):
    # Adds a new event to the calendar | Agrega un nuevo evento al calendario
    conn = get_connection()
    conn.execute(
        "INSERT INTO events (date, type, description, color, time) VALUES (?, ?, ?, ?, ?)",
        (date, event_type, description, color, time)
    )
    conn.commit()
    conn.close()

def delete_event(event_id):
    # Removes an event from the calendar | Elimina un evento del calendario
    conn = get_connection()
    conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()