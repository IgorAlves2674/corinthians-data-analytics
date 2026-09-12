import subprocess
import sys
from pathlib import Path
from time import perf_counter


# ============================================================
# 1. DESCOBRE A RAIZ DO PROJETO
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ============================================================
# 2. PIPELINE DE ATUALIZAÇÃO
# ============================================================

scripts = [
    "src/extract_players.py",
    "src/transform_players.py",
    "src/extract_match_stats.py",
    "src/validate_match_stats.py",
    "src/transform_match_stats.py",
    "src/extract_matches.py",
    "src/transform_matches.py",
]


# ============================================================
# 3. EXECUTA CADA ETAPA
# ============================================================

print("\n" + "=" * 60)
print("CORINTHIANS DATA ANALYTICS")
print("ATUALIZAÇÃO DOS DADOS")
print("=" * 60)

inicio_total = perf_counter()


for numero, script in enumerate(
    scripts,
    start=1
):

    print(
        f"\n[{numero}/{len(scripts)}] Executando {script}"
    )

    print("-" * 60)

    inicio = perf_counter()

    try:

        subprocess.run(
            [
                sys.executable,
                script
            ],
            cwd=PROJECT_ROOT,
            check=True
        )

    except subprocess.CalledProcessError:

        print("\n" + "=" * 60)
        print("ERRO NA ATUALIZAÇÃO")
        print("=" * 60)

        print(
            f"\nA execução falhou em:\n{script}"
        )

        print(
            "\nO pipeline foi interrompido "
            "para evitar gerar dados inconsistentes."
        )

        sys.exit(1)


    tempo = (
        perf_counter()
        - inicio
    )

    print(
        f"\nEtapa concluída em "
        f"{tempo:.2f} segundos."
    )


# ============================================================
# 4. FINALIZAÇÃO
# ============================================================

tempo_total = (
    perf_counter()
    - inicio_total
)


print("\n" + "=" * 60)
print("ATUALIZAÇÃO CONCLUÍDA COM SUCESSO")
print("=" * 60)

print(
    f"\nTempo total: "
    f"{tempo_total:.2f} segundos."
)

print(
    "\nOs arquivos do dashboard "
    "estão atualizados."
)