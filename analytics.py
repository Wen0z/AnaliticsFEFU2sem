import pandas as pd
import plotly.express as px


def read_dataset(uploaded_file):
    """
    Чтение CSV или Excel.
    """

    filename = uploaded_file.name.lower()

    if filename.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        df = pd.read_excel(uploaded_file)

    else:
        raise ValueError("Поддерживаются только CSV и Excel.")

    # Убираем лишние пробелы
    df.columns = df.columns.str.strip()

    return df


def get_dataset_info(df):
    """
    Основная информация о датасете.
    """

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "missing_values": int(df.isna().sum().sum()),
        "duplicates": int(df.duplicated().sum())
    }


def get_column_types(df):

    rows = []

    for column in df.columns:

        rows.append({
            "Столбец": column,
            "Тип": str(df[column].dtype),
            "Пропусков": int(df[column].isna().sum()),
            "Уникальных": int(df[column].nunique())
        })

    return pd.DataFrame(rows)

def create_basic_charts(df):
    """
    Автоматическое построение графиков.
    """

    charts = []

    # ---------- Топ блюд ----------

    if {"Item Name", "Quantity"}.issubset(df.columns):

        top_items = (
            df.groupby("Item Name")["Quantity"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        charts.append(
            px.bar(
                top_items,
                x="Item Name",
                y="Quantity",
                title="Топ-10 популярных блюд"
            )
        )

    # ---------- Выручка ----------

    if {
        "Item Name",
        "Quantity",
        "Product Price"
    }.issubset(df.columns):

        revenue = df.copy()

        revenue["Revenue"] = (
            revenue["Quantity"] *
            revenue["Product Price"]
        )

        revenue = (
            revenue.groupby("Item Name")["Revenue"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        charts.append(
            px.bar(
                revenue,
                x="Item Name",
                y="Revenue",
                title="Топ блюд по выручке"
            )
        )

    # ---------- Заказы по дням ----------

    if {
        "Order Date",
        "Order Number"
    }.issubset(df.columns):

        tmp = df.copy()

        tmp["Order Date"] = pd.to_datetime(
            tmp["Order Date"],
            errors="coerce"
        )

        daily = (
            tmp.groupby(
                tmp["Order Date"].dt.date
            )["Order Number"]
            .nunique()
            .reset_index()
        )

        daily.columns = [
            "Дата",
            "Заказы"
        ]

        charts.append(
            px.line(
                daily,
                x="Дата",
                y="Заказы",
                title="Количество заказов по дням"
            )
        )

    return charts

def prepare_summary_for_llm(df):
    """
    Формирование подробной сводки о датасете.
    """

    summary = []

    summary.append("=== ОБЩАЯ ИНФОРМАЦИЯ ===\n")

    summary.append(f"Количество строк: {len(df)}")
    summary.append(f"Количество столбцов: {len(df.columns)}")

    summary.append("\nСтолбцы:")

    for column in df.columns:

        summary.append(
            f"- {column}: {df[column].dtype}"
        )

    summary.append("\nКоличество пропусков:")

    summary.append(
        df.isna().sum().to_string()
    )

    summary.append("\n")

    summary.append("=== ПЕРВЫЕ СТРОКИ ===\n")

    summary.append(
        df.head(15).to_string(index=False)
    )

    summary.append("\n")

    summary.append("=== ОПИСАТЕЛЬНАЯ СТАТИСТИКА ===\n")

    summary.append(
        df.describe(include="all").to_string()
    )

    summary.append("\n")

    # Если это ресторанный датасет —
    # добавляем специальную аналитику

    if {
        "Quantity",
        "Product Price"
    }.issubset(df.columns):

        revenue = (
            df["Quantity"] *
            df["Product Price"]
        )

        summary.append(
            f"\nОбщая выручка: {revenue.sum():.2f}"
        )

    if "Order Number" in df.columns:

        summary.append(
            f"\nКоличество заказов: "
            f"{df['Order Number'].nunique()}"
        )

    if "Item Name" in df.columns:

        summary.append("\nТоп блюд:")

        summary.append(
            df["Item Name"]
            .value_counts()
            .head(10)
            .to_string()
        )

    return "\n".join(summary)

