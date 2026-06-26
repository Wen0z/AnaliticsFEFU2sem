import streamlit as st

from analytics import (
    read_dataset,
    get_dataset_info,
    get_column_types,
    create_basic_charts,
    prepare_summary_for_llm,
)

from agent import generate_report


st.set_page_config(
    page_title="Restaurant Orders Analytics",
    page_icon="🍔",
    layout="wide"
)

st.title("🍔 Restaurant Orders Analytics with LLM")

st.markdown(
    """
Загрузите **CSV** или **Excel** файл с данными о заказах ресторана.

После загрузки приложение автоматически:

- исследует структуру датасета;
- строит основные графики;
- формирует сводку данных;
- отправляет результаты анализа в LLM через Groq API;
- получает аналитический отчет и рекомендации.
"""
)

uploaded_file = st.file_uploader(
    "Выберите CSV или Excel",
    type=["csv", "xlsx", "xls"]
)

user_instruction = st.text_area(
    "Инструкция для LLM",
    value="""Проанализируй данные заказов ресторана.

Определи наиболее популярные блюда.

Оцени продажи.

Выдели закономерности.

Сделай выводы.

Предложи рекомендации владельцу ресторана.
""",
    height=180
)

if uploaded_file is not None:

    try:

        df = read_dataset(uploaded_file)

        st.success("Датасет успешно загружен.")

        st.subheader("Предпросмотр данных")

        st.dataframe(
            df.head(20),
            width="stretch"
        )

        info = get_dataset_info(df)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Строк",
            info["rows"]
        )

        col2.metric(
            "Столбцов",
            info["columns"]
        )

        col3.metric(
            "Пропуски",
            info["missing_values"]
        )

        col4.metric(
            "Дубликаты",
            info["duplicates"]
        )

        st.divider()

        st.subheader("Типы данных")

        st.dataframe(
            get_column_types(df),
            width="stretch"
        )

        st.divider()

        st.subheader("Графики")

        charts = create_basic_charts(df)

        if charts:

            for chart in charts:

                chart.update_layout(height=450)

                st.plotly_chart(
                    chart,
                    width="stretch"
                )

        else:

            st.info(
                "Недостаточно данных для построения графиков."
            )

        st.divider()

        if st.button(
            "Запустить LLM-анализ",
            type="primary"
        ):

            with st.spinner("Подготовка данных..."):

                summary = prepare_summary_for_llm(df)

            with st.expander(
                "Сводка, передаваемая LLM"
            ):

                st.text(summary)

            with st.spinner(
                "LLM анализирует данные..."
            ):

                report = generate_report(
                    summary,
                    user_instruction
                )

            st.divider()

            st.subheader("📊 Аналитический отчет")

            st.markdown(report)

    except Exception as e:

        st.error(f"Ошибка: {e}")

else:

    st.info(
        "Загрузите файл для начала анализа."
    )