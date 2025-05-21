"""
burndown_sprint1_manual.py

Gera um burndown chart da Sprint 1 (19–24 Maio 2025) a partir de dados
manuais de issues, datas planejadas e datas reais de conclusão.
"""

import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MaxNLocator
import os

# ───────────── Configuração das Issues ─────────────
issues = [
    {"title": "Diagrama de componentes",         "planned_end": "2025-05-20", "done_at": "2025-05-19"},
    {"title": "Modelo de dados ORCID",           "planned_end": "2025-05-20", "done_at": "2025-05-20"},
    {"title": "Escrever 6 casos de uso",         "planned_end": "2025-05-21", "done_at": "2025-05-21"},
    {"title": "Definir 6 casos de teste",        "planned_end": "2025-05-21", "done_at": "2025-05-18"},
    {"title": "Protótipo de funcionalidade de busca", "planned_end": "2025-05-22", "done_at": "2025-05-20"},
    {"title": "Protótipo de visualizações",      "planned_end": "2025-05-23", "done_at": "2025-05-21"},
    {"title": "Projetar esquema da base de dados","planned_end": "2025-05-23", "done_at": "2025-05-20"},
    {"title": "Prototipagem de UI",              "planned_end": "2025-05-24", "done_at": "2025-05-21"},
    {"title": "Project Board & burndown",        "planned_end": "2025-05-19", "done_at": "2025-05-19"},
]


# ───────────── Datas da Sprint ─────────────
start = dt.date(2025, 5, 19)
end   = dt.date(2025, 5, 24)
timeline = [start + dt.timedelta(days=i) for i in range((end - start).days + 1)]
total_issues = len(issues)

# ───────────── Cálculo do burndown ─────────────
remaining = []
for day in timeline:
    open_count = 0
    for issue in issues:
        done = (dt.datetime.strptime(issue["done_at"], "%Y-%m-%d").date()
                if issue["done_at"] else None)
        if not done or done > day:
            open_count += 1
    remaining.append(open_count)

ideal = [
    total_issues - (i * total_issues / (len(timeline)-1))
    for i in range(len(timeline))
]

# ───────────── Plotagem ─────────────
plt.figure(figsize=(10, 6))
plt.plot(timeline, remaining, marker='o', label="Real")
plt.plot(timeline, ideal, linestyle='--', label="Ideal")
plt.title("Burndown – Sprint 1: MVP Interface Preliminar")
plt.xlabel("Data")
plt.ylabel("Issues abertas")
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.5)
plt.gca().xaxis.set_major_formatter(DateFormatter('%b %d'))
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
plt.legend()
plt.tight_layout()

# ───────────── Escolha do diretório de saída ─────────────
base_docs = os.path.join(os.getcwd(), "docs")
# ordem de preferência de pastas em docs/:
candidates = ["metrics", "architecture", "tests", "requirements", "interviews"]
save_dir = None

for sub in candidates:
    path = os.path.join(base_docs, sub)
    if os.path.isdir(path):
        save_dir = path
        break

# se não encontrou nenhuma, cria docs/metrics
if save_dir is None:
    save_dir = os.path.join(base_docs, "metrics")
    os.makedirs(save_dir, exist_ok=True)

output_path = os.path.join(save_dir, "burndown_sprint1.png")
plt.savefig(output_path, dpi=120)
print(f"✅ Gráfico salvo em {output_path}")
