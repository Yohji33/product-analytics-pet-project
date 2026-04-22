from pathlib import Path
from html import escape

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "dashboards" / "powerbi_data"
DASHBOARDS_DIR = ROOT_DIR / "dashboards"
SCREENSHOTS_DIR = DASHBOARDS_DIR / "screenshots"


BG = "#f3efe6"
CARD = "#fffaf0"
INK = "#17212b"
MUTED = "#69747e"
GRID = "#e5dac8"
ORANGE = "#d76f36"
TEAL = "#197b72"
BLUE = "#436f9f"
YELLOW = "#e4af45"
RED = "#bb4d3e"


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / name)


def fmt_int(value: float) -> str:
    return f"{value:,.0f}".replace(",", " ")


def fmt_money(value: float) -> str:
    return f"{value:,.0f}".replace(",", " ")


def fmt_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def fmt_ratio(value: float) -> str:
    return f"{value:.2f}x"


def add_panel(fig, rect, title=None):
    ax = fig.add_axes(rect)
    ax.set_facecolor(CARD)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=0.8, alpha=0.85)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.title.set_color(INK)
    ax.title.set_fontweight("bold")
    if title:
        ax.set_title(title, loc="left", pad=12, fontsize=12)

    patch = FancyBboxPatch(
        (rect[0], rect[1]),
        rect[2],
        rect[3],
        boxstyle="round,pad=0.012,rounding_size=0.02",
        transform=fig.transFigure,
        facecolor=CARD,
        edgecolor="#eadfce",
        linewidth=1.0,
        zorder=-1,
    )
    fig.patches.append(patch)
    return ax


def add_card(fig, rect, label, value, note, color):
    ax = fig.add_axes(rect)
    ax.axis("off")
    patch = FancyBboxPatch(
        (0, 0),
        1,
        1,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        transform=ax.transAxes,
        facecolor=CARD,
        edgecolor="#eadfce",
        linewidth=1.0,
    )
    ax.add_patch(patch)
    ax.add_patch(
        FancyBboxPatch(
            (0.05, 0.15),
            0.025,
            0.7,
            boxstyle="round,pad=0.004,rounding_size=0.02",
            transform=ax.transAxes,
            facecolor=color,
            edgecolor=color,
        )
    )
    ax.text(0.11, 0.70, label, color=MUTED, fontsize=9, fontweight="bold", transform=ax.transAxes)
    ax.text(0.11, 0.36, value, color=INK, fontsize=20, fontweight="bold", transform=ax.transAxes)
    ax.text(0.11, 0.14, note, color=MUTED, fontsize=8, transform=ax.transAxes)


def build_png(kpi, monthly, funnel, marketing_efficiency, ltv_by_channel, repeat_summary, ab_test_results, categories, top_products):
    plt.rcParams["font.family"] = "DejaVu Sans"
    fig = plt.figure(figsize=(16, 12), dpi=160)
    fig.patch.set_facecolor(BG)

    fig.text(0.04, 0.965, "Product Analytics Dashboard", fontsize=24, fontweight="bold", color=INK)
    fig.text(
        0.04,
        0.94,
        "Синтетические данные e-commerce: выручка, воронка, CAC/ROMI, LTV и A/B-тест",
        fontsize=10,
        color=MUTED,
    )

    add_card(fig, [0.04, 0.83, 0.21, 0.085], "Выручка", fmt_money(kpi["Выручка"]), "за весь период", ORANGE)
    add_card(fig, [0.275, 0.83, 0.21, 0.085], "Оплаченные заказы", fmt_int(kpi["Оплаченные заказы"]), "успешные покупки", TEAL)
    add_card(fig, [0.51, 0.83, 0.21, 0.085], "Средний чек", fmt_money(kpi["Средний чек"]), "выручка / заказы", BLUE)
    add_card(fig, [0.745, 0.83, 0.21, 0.085], "Конверсия", fmt_percent(kpi["Конверсия сессии в заказ"]), "сессия -> заказ", YELLOW)

    monthly = monthly.copy()
    monthly["month"] = pd.to_datetime(monthly["month"])
    monthly["month_label"] = monthly["month"].dt.strftime("%b")
    ax = add_panel(fig, [0.04, 0.60, 0.57, 0.19], "Выручка по месяцам")
    ax.bar(monthly["month_label"], monthly["revenue"], color=ORANGE, alpha=0.82)
    ax.plot(monthly["month_label"], monthly["revenue"], color=INK, linewidth=1.8, marker="o", markersize=4)
    ax.set_ylabel("Выручка", color=MUTED, fontsize=8)
    ax.grid(axis="x", visible=False)
    best = monthly.loc[monthly["revenue"].idxmax()]
    ax.annotate(
        f"пик: {fmt_money(best['revenue'])}",
        xy=(best["month_label"], best["revenue"]),
        xytext=(0, 18),
        textcoords="offset points",
        ha="center",
        color=INK,
        fontsize=8,
        arrowprops={"arrowstyle": "->", "color": MUTED, "lw": 0.8},
    )

    funnel = funnel.copy()
    event_labels = {"view_item": "Просмотр", "add_to_cart": "Корзина", "purchase": "Покупка"}
    funnel["event_label"] = funnel["event_type"].map(event_labels).fillna(funnel["event_type"])
    funnel = funnel.sort_values("step_order")
    ax = add_panel(fig, [0.65, 0.60, 0.305, 0.19], "Воронка пользователей")
    ax.barh(funnel["event_label"], funnel["users_count"], color=[BLUE, TEAL, ORANGE], alpha=0.9)
    ax.invert_yaxis()
    ax.grid(axis="x", color=GRID)
    ax.grid(axis="y", visible=False)
    for _, row in funnel.iterrows():
        ax.text(row["users_count"] + 8, row["event_label"], fmt_int(row["users_count"]), va="center", fontsize=9, color=INK)
    ax.set_xlim(0, funnel["users_count"].max() * 1.22)

    marketing = marketing_efficiency.sort_values("romi")
    ax = add_panel(fig, [0.04, 0.36, 0.285, 0.19], "ROMI по каналам")
    ax.barh(marketing["acquisition_channel"], marketing["romi"], color=TEAL, alpha=0.9)
    ax.grid(axis="x", color=GRID)
    ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(lambda value, _: f"{value * 100:.0f}%")
    for y, value in enumerate(marketing["romi"]):
        ax.text(value + 0.12, y, fmt_percent(value), va="center", fontsize=7.5, color=INK)
    ax.set_xlim(0, marketing["romi"].max() * 1.25)

    cac = marketing_efficiency.sort_values("cac", ascending=False)
    ax = add_panel(fig, [0.365, 0.36, 0.255, 0.19], "CAC по каналам")
    ax.barh(cac["acquisition_channel"], cac["cac"], color=[RED, ORANGE, BLUE, TEAL, YELLOW], alpha=0.9)
    ax.grid(axis="x", color=GRID)
    ax.grid(axis="y", visible=False)
    for y, value in enumerate(cac["cac"]):
        ax.text(value + 8, y, fmt_money(value), va="center", fontsize=7.5, color=INK)
    ax.set_xlim(0, cac["cac"].max() * 1.28)

    categories = categories.sort_values("revenue")
    ax = add_panel(fig, [0.66, 0.36, 0.295, 0.19], "Выручка по категориям")
    ax.barh(categories["category"], categories["revenue"], color=BLUE, alpha=0.9)
    ax.grid(axis="x", color=GRID)
    ax.grid(axis="y", visible=False)
    for y, value in enumerate(categories["revenue"]):
        ax.text(value + 1400, y, fmt_money(value), va="center", fontsize=7.5, color=INK)
    ax.set_xlim(0, categories["revenue"].max() * 1.27)

    ltv = ltv_by_channel.sort_values("ltv_cac_ratio")
    ax = add_panel(fig, [0.04, 0.13, 0.285, 0.18], "LTV/CAC по каналам")
    ax.barh(ltv["acquisition_channel"], ltv["ltv_cac_ratio"], color=BLUE, alpha=0.9)
    ax.grid(axis="x", color=GRID)
    ax.grid(axis="y", visible=False)
    for y, value in enumerate(ltv["ltv_cac_ratio"]):
        ax.text(value + 0.12, y, fmt_ratio(value), va="center", fontsize=7.5, color=INK)
    ax.set_xlim(0, ltv["ltv_cac_ratio"].max() * 1.25)

    repeat_metrics = repeat_summary.set_index("metric")["value"].to_dict()
    ax = add_panel(fig, [0.365, 0.13, 0.255, 0.18], "Повторные покупки")
    labels = ["Покупатели", "Повторные"]
    values = [repeat_metrics["Покупатели"], repeat_metrics["Повторные покупатели"]]
    bars = ax.bar(labels, values, color=[TEAL, ORANGE], alpha=0.9)
    ax.grid(axis="x", visible=False)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 5, fmt_int(value), ha="center", fontsize=8, color=INK)
    ax.set_ylim(0, max(values) * 1.25)

    ab = ab_test_results.sort_values("variant")
    ax = add_panel(fig, [0.66, 0.13, 0.295, 0.18], "A/B-тест CTA")
    bars = ax.bar(ab["variant"], ab["conversion_rate"], color=[BLUE, ORANGE], alpha=0.9)
    ax.yaxis.set_major_formatter(lambda value, _: f"{value * 100:.0f}%")
    ax.grid(axis="x", visible=False)
    for bar, value in zip(bars, ab["conversion_rate"]):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.008, fmt_percent(value), ha="center", fontsize=8, color=INK)
    ax.set_ylim(0, ab["conversion_rate"].max() * 1.35)

    top = top_products.sort_values("revenue", ascending=False).head(3)
    best_romi = marketing_efficiency.sort_values("romi", ascending=False).iloc[0]
    test_row = ab_test_results.loc[ab_test_results["variant"] == "test"].iloc[0]
    insights = [
        f"Лидер по выручке: {top.iloc[0]['product_name']} ({fmt_money(top.iloc[0]['revenue'])})",
        f"Лучший ROMI: {best_romi['acquisition_channel']} ({fmt_percent(best_romi['romi'])})",
        f"A/B-тест: test +{fmt_percent(test_row['absolute_uplift'])} к конверсии, p-value {test_row['p_value']:.3f}",
    ]
    fig.text(0.04, 0.06, "Короткие выводы", fontsize=13, fontweight="bold", color=INK)
    for index, insight in enumerate(insights):
        fig.text(0.055, 0.038 - index * 0.018, f"{index + 1}. {insight}", fontsize=9.5, color=MUTED)
    fig.text(0.74, 0.025, "Источник: CSV-витрины из dashboards/powerbi_data", fontsize=8, color=MUTED)

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = SCREENSHOTS_DIR / "product_analytics_dashboard.png"
    fig.savefig(output_path, facecolor=BG, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    return output_path


def bar_rows(df, label_col, value_col, formatter, limit=None, ascending=False):
    data = df.sort_values(value_col, ascending=ascending)
    if limit:
        data = data.head(limit)
    max_value = data[value_col].max()
    rows = []
    for _, row in data.iterrows():
        width = 100 * row[value_col] / max_value
        rows.append(
            f"""
            <div class="bar-row">
              <div class="bar-label">{escape(str(row[label_col]))}</div>
              <div class="bar-track"><div class="bar-fill" style="width: {width:.1f}%"></div></div>
              <div class="bar-value">{escape(formatter(row[value_col]))}</div>
            </div>
            """
        )
    return "\n".join(rows)


def metric_rows(metric_dict, rows):
    return "\n".join(
        f"""
        <div class="metric-line">
          <span>{escape(label)}</span>
          <b>{escape(formatter(metric_dict[metric]))}</b>
        </div>
        """
        for metric, label, formatter in rows
    )


def build_html(
    kpi,
    monthly,
    funnel,
    channels,
    marketing_efficiency,
    ltv_by_channel,
    repeat_summary,
    ab_test_results,
    devices,
    categories,
    top_products,
):
    monthly = monthly.copy()
    monthly["month"] = pd.to_datetime(monthly["month"])
    monthly["month_label"] = monthly["month"].dt.strftime("%b")
    monthly_max = monthly["revenue"].max()
    monthly_bars = "\n".join(
        f"""
        <div class="month-bar">
          <div class="month-value" style="height: {100 * row['revenue'] / monthly_max:.1f}%"></div>
          <span>{escape(row['month_label'])}</span>
        </div>
        """
        for _, row in monthly.iterrows()
    )

    funnel = funnel.sort_values("step_order").copy()
    event_labels = {"view_item": "Просмотр", "add_to_cart": "Корзина", "purchase": "Покупка"}
    funnel["event_label"] = funnel["event_type"].map(event_labels).fillna(funnel["event_type"])
    funnel_max = funnel["users_count"].max()
    funnel_rows = "\n".join(
        f"""
        <div class="funnel-row">
          <span>{escape(row['event_label'])}</span>
          <div class="funnel-track"><div class="funnel-fill" style="width: {100 * row['users_count'] / funnel_max:.1f}%"></div></div>
          <b>{fmt_int(row['users_count'])}</b>
        </div>
        """
        for _, row in funnel.iterrows()
    )
    repeat_metrics = repeat_summary.set_index("metric")["value"].to_dict()
    repeat_rows = metric_rows(
        repeat_metrics,
        [
            ("Повторные покупатели", "Повторные покупатели", fmt_int),
            ("Доля повторных покупателей", "Repeat purchase rate", fmt_percent),
            ("LTV на пользователя", "LTV на пользователя", fmt_money),
            ("LTV на покупателя", "LTV на покупателя", fmt_money),
        ],
    )

    html = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Product Analytics Dashboard</title>
  <style>
    :root {{
      --bg: #f3efe6;
      --card: #fffaf0;
      --ink: #17212b;
      --muted: #69747e;
      --line: #eadfce;
      --orange: #d76f36;
      --teal: #197b72;
      --blue: #436f9f;
      --yellow: #e4af45;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background:
        radial-gradient(circle at top left, rgba(215,111,54,.24), transparent 26rem),
        radial-gradient(circle at bottom right, rgba(25,123,114,.18), transparent 28rem),
        var(--bg);
      color: var(--ink);
      font-family: "Segoe UI", Arial, sans-serif;
    }}
    main {{ max-width: 1280px; margin: 0 auto; padding: 42px 28px 52px; }}
    header {{ display: flex; justify-content: space-between; gap: 24px; align-items: end; margin-bottom: 24px; }}
    h1 {{ margin: 0; font-size: 42px; letter-spacing: -.04em; }}
    h2 {{ margin: 0 0 16px; font-size: 18px; }}
    p {{ color: var(--muted); line-height: 1.5; }}
    .subtitle {{ max-width: 720px; margin: 8px 0 0; }}
    .badge {{ border: 1px solid var(--line); background: rgba(255,250,240,.72); padding: 10px 14px; border-radius: 999px; color: var(--muted); white-space: nowrap; }}
    .grid {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 18px; }}
    .card {{
      background: rgba(255,250,240,.9);
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 22px;
      box-shadow: 0 18px 48px rgba(23,33,43,.07);
    }}
    .kpi {{ grid-column: span 3; min-height: 138px; position: relative; overflow: hidden; }}
    .kpi:before {{ content: ""; position: absolute; inset: 0 auto 0 0; width: 8px; background: var(--accent); }}
    .kpi span {{ color: var(--muted); font-size: 13px; font-weight: 700; }}
    .kpi strong {{ display: block; margin-top: 14px; font-size: 34px; letter-spacing: -.03em; }}
    .kpi small {{ display: block; color: var(--muted); margin-top: 8px; }}
    .wide {{ grid-column: span 7; }}
    .side {{ grid-column: span 5; }}
    .third {{ grid-column: span 4; }}
    .bars {{ height: 270px; display: flex; gap: 10px; align-items: end; padding-top: 20px; border-bottom: 1px solid var(--line); }}
    .month-bar {{ flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: end; align-items: center; gap: 8px; color: var(--muted); font-size: 12px; }}
    .month-value {{ width: 100%; min-height: 8px; border-radius: 12px 12px 4px 4px; background: linear-gradient(180deg, var(--orange), #b9562a); }}
    .funnel-row, .bar-row {{ display: grid; grid-template-columns: 110px 1fr 86px; gap: 12px; align-items: center; margin: 13px 0; }}
    .funnel-track, .bar-track {{ height: 18px; border-radius: 999px; background: #eadfce; overflow: hidden; }}
    .funnel-fill, .bar-fill {{ height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--teal), var(--orange)); }}
    .bar-label, .funnel-row span {{ color: var(--muted); font-weight: 700; }}
    .bar-value, .funnel-row b {{ text-align: right; }}
    .metric-line {{ display: flex; justify-content: space-between; gap: 16px; padding: 11px 0; border-bottom: 1px solid var(--line); color: var(--muted); }}
    .metric-line b {{ color: var(--ink); }}
    .notes {{ grid-column: span 12; display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
    .note {{ background: rgba(23,33,43,.92); color: white; border-radius: 22px; padding: 20px; }}
    .note b {{ color: #ffd88b; }}
    @media (max-width: 900px) {{
      .kpi, .wide, .side, .third, .notes {{ grid-column: span 12; }}
      .notes {{ grid-template-columns: 1fr; }}
      header {{ display: block; }}
    }}
  </style>
</head>
<body>
<main>
  <header>
    <div>
      <h1>Product Analytics Dashboard</h1>
      <p class="subtitle">Учебная аналитическая витрина по e-commerce: KPI, динамика выручки, воронка и сегменты, которые помогают понять, где продукт зарабатывает и где теряет пользователей.</p>
    </div>
    <div class="badge">CSV -> Python -> Dashboard</div>
  </header>

  <section class="grid">
    <article class="card kpi" style="--accent: var(--orange)"><span>Выручка</span><strong>{fmt_money(kpi["Выручка"])}</strong><small>за весь период</small></article>
    <article class="card kpi" style="--accent: var(--teal)"><span>Оплаченные заказы</span><strong>{fmt_int(kpi["Оплаченные заказы"])}</strong><small>успешные покупки</small></article>
    <article class="card kpi" style="--accent: var(--blue)"><span>Средний чек</span><strong>{fmt_money(kpi["Средний чек"])}</strong><small>выручка / заказы</small></article>
    <article class="card kpi" style="--accent: var(--yellow)"><span>Конверсия</span><strong>{fmt_percent(kpi["Конверсия сессии в заказ"])}</strong><small>сессия -> заказ</small></article>

    <article class="card wide">
      <h2>Выручка по месяцам</h2>
      <div class="bars">{monthly_bars}</div>
    </article>

    <article class="card side">
      <h2>Воронка пользователей</h2>
      {funnel_rows}
    </article>

    <article class="card third">
      <h2>Выручка по каналам</h2>
      {bar_rows(channels, "acquisition_channel", "revenue", fmt_money)}
    </article>

    <article class="card third">
      <h2>ROMI по каналам</h2>
      {bar_rows(marketing_efficiency, "acquisition_channel", "romi", fmt_percent)}
    </article>

    <article class="card third">
      <h2>CAC по каналам</h2>
      {bar_rows(marketing_efficiency, "acquisition_channel", "cac", fmt_money, ascending=True)}
    </article>

    <article class="card third">
      <h2>LTV/CAC по каналам</h2>
      {bar_rows(ltv_by_channel, "acquisition_channel", "ltv_cac_ratio", fmt_ratio)}
    </article>

    <article class="card third">
      <h2>Конверсия по устройствам</h2>
      {bar_rows(devices, "device_type", "session_to_order_conversion", fmt_percent)}
    </article>

    <article class="card third">
      <h2>Выручка по категориям</h2>
      {bar_rows(categories, "category", "revenue", fmt_money)}
    </article>

    <article class="card wide">
      <h2>Топ товаров по выручке</h2>
      {bar_rows(top_products, "product_name", "revenue", fmt_money, limit=6)}
    </article>

    <article class="card side">
      <h2>Повторные покупки</h2>
      {repeat_rows}
    </article>

    <article class="card wide">
      <h2>A/B-тест CTA</h2>
      {bar_rows(ab_test_results, "variant", "conversion_rate", fmt_percent)}
    </article>

    <article class="card side">
      <h2>Что видно из данных</h2>
      <p>Лучший месяц по выручке - декабрь 2025. Самый сильный канал по выручке - referral, а по конверсии пользователя в покупателя выделяется email.</p>
      <p>Organic даёт лучший ROMI и LTV/CAC. Ads приносит продажи, но имеет самый дорогой CAC, поэтому бюджет стоит проверять осторожнее.</p>
      <p>В A/B-тесте тестовая CTA-кнопка показывает положительный uplift конверсии.</p>
    </article>

    <section class="notes">
      <div class="note"><b>Продукт:</b> воронка высокая, но этап корзина -> покупка всё равно стоит контролировать.</div>
      <div class="note"><b>Маркетинг:</b> referral и social дают максимум выручки, но organic лучше окупается по ROMI и LTV/CAC.</div>
      <div class="note"><b>Эксперимент:</b> test-вариант CTA можно раскатывать после проверки на большем трафике.</div>
    </section>
  </section>
</main>
</body>
</html>
"""
    output_path = DASHBOARDS_DIR / "product_analytics_dashboard.html"
    clean_html = "\n".join(line.rstrip() for line in html.splitlines()) + "\n"
    output_path.write_text(clean_html, encoding="utf-8")
    return output_path


def main():
    kpi = read_csv("kpi_overview.csv").set_index("metric")["value"].to_dict()
    monthly = read_csv("monthly_metrics.csv")
    funnel = read_csv("funnel.csv")
    channels = read_csv("acquisition_channel_metrics.csv")
    marketing_efficiency = read_csv("marketing_efficiency.csv")
    ltv_by_channel = read_csv("ltv_by_channel.csv")
    repeat_summary = read_csv("repeat_purchase_summary.csv")
    ab_test_results = read_csv("ab_test_results.csv")
    devices = read_csv("device_metrics.csv")
    categories = read_csv("category_revenue.csv")
    top_products = read_csv("top_products.csv")

    png_path = build_png(
        kpi,
        monthly,
        funnel,
        marketing_efficiency,
        ltv_by_channel,
        repeat_summary,
        ab_test_results,
        categories,
        top_products,
    )
    html_path = build_html(
        kpi,
        monthly,
        funnel,
        channels,
        marketing_efficiency,
        ltv_by_channel,
        repeat_summary,
        ab_test_results,
        devices,
        categories,
        top_products,
    )

    print(f"Dashboard image: {png_path}")
    print(f"Dashboard HTML: {html_path}")


if __name__ == "__main__":
    main()
