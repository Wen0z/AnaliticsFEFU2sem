import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL = os.getenv("MODEL", "llama-3.3-70b-versatile")
API_KEY = os.getenv("GROQ_API_KEY")


def generate_report(summary: str, instruction: str) -> str:
    """
    Генерация аналитического отчета с помощью Groq.
    """

    if not API_KEY:
        raise ValueError(
            "Не найден GROQ_API_KEY в файле .env"
        )

    client = Groq(api_key=API_KEY)

    system_prompt = """
Ты опытный аналитик данных ресторанного бизнеса.

Тебе передается подробная информация о датасете заказов ресторана.

Твоя задача — провести анализ данных и подготовить аналитический отчет.

Не пересказывай полученные данные.

Сделай собственные выводы.

Ответ оформи в Markdown.

Используй следующую структуру.

# Общая характеристика данных

Кратко опиши датасет.

# Основные выводы

Перечисли самые важные закономерности.

# Инсайты

Найди интересные особенности данных.

# Возможные проблемы

Если они есть.

# Рекомендации

Предложи рекомендации владельцу ресторана.

Используй только данные, которые присутствуют в отчете.

Не придумывай информацию.
"""

    user_prompt = f"""
Инструкция пользователя:

{instruction}

Ниже приведены результаты автоматического анализа датасета.

{summary}

Подготовь подробный аналитический отчет.
"""

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return response.choices[0].message.content