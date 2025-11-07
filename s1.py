# main.py (S1)
import tkinter as tk
from tkinter import ttk, messagebox
import requests, json, time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"
LOG_FILE = "s1_logs.jsonl"

# -------- logger de chamadas --------
def call_and_log(method, path, payload=None, timeout=15):
    url = f"{BASE_URL}{path}"
    ts = time.time()
    try:
        r = requests.request(method, url, json=payload, timeout=timeout)
        try:
            body = r.json()
        except Exception:
            body = r.text
        entry = {"ts": ts, "method": method, "path": path, "status": r.status_code,
                 "req": payload, "resp": body}
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return r.status_code, body
    except Exception as e:
        entry = {"ts": ts, "method": method, "path": path, "error": str(e)}
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        raise

# ======= ORDENS FIXAS POR FONTE =======
ORD_USUARIOS   = ["id_usuario", "nickname", "email", "senha_hash", "pais_origem", "data_criacao"]
ORD_TRANSACOES = ["id_transacao", "id_usuario", "jogador_id", "tipo", "valor", "data_transacao"]
ORD_ESTATISTICAS = ["id", "nome", "ritmo", "chute", "passe", "dribles", "defesa", "fisico"]
ORD_JOGADORES  = ["id", "nome", "overall", "posicao", "quantidade", "raridade", "valor"]

HEAD_USUARIOS = {
    "id_usuario":"ID_USUARIO","nickname":"NICKNAME","email":"EMAIL",
    "senha_hash":"SENHA_HASH","pais_origem":"PAIS_ORIGEM","data_criacao":"DATA_CRIACAO"
}
HEAD_TRANSACOES = {
    "id_transacao":"ID_TRANSACAO","id_usuario":"ID_USUARIO","jogador_id":"JOGADOR_ID",
    "tipo":"TIPO","valor":"VALOR","data_transacao":"DATA_TRANSACAO"
}
HEAD_ESTATISTICAS = {
    "id":"ID","nome":"Nome","ritmo":"Ritmo","chute":"Chute",
    "passe":"Passe","dribles":"Dribles","defesa":"Defesa","fisico":"Fisico"
}
HEAD_JOGADORES = {
    "id":"ID","nome":"Nome","overall":"Overall","posicao":"Posição",
    "quantidade":"Qtd","raridade":"Raridade","valor":"Valor"
}

def get_val(d, key):
    if key in d: return d[key]
    low = key.lower()
    if low in d: return d[low]
    tit = key.title()
    if tit in d: return d[tit]
    return ""

def render_table(lista, ordem_cols, headers):
    for i in tree.get_children():
        tree.delete(i)
    tree["columns"] = ordem_cols
    tree["show"] = "headings"
    for c in ordem_cols:
        tree.heading(c, text=headers.get(c, c).upper())
        tree.column(c, width=max(110, int(1050/len(ordem_cols))), anchor="center")
    for item in lista:
        row = [get_val(item, c) for c in ordem_cols]
        tree.insert("", "end", values=row)

# ======= LISTAR (GET S2) =======
def carregar_usuarios():
    status, body = call_and_log("get", "/usuarios")
    if status == 200 and isinstance(body, list):
        render_table(body, ORD_USUARIOS, HEAD_USUARIOS)
    else:
        messagebox.showerror("Erro", f"{status}: {body}")

def carregar_transacoes():
    status, body = call_and_log("get", "/transacoes")
    if status == 200 and isinstance(body, list):
        render_table(body, ORD_TRANSACOES, HEAD_TRANSACOES)
    else:
        messagebox.showerror("Erro", f"{status}: {body}")

def carregar_estatisticas():
    status, body = call_and_log("get", "/estatisticas", timeout=6)
    if status == 200 and isinstance(body, list):
        render_table(body, ORD_ESTATISTICAS, HEAD_ESTATISTICAS)
    else:
        messagebox.showerror("Erro", f"{status}: {body}")

def carregar_jogadores():
    status, body = call_and_log("get", "/jogadores")
    if status == 200 and isinstance(body, list):
        render_table(body, ORD_JOGADORES, HEAD_JOGADORES)
    else:
        messagebox.showerror("Erro", f"{status}: {body}")

# ======= INSERIR (POST S2) =======

def inserir_usuario():
    data = {
        "id_usuario": 21,
        "nickname": "BittererFlea",
        "email": "BittererFlea01@gmail.com",
        "senha_hash": "$2a$10$q.M8FZ.JKxO1q1UejaxsaeA1B2Ozv5XsRhvDia0bcQPkIUUf6..2q",
        "pais_origem": "Brasil",
        "data_criacao": "2025-11-06 22:37:00"
    }
    status, body = call_and_log("post", "/usuarios", data)
    if status == 200:
        messagebox.showinfo("Usuário", "Usuário real inserido com sucesso.")
    else:
        messagebox.showerror("Erro", f"{status}: {body}")

def inserir_transacao():
    data = {
        "id_transacao": 647,
        "id_usuario": 20,
        "jogador_id": 62,
        "tipo": "Venda",
        "valor": 1400000,
        "data_transacao": "2025-03-11"
    }
    status, body = call_and_log("post", "/transacoes", data)
    if status == 200:
        messagebox.showinfo("Transação", "Transação real inserida com sucesso.")
    else:
        messagebox.showerror("Erro", f"{status}: {body}")

def inserir_estatistica():
    data = {
        "id": 62,
        "nome": "Iniesta",
        "ritmo": 83,
        "chute": 80,
        "passe": 91,
        "dribles": 92,
        "defesa": 62,
        "fisico": 66
    }
    status, body = call_and_log("post", "/estatisticas", data)
    if status == 200:
        messagebox.showinfo("Estatística", "Estatística real inserida com sucesso.")
    else:
        messagebox.showerror("Erro", f"{status}: {body}")

def inserir_jogador():
    data = {
        "id": 62,
        "nome": "Iniesta",
        "overall": 92,
        "posicao": "CM",
        "quantidade": 1,
        "raridade": "Icone",
        "valor": 1400000
    }
    status, body = call_and_log("post", "/jogadores", data)
    if status == 200:
        messagebox.showinfo("Jogador", "Jogador real inserido com sucesso.")
    else:
        messagebox.showerror("Erro", f"{status}: {body}")


# ======= GUI =======
root = tk.Tk()
root.title("S1 - Polyglot Viewer (via S2)")
root.geometry("1180x640")

top = tk.Frame(root)
top.pack(fill="x", padx=8, pady=8)

# Listar
tk.Label(top, text="Listar").grid(row=0, column=0, sticky="w")
tk.Button(top, text="👤 Usuários (Postgres)",  command=carregar_usuarios,  bg="#06F50E").grid(row=1, column=0, padx=5)
tk.Button(top, text="💸 Transações (Postgres)", command=carregar_transacoes, bg="#06F50E").grid(row=1, column=1, padx=5)
tk.Button(top, text="📊 Estatísticas (MongoDB)", command=carregar_estatisticas, bg="#24A0ED").grid(row=1, column=2, padx=5)
tk.Button(top, text="🎮 Jogadores (Cassandra)",  command=carregar_jogadores,  bg="#F9C74F").grid(row=1, column=3, padx=5)

# Inserir (dados reais)
tk.Label(top, text="Inserir dados").grid(row=0, column=5, sticky="w", padx=(30,0))
tk.Button(top, text="＋ Usuário",command=inserir_usuario).grid(row=1, column=5, padx=5)
tk.Button(top, text="＋ Transação",command=inserir_transacao).grid(row=1, column=6, padx=5)
tk.Button(top, text="＋ Estatística",command=inserir_estatistica).grid(row=1, column=7, padx=5)
tk.Button(top, text="＋ Jogador",command=inserir_jogador).grid(row=1, column=8, padx=5)

# Tabela
tree = ttk.Treeview(root, height=26)
tree.pack(fill="both", expand=True, padx=8, pady=8)

root.mainloop()
