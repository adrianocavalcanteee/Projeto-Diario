import sqlite3
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, scrolledtext

# 🔧 Criação da tabela do banco
def criar_tabela():
    with sqlite3.connect("diario.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anotacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora TEXT NOT NULL,
                texto TEXT NOT NULL
            );
        """)
        conn.commit()

# ✅ Criar: salvar anotação
def salvar_anotacao():
    texto = entrada_texto.get("1.0", tk.END).strip()
    if not texto:
        messagebox.showwarning("Aviso", "A anotação está vazia!")
        return

    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    entrada_formatada = f"[{data_hora}] {texto}\n"

    with sqlite3.connect("diario.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO anotacoes (data_hora, texto) VALUES (?, ?)", (data_hora, texto))
        conn.commit()

    with open("diario.txt", "a", encoding="utf-8") as arquivo:
        arquivo.write(entrada_formatada)

    entrada_texto.delete("1.0", tk.END)
    messagebox.showinfo("Sucesso", "Anotação salva com sucesso!")

# 📖 Ler: exibe as anotações
def ler_anotacoes():
    if not os.path.exists("diario.db"):
        messagebox.showinfo("Diário", "O diário está vazio.")
        return

    with sqlite3.connect("diario.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, data_hora, texto FROM anotacoes ORDER BY id")
        entradas = cursor.fetchall()

        texto_resultado.delete("1.0", tk.END)

        if not entradas:
            texto_resultado.insert(tk.END, "O diário está vazio.")
        else:
            for id_, data_hora, texto in entradas:
                texto_resultado.insert(tk.END, f"ID {id_} - [{data_hora}] {texto}\n")

# 🗑️ Deletar: apagar por ID
def apagar_anotacao_por_id():
    def confirmar_exclusao():
        id_escolhido = entrada_id.get().strip()
        if not id_escolhido.isdigit():
            messagebox.showerror("Erro", "Digite um ID numérico válido.")
            return

        id_int = int(id_escolhido)
        with sqlite3.connect("diario.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM anotacoes WHERE id = ?", (id_int,))
            if not cursor.fetchone():
                messagebox.showinfo("Não encontrado", f"Nenhuma anotação com ID {id_int}.")
                return
            cursor.execute("DELETE FROM anotacoes WHERE id = ?", (id_int,))
            conn.commit()

        messagebox.showinfo("Sucesso", f"Anotação ID {id_int} apagada.")
        janela.destroy()

    janela = tk.Toplevel()
    janela.title("🗑️ Apagar Anotação")
    janela.geometry("300x150")
    janela.configure(bg="#e6f2ff")

    tk.Label(janela, text="ID da anotação a apagar:", bg="#e6f2ff").pack(pady=10)
    entrada_id = tk.Entry(janela)
    entrada_id.pack(pady=5)
    tk.Button(janela, text="Apagar", command=confirmar_exclusao, bg="#99ccff").pack(pady=10)

# ✏️ Atualizar: editar anotação por ID
def editar_anotacao():
    def buscar_anotacao():
        id_busca = entrada_id.get().strip()
        if not id_busca.isdigit():
            messagebox.showerror("Erro", "Digite um ID válido.")
            return

        id_int = int(id_busca)
        with sqlite3.connect("diario.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT texto FROM anotacoes WHERE id = ?", (id_int,))
            resultado = cursor.fetchone()
            if not resultado:
                messagebox.showinfo("Erro", f"ID {id_int} não encontrado.")
                return

            texto_existente.set(resultado[0])

    def atualizar():
        novo_texto = campo_texto.get("1.0", tk.END).strip()
        id_editar = entrada_id.get().strip()
        if not id_editar.isdigit() or not novo_texto:
            messagebox.showwarning("Erro", "Dados inválidos.")
            return

        with sqlite3.connect("diario.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE anotacoes SET texto = ? WHERE id = ?", (novo_texto, int(id_editar)))
            conn.commit()

        messagebox.showinfo("Sucesso", "Anotação atualizada.")
        janela_editar.destroy()

    janela_editar = tk.Toplevel()
    janela_editar.title("✏️ Editar Anotação")
    janela_editar.geometry("500x350")
    janela_editar.configure(bg="#e6f2ff")

    texto_existente = tk.StringVar()

    tk.Label(janela_editar, text="Digite o ID da anotação:", bg="#e6f2ff").pack(pady=5)
    entrada_id = tk.Entry(janela_editar)
    entrada_id.pack(pady=5)

    tk.Button(janela_editar, text="Buscar", command=buscar_anotacao, bg="#99ccff").pack(pady=5)

    campo_texto = scrolledtext.ScrolledText(janela_editar, width=50, height=10)
    campo_texto.pack(pady=5)

    def preencher_texto(*args):
        campo_texto.delete("1.0", tk.END)
        campo_texto.insert(tk.END, texto_existente.get())

    texto_existente.trace("w", preencher_texto)

    tk.Button(janela_editar, text="Salvar Alterações", command=atualizar, bg="#99ccff").pack(pady=10)

# 🎨 Interface Gráfica principal
def iniciar_interface():
    global entrada_texto, texto_resultado

    criar_tabela()

    root = tk.Tk()
    root.title("📘 Diário Eletrônico - CRUD Completo")
    root.geometry("680x700")
    root.configure(bg="#e6f2ff")

    fonte = ("Arial", 11)
    bg = "#e6f2ff"
    btn = "#99ccff"

    tk.Label(root, text="Digite sua anotação:", bg=bg, font=fonte).pack(pady=5)

    entrada_texto = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=8, font=fonte)
    entrada_texto.pack(pady=5)

    tk.Button(root, text="Salvar Anotação", command=salvar_anotacao, bg=btn, font=fonte).pack(pady=5)
    tk.Button(root, text="Ler Diário", command=ler_anotacoes, bg=btn, font=fonte).pack(pady=5)
    tk.Button(root, text="✏️ Editar Anotação", command=editar_anotacao, bg=btn, font=fonte).pack(pady=5)
    tk.Button(root, text="🗑️ Apagar Anotação", command=apagar_anotacao_por_id, bg=btn, font=fonte).pack(pady=5)

    texto_resultado = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=18, font=fonte)
    texto_resultado.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    iniciar_interface()
