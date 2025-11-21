import tkinter as tk
from tkinter import ttk, messagebox
import re
from Database.database import DB

class ClientForm(tk.Toplevel):
    """Finestra emergent per Afegir o Editar Clients"""
    def __init__(self, parent, db, client_data=None, callback=None):
        super().__init__(parent)
        self.db = db
        self.client_data = client_data
        self.callback = callback
        
        self.title("Editar Client" if client_data else "Nou Client")
        self.geometry("400x450")
        self.resizable(False, False)
        self.grab_set()

        self.create_widgets()
        if client_data:
            self.fill_fields()

    def create_widgets(self):
        labels = ["DNI/NIE:", "Nom *:", "Cognoms *:", "Email:", "Telèfon:", "Tipus:", "Estat:"]
        self.entries = {}

        for i, label_text in enumerate(labels):
            tk.Label(self, text=label_text).grid(row=i, column=0, padx=10, pady=10, sticky="e")
            
            if "Tipus" in label_text:
                widget = ttk.Combobox(self, values=["regular", "vip", "premium"], state="readonly")
                widget.current(0)
            elif "Estat" in label_text:
                widget = ttk.Combobox(self, values=["actiu", "suspès", "inactiu"], state="readonly")
                widget.current(0)
            else:
                widget = tk.Entry(self, width=30)
            
            widget.grid(row=i, column=1, padx=10, pady=5)
            key = label_text.replace(" *:", "").replace(":", "")
            self.entries[key] = widget

        btn_save = tk.Button(self, text="Guardar", bg="#4CAF50", fg="white", command=self.save)
        btn_save.grid(row=len(labels), column=0, columnspan=2, pady=20, ipadx=20)

    def fill_fields(self):
        d = self.client_data
        vals = {
            "DNI/NIE": d[1], "Nom": d[2], "Cognoms": d[3], 
            "Email": d[4], "Telèfon": d[5], "Tipus": d[7], "Estat": d[8]
        }
        for key, val in vals.items():
            if val:
                if isinstance(self.entries[key], ttk.Combobox):
                    self.entries[key].set(val)
                else:
                    self.entries[key].insert(0, str(val))

    def validate(self):
        nom = self.entries["Nom"].get().strip()
        cognoms = self.entries["Cognoms"].get().strip()
        email = self.entries["Email"].get().strip()

        if not nom or not cognoms:
            messagebox.showwarning("Validació", "Nom i Cognoms són obligatoris.")
            return False
        
        if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            messagebox.showwarning("Validació", "Format d'email incorrecte.")
            return False
        return True

    def save(self):
        if not self.validate(): return

        data = {k: v.get().strip() for k, v in self.entries.items()}
        
        if self.client_data:
            success, msg = self.db.update_client(
                self.client_data[0], # ID
                data["DNI/NIE"], data["Nom"], data["Cognoms"], data["Email"],
                data["Telèfon"], data["Tipus"], data["Estat"]
            )
        else:
            success, msg = self.db.insert_client(
                data["DNI/NIE"], data["Nom"], data["Cognoms"], data["Email"],
                data["Telèfon"], data["Tipus"], data["Estat"]
            )

        if success:
            messagebox.showinfo("Èxit", msg)
            if self.callback: self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error BBDD", msg)


class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestió HipoAposta (Tkinter)")
        self.root.geometry("1000x600")
        self.db = DB()
        self.create_top_bar()
        self.create_treeview()
        self.create_status_bar()
        self.load_data()

    def create_top_bar(self):
        frame = tk.Frame(self.root, pady=10, bg="#f0f0f0")
        frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(frame, text="Filtrar per nom:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        
        self.entry_search = tk.Entry(frame)
        self.entry_search.pack(side=tk.LEFT, padx=5)

        tk.Button(frame, text="Cercar", command=self.search).pack(side=tk.LEFT, padx=2)
        tk.Button(frame, text="Reiniciar", command=self.reset).pack(side=tk.LEFT, padx=2)
        tk.Button(frame, text="Eliminar", fg="red", command=self.delete_client).pack(side=tk.RIGHT, padx=5)
        tk.Button(frame, text="Editar", command=self.open_edit_form).pack(side=tk.RIGHT, padx=5)
        tk.Button(frame, text="Afegir", bg="#4CAF50", fg="white", command=self.open_add_form).pack(side=tk.RIGHT, padx=5)

    def create_treeview(self):
        cols = ("ID", "DNI", "Nom", "Cognoms", "Email", "Telèfon", "Saldo", "Tipus", "Estat")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings")

    
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=40, anchor="center")
        
        self.tree.heading("DNI", text="DNI/NIE")
        self.tree.column("DNI", width=100)

        self.tree.heading("Nom", text="Nom")
        self.tree.column("Nom", width=100)

        self.tree.heading("Cognoms", text="Cognoms")
        self.tree.column("Cognoms", width=150)

        self.tree.heading("Email", text="Email")
        self.tree.column("Email", width=200)
        
        self.tree.heading("Telèfon", text="Telèfon")
        self.tree.column("Telèfon", width=100)

        self.tree.heading("Saldo", text="Saldo (€)")
        self.tree.column("Saldo", width=80, anchor="e")

        self.tree.heading("Tipus", text="Tipus")
        self.tree.column("Tipus", width=80, anchor="center")

        self.tree.heading("Estat", text="Estat")
        self.tree.column("Estat", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("Llest.")
        lbl = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        lbl.pack(side=tk.BOTTOM, fill=tk.X)

    def load_data(self, name_filter=""):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        rows = self.db.fetch_clients(name_filter)

        for r in rows:
            self.tree.insert("", tk.END, values=r)
        
        self.status_var.set(f"Registres carregats: {len(rows)}")

    def search(self):
        term = self.entry_search.get().strip()
        self.load_data(term)

    def reset(self):
        self.entry_search.delete(0, tk.END)
        self.load_data()

    def open_add_form(self):
        ClientForm(self.root, self.db, callback=self.load_data)

    def open_edit_form(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atenció", "Selecciona un client per editar.")
            return
        
        item_values = self.tree.item(selected[0])['values']
        ClientForm(self.root, self.db, client_data=item_values, callback=self.load_data)

    def delete_client(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atenció", "Selecciona un client per eliminar.")
            return
        
        client_id = self.tree.item(selected[0])['values'][0]
        nom_client = self.tree.item(selected[0])['values'][2]

        confirm = messagebox.askyesno("Confirmar", f"Estàs segur d'eliminar a {nom_client}?")
        if confirm:
            success, msg = self.db.delete_client(client_id)
            if success:
                self.load_data()
                self.status_var.set(msg)
            else:
                messagebox.showerror("Error", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()