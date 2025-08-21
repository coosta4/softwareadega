import customtkinter as ctk
from tkinter import ttk, messagebox
import database as db

class GestaoEstoqueWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)

        self.title("Gestão de Estoque - Adega Real")
        self.geometry("1000x600")
        
        self.id_selecionado = None

        self.frame_formulario = ctk.CTkFrame(self, width=980, height=150)
        self.frame_formulario.pack(pady=10, padx=10, fill="x")
        self.frame_formulario.grid_propagate(False)

        self.frame_botoes = ctk.CTkFrame(self, width=980)
        self.frame_botoes.pack(pady=5, padx=10, fill="x")

        self.frame_tabela = ctk.CTkFrame(self, width=980)
        self.frame_tabela.pack(pady=10, padx=10, fill="both", expand=True)

        self._criar_widgets_formulario()
        self._criar_widgets_botoes()
        self._criar_widget_tabela()
        self._carregar_produtos()

    def _criar_widgets_formulario(self):
        self.frame_formulario.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(self.frame_formulario, text="Código de Barras:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_codigo = ctk.CTkEntry(self.frame_formulario)
        self.entry_codigo.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.frame_formulario, text="Nome do Produto:").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.entry_nome = ctk.CTkEntry(self.frame_formulario)
        self.entry_nome.grid(row=1, column=1, padx=5, pady=5, columnspan=3, sticky="ew")

        ctk.CTkLabel(self.frame_formulario, text="Preço de Venda (R$):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_preco_venda = ctk.CTkEntry(self.frame_formulario)
        self.entry_preco_venda.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.frame_formulario, text="Preço de Custo (R$):").grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.entry_preco_custo = ctk.CTkEntry(self.frame_formulario)
        self.entry_preco_custo.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.frame_formulario, text="Qtd. em Estoque:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.entry_estoque = ctk.CTkEntry(self.frame_formulario)
        self.entry_estoque.grid(row=3, column=2, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.frame_formulario, text="Estoque Mínimo:").grid(row=2, column=3, padx=5, pady=5, sticky="w")
        self.entry_estoque_minimo = ctk.CTkEntry(self.frame_formulario)
        self.entry_estoque_minimo.grid(row=3, column=3, padx=5, pady=5, sticky="ew")
    
    def _criar_widgets_botoes(self):
        btn_salvar = ctk.CTkButton(self.frame_botoes, text="Salvar", command=self._salvar_produto)
        btn_salvar.pack(side="left", padx=10, pady=10)
        
        btn_limpar = ctk.CTkButton(self.frame_botoes, text="Novo/Limpar", command=self._limpar_campos)
        btn_limpar.pack(side="left", padx=10, pady=10)

        btn_remover = ctk.CTkButton(self.frame_botoes, text="Remover", fg_color="red", hover_color="#CC0000", command=self._remover_produto)
        btn_remover.pack(side="left", padx=10, pady=10)
    
    def _criar_widget_tabela(self):
        colunas = ('id', 'codigo_barras', 'nome', 'preco_venda', 'estoque', 'estoque_minimo')
        self.tabela = ttk.Treeview(self.frame_tabela, columns=colunas, show='headings')

        self.tabela.heading('id', text='ID')
        self.tabela.heading('codigo_barras', text='Código')
        self.tabela.heading('nome', text='Nome do Produto')
        self.tabela.heading('preco_venda', text='Preço Venda')
        self.tabela.heading('estoque', text='Estoque Atual')
        self.tabela.heading('estoque_minimo', text='Estoque Mín.')

        self.tabela.column('id', width=50, anchor=ctk.CENTER)
        self.tabela.column('codigo_barras', width=120)
        self.tabela.column('nome', width=350)
        self.tabela.column('preco_venda', width=100, anchor=ctk.CENTER)
        self.tabela.column('estoque', width=100, anchor=ctk.CENTER)
        self.tabela.column('estoque_minimo', width=100, anchor=ctk.CENTER)

        self.tabela.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(self.frame_tabela, command=self.tabela.yview)
        scrollbar.pack(side="right", fill="y")
        self.tabela.configure(yscrollcommand=scrollbar.set)
        
        self.tabela.bind("<<TreeviewSelect>>", self._ao_selecionar_produto)
    
    def _carregar_produtos(self):
        for i in self.tabela.get_children():
            self.tabela.delete(i)

        produtos = db.listar_produtos()
        for produto in produtos:
            self.tabela.insert('', 'end', values=produto)

    def _ao_selecionar_produto(self, event):
        item_selecionado = self.tabela.selection()
        if not item_selecionado:
            return
        
        valores = self.tabela.item(item_selecionado, "values")
        self.id_selecionado = valores[0]

        produto_completo = next((p for p in db.listar_produtos() if p[0] == int(self.id_selecionado)), None)
        
        self._limpar_campos(limpar_id=False)

        self.entry_codigo.insert(0, valores[1])
        self.entry_nome.insert(0, valores[2])
        self.entry_preco_venda.insert(0, valores[3])
        self.entry_estoque.insert(0, valores[4])
        self.entry_estoque_minimo.insert(0, valores[5])
    
    def _limpar_campos(self, limpar_id=True):
        if limpar_id:
            self.id_selecionado = None
        self.entry_codigo.delete(0, 'end')
        self.entry_nome.delete(0, 'end')
        self.entry_preco_venda.delete(0, 'end')
        self.entry_preco_custo.delete(0, 'end')
        self.entry_estoque.delete(0, 'end')
        self.entry_estoque_minimo.delete(0, 'end')
        self.tabela.selection_remove(self.tabela.selection())

    def _salvar_produto(self):
        codigo = self.entry_codigo.get()
        nome = self.entry_nome.get()
        preco_venda = self.entry_preco_venda.get()
        preco_custo = self.entry_preco_custo.get() or "0"
        estoque = self.entry_estoque.get()
        estoque_minimo = self.entry_estoque_minimo.get() or "5"

        if not all([codigo, nome, preco_venda, estoque]):
            messagebox.showerror("Erro de Validação", "Código, Nome, Preço de Venda e Estoque são obrigatórios.")
            return
        
        try:
            if self.id_selecionado is None:
                db.adicionar_produto(codigo, nome, float(preco_venda), float(preco_custo), int(estoque), int(estoque_minimo))
                messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")
            else:
                db.atualizar_produto(self.id_selecionado, codigo, nome, float(preco_venda), float(preco_custo), int(estoque), int(estoque_minimo))
                messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")

            self._limpar_campos()
            self._carregar_produtos()

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar o produto: {e}")
    
    def _remover_produto(self):
        if self.id_selecionado is None:
            messagebox.showwarning("Atenção", "Selecione um produto na tabela para remover.")
            return
        
        if messagebox.askyesno("Confirmar Remoção", f"Tem certeza que deseja remover o produto ID {self.id_selecionado}?"):
            try:
                db.remover_produto(self.id_selecionado)
                messagebox.showinfo("Sucesso", "Produto removido com sucesso!")
                self._limpar_campos()
                self._carregar_produtos()
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao remover o produto: {e}")