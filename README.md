# PID – strojenie temperatury

Prosta aplikacja w Pythonie (Streamlit) do symulacji i wizualizacji strojenia regulatora PID dla obiektu termicznego.

## Funkcje

- Regulacja temperatury z parametrami **Kp**, **Ki**, **Kd**
- Symulacja odpowiedzi skokowej (temperatura zadana vs. aktualna)
- Wykres strojenia (Plotly)
- Podstawowe metryki: przeregulowanie, błąd ustalony

## Wymagania

- Python 3.11+

## Instalacja

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Uruchomienie

```bash
streamlit run app.py
```

## Struktura projektu

```
.
├── app.py              # interfejs Streamlit
├── pid_controller.py   # regulator PID
├── plant.py            # model obiektu termicznego
├── simulation.py       # pętla symulacji
├── requirements.txt
└── README.md
```

## Licencja

MIT
