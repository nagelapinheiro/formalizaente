"""Limpeza explícita dos artefatos derivados da PoC."""

from src.pipeline import reset_derived_data

if __name__ == "__main__":
    reset_derived_data()
    print("Artefatos derivados removidos; data/raw foi preservado.")

