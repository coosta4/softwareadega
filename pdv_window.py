import customtkinter as ctk
from tkinter import ttk, messagebox
import database as db

class PdvWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Ponto de Venda (PDV) - Adega Real")
        self.geometry("1100x700")

        self.carrinho = []

        self._criar_widgets()
        self.entry_codigo.focus_set()

    def _criar_widgets(self):
        frame_esquerda = ctk.CTkFrame(self, width=700)
        frame_esquerda.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        frame_direita = ctk.CTkFrame(self, width=350)
        frame_direita.pack(side="right", fill="both", expand=False, padx=10, pady=10)

        frame_entrada = ctk.CTkFrame(frame_esquerda)
        frame_entrada.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(frame_entrada, text="Código do Produto:", font=("Arial", 14)).pack(side="left", padx=10, pady=10)
        self.entry_codigo = ctk.CTkEntry(frame_entrada, font=("Arial", 16), width=300)
        self.entry_codigo.pack(side="left", padx=10, pady=10)
        self.entry_codigo.bind("<Return>", self._adicionar_ao_carrinho_event)

        frame_carrinho = ctk.CTkFrame(frame_esquerda)
        frame_carrinho.pack(fill="both", expand=True, padx=5, pady=5)
        
        colunas = ('cod', 'nome', 'qtd', 'preco_unit', 'subtotal')
        self.tabela_carrinho = ttk.Treeview(frame_carrinho, columns=colunas, show='headings')
        self.tabela_carrinho.heading('cod', text='Código')
        self.tabela_carrinho.heading('nome', text='Nome')
        self.tabela_carrinho.heading('qtd', text='Qtd.')
        self.tabela_carrinho.heading('preco_unit', text='Preço Unit.')
        self.tabela_carrinho.heading('subtotal', text='Subtotal')
        self.tabela_carrinho.column('cod', width=100)
        self.tabela_carrinho.column('nome', width=300)
        self.tabela_carrinho.column('qtd', width=50, anchor=ctk.CENTER)
        self.tabela_carrinho.column('preco_unit', width=100, anchor=ctk.E)
        self.tabela_carrinho.column('subtotal', width=100, anchor=ctk.E)
        self.tabela_carrinho.pack(fill="both", expand=True)

        frame_total = ctk.CTkFrame(frame_direita, fg_color="#333333")
        frame_total.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(frame_total, text="TOTAL (R$)", font=("Arial", 20, "bold")).pack(pady=5)
        self.label_total = ctk.CTkLabel(frame_total, text="0.00", font=("Arial", 48, "bold"), text_color="#22DD55")
        self.label_total.pack(pady=10, padx=10)
        
        frame_acoes = ctk.CTkFrame(frame_direita)
        frame_acoes.pack(fill="both", expand=True, padx=10, pady=10)

        btn_finalizar = ctk.CTkButton(frame_acoes, text="FINALIZAR VENDA (F5)", font=("Arial", 16), command=self._finalizar_venda, fg_color="green", hover_color="#00AA00")
        btn_finalizar.pack(fill="x", pady=15, ipady=10)

        btn_remover_item = ctk.CTkButton(frame_acoes, text="REMOVER ITEM (DEL)", font=("Arial", 16), command=self._remover_item_carrinho)
        btn_remover_item.pack(fill="x", pady=15, ipady=10)

        btn_cancelar = ctk.CTkButton(frame_acoes, text="CANCELAR VENDA (ESC)", font=("Arial", 16), command=self._cancelar_venda, fg_color="red", hover_color="#CC0000")
        btn_cancelar.pack(fill="x", side="bottom", pady=15, ipady=10)
        
    def _adicionar_ao_carrinho_event(self, event):
        entrada = self.entry_codigo.get()
        if not entrada:
            return
        
        quantidade_a_adicionar = 1
        codigo_produto = entrada

        if 'x' in entrada:
            try:
                partes = entrada.split('x')
                quantidade_a_adicionar = int(partes[0])
                codigo_produto = partes[1]
            except (ValueError, IndexError):
                messagebox.showerror("Entrada inválida", "Formato inválido. Use 'Qtd * Código' ou apenas 'Código'.")
                return

        produto_db = db.buscar_produto_por_codigo(codigo_produto)
        
        if not produto_db:
            messagebox.showwarning("Produto não encontrado", f"Nenhum produto com o código '{codigo_produto}' foi encontrado.")
            self.entry_codigo.delete(0, 'end')
            return
            
        produto_id, nome, preco, estoque_atual = produto_db
        
        item_no_carrinho = None
        for item in self.carrinho:
            if item['id'] == produto_id:
                item_no_carrinho = item
                break
        
        qtd_desejada = (item_no_carrinho['qtd'] + 1) if item_no_carrinho else 1
        if qtd_desejada > estoque_atual:
            messagebox.showerror("Estoque Insuficiente", f"Estoque do produto '{nome}' é insuficiente ({estoque_atual} un.).")
            return
            
        if item_no_carrinho:
            item_no_carrinho['qtd'] += 1
        else:
            self.carrinho.append({'id': produto_id, 'cod': codigo_produto, 'nome': nome, 'preco': preco, 'qtd': 1})
        
        self.entry_codigo.delete(0, 'end')
        self._atualizar_carrinho_display()
        
    def _atualizar_carrinho_display(self):
        for i in self.tabela_carrinho.get_children():
            self.tabela_carrinho.delete(i)
        
        total = 0
        for item in self.carrinho:
            subtotal = item['preco'] * item['qtd']
            total += subtotal
            valores = (item['cod'], item['nome'], item['qtd'], f"{item['preco']:.2f}", f"{subtotal:.2f}")
            self.tabela_carrinho.insert('', 'end', values=valores)
            
        self.label_total.configure(text=f"{total:.2f}")
    
    def _remover_item_carrinho(self):
        selecionado = self.tabela_carrinho.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um item na lista para remover.")
            return

        valores = self.tabela_carrinho.item(selecionado, "values")
        codigo_item_remover = valores[0]

        self.carrinho = [item for item in self.carrinho if item['cod'] != codigo_item_remover]
        
        self._atualizar_carrinho_display()

    def _cancelar_venda(self):
        if self.carrinho and messagebox.askyesno("Confirmar", "Tem certeza que deseja cancelar a venda atual?"):
            self.carrinho.clear()
            self._atualizar_carrinho_display()

    def _finalizar_venda(self):
        if not self.carrinho:
            messagebox.showwarning("Atenção", "O carrinho está vazio. Adicione produtos antes de finalizar.")
            return
            
        if messagebox.askyesno("Finalizar Venda", f"Confirmar a venda no valor de R$ {self.label_total.cget('text')}?"):
            db.registrar_venda(self.carrinho)
            messagebox.showinfo("Sucesso", "Venda registrada com sucesso!")
            self.carrinho.clear()
            self._atualizar_carrinho_display()