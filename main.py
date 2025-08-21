import customtkinter as ctk
import database as db

from pdv_window import PdvWindow
from gestao_estoque_window import GestaoEstoqueWindow
from relatorios_window import RelatoriosWindow

class MainMenu(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Adega Real - Menu Principal")
        self.geometry("400x350")
        
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Menu Principal", font=("Arial", 24, "bold")).grid(row=0, column=0, pady=20, padx=10)

        btn_pdv = ctk.CTkButton(self, text="Ponto de Venda (PDV)", command=self.abrir_pdv, height=50)
        btn_pdv.grid(row=1, column=0, pady=10, padx=20, sticky="ew")

        btn_estoque = ctk.CTkButton(self, text="Gestão de Estoque", command=self.abrir_gestao_estoque, height=50)
        btn_estoque.grid(row=2, column=0, pady=10, padx=20, sticky="ew")

        btn_relatorios = ctk.CTkButton(self, text="Relatórios", command=self.abrir_relatorios, height=50)
        btn_relatorios.grid(row=3, column=0, pady=10, padx=20, sticky="ew")
        
        self.pdv_window = None
        self.estoque_window = None
        self.relatorios_window = None

    def abrir_pdv(self):
        if self.pdv_window is None or not self.pdv_window.winfo_exists():
            self.pdv_window = PdvWindow(self)
            self.pdv_window.transient(self)
        else:
            self.pdv_window.focus()

    def abrir_gestao_estoque(self):
        if self.estoque_window is None or not self.estoque_window.winfo_exists():
            self.estoque_window = GestaoEstoqueWindow()
        else:
            self.estoque_window.focus()
            
    def abrir_relatorios(self):
        if self.relatorios_window is None or not self.relatorios_window.winfo_exists():
            self.relatorios_window = RelatoriosWindow(self)
            self.relatorios_window.transient(self)
        else:
            self.relatorios_window.focus()

if __name__ == "__main__":
    db.criar_tabela()
    app = MainMenu()
    app.mainloop()