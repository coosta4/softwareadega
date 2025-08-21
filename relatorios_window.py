import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date
import database as db

class RelatoriosWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Relatórios - Adega Real")
        self.geometry("800x600")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_vendas = self.tabview.add("Vendas por Período")
        self.tab_estoque = self.tabview.add("Estoque Baixo")

        self._criar_aba_vendas()
        self._criar_aba_estoque()

    def _criar_aba_vendas(self):
        frame_filtros = ctk.CTkFrame(self.tab_vendas)
        frame_filtros.pack(fill="x", padx=10, pady=10)

        hoje = date.today().strftime("%Y-%m-%d")
        
        ctk.CTkLabel(frame_filtros, text="Data Início:").pack(side="left", padx=5)
        self.entry_data_inicio = ctk.CTkEntry(frame_filtros)
        self.entry_data_inicio.insert(0, hoje)
        self.entry_data_inicio.pack(side="left", padx=5)

        ctk.CTkLabel(frame_filtros, text="Data Fim:").pack(side="left", padx=5)
        self.entry_data_fim = ctk.CTkEntry(frame_filtros)
        self.entry_data_fim.insert(0, hoje)
        self.entry_data_fim.pack(side="left", padx=5)

        btn_gerar = ctk.CTkButton(frame_filtros, text="Gerar Relatório", command=self._gerar_relatorio_vendas)
        btn_gerar.pack(side="left", padx=10)

        colunas_vendas = ('id', 'data_hora', 'total')
        self.tabela_vendas = ttk.Treeview(self.tab_vendas, columns=colunas_vendas, show='headings')
        self.tabela_vendas.heading('id', text='ID Venda')
        self.tabela_vendas.heading('data_hora', text='Data e Hora')
        self.tabela_vendas.heading('total', text='Total (R$)')
        self.tabela_vendas.pack(fill="both", expand=True, padx=10, pady=10)

        self.label_total_periodo = ctk.CTkLabel(self.tab_vendas, text="Total do Período: R$ 0.00", font=("Arial", 16, "bold"))
        self.label_total_periodo.pack(pady=10)

    def _criar_aba_estoque(self):
        btn_verificar = ctk.CTkButton(self.tab_estoque, text="Verificar Estoque Baixo Agora", command=self._gerar_relatorio_estoque)
        btn_verificar.pack(pady=20)
        
        colunas_estoque = ('nome', 'estoque_atual', 'estoque_minimo')
        self.tabela_estoque = ttk.Treeview(self.tab_estoque, columns=colunas_estoque, show='headings')
        self.tabela_estoque.heading('nome', text='Nome do Produto')
        self.tabela_estoque.heading('estoque_atual', text='Estoque Atual')
        self.tabela_estoque.heading('estoque_minimo', text='Estoque Mínimo')
        self.tabela_estoque.pack(fill="both", expand=True, padx=10, pady=10)

    def _gerar_relatorio_vendas(self):
        data_inicio = self.entry_data_inicio.get()
        data_fim = self.entry_data_fim.get()

        for i in self.tabela_vendas.get_children():
            self.tabela_vendas.delete(i)
        
        vendas = db.gerar_relatorio_vendas(data_inicio, data_fim)
        total_periodo = 0
        for venda in vendas:
            self.tabela_vendas.insert('', 'end', values=(venda[0], venda[1], f"{venda[2]:.2f}"))
            total_periodo += venda[2]
            
        self.label_total_periodo.configure(text=f"Total do Período: R$ {total_periodo:.2f}")

    def _gerar_relatorio_estoque(self):
        for i in self.tabela_estoque.get_children():
            self.tabela_estoque.delete(i)
            
        produtos = db.gerar_relatorio_estoque_baixo()
        if not produtos:
            messagebox.showinfo("Estoque OK", "Nenhum produto com estoque baixo encontrado.")
        
        for produto in produtos:
            self.tabela_estoque.insert('', 'end', values=produto)