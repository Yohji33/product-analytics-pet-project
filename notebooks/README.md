# Notebooks

Эта папка используется для Python-анализа и Jupyter Notebook.

Основной notebook:

- `01_eda_analysis.ipynb`

Первый EDA-этап можно воспроизвести командой:

```bash
python notebooks/eda_analysis.py
```

Скрипт читает CSV-файлы из `data/sample/` и сохраняет графики в `dashboards/figures/`.

В EDA входят:

- выручка по месяцам
- продуктовая воронка
- выручка по категориям
- конверсия по устройствам
- LTV/CAC по каналам
- конверсия A/B-теста
