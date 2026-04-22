# Дашборды

Эта папка содержит материалы для визуализации проекта.

## Что внутри

- `figures/` - PNG-графики из Python EDA
- `powerbi_data/` - подготовленные CSV-датасеты для Power BI
- `product_analytics_dashboard.html` - статический dashboard для портфолио
- `screenshots/product_analytics_dashboard.png` - превью dashboard для README

## Как обновить dashboard

Если CSV-файлы в `powerbi_data/` изменились, пересоберите dashboard:

```bash
python scripts/build_portfolio_dashboard.py
```

## Power BI

Для ручной сборки dashboard в Power BI Desktop используйте файлы из `powerbi_data/`.

Подробная инструкция: `docs/powerbi_dashboard_guide.md`
