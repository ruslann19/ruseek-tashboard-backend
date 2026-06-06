import html
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup


def get_raw_text(url: str) -> str:
    raw_html = load_html(url)

    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    post_message = query_params["p"][0]
    raw_text = extract_text_from_html_block(raw_html, post_message)
    return raw_text


def load_html(url: str) -> str:
    # Разбираем URL
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)

    # Проверка, что URL соответствует определённому домену
    if not (
        parsed.netloc in "www.forumsi.org"
        and parsed.path == "/showpost.php"
        and "p" in query_params
    ):
        raise ValueError(
            'URL должен соответствовать схеме: "http://www.forumsi.org/showpost.php?p=..."'
        )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # вызовет исключение при 4xx/5xx
        raw_html = response.text
        return raw_html
    except requests.exceptions.RequestException as error:
        raise Exception(f"Ошибка загрузки: {error}")


def extract_text_from_html_block(html_string, post_message):
    # Парсим HTML
    soup = BeautifulSoup(html_string, "html.parser")

    # Находим нужный блок по id
    id = f"post_message_{post_message}"
    block = soup.find("div", id=id)
    if not block:
        raise ValueError(f'Блок с id="{id}" не найден на странице')

    # Заменяем <br> на '\n', чтобы сохранить разрывы строк
    for br in block.find_all("br"):
        br.replace_with("")

    # Получаем текст — удаляем лишние пробелы/отступы, но сохраняем '\n'
    text = block.get_text(separator="", strip=False)

    # Декодируем HTML-сущности (например, &nbsp; → пробел, &lt; → <)
    text = html.unescape(text)

    # Убираем лишние пустые строки (опционально)
    lines = [line.rstrip() for line in text.splitlines()]

    # Удаляем дублирующиеся пустые строки, оставляя по 1
    cleaned_lines = []
    prev_empty = False
    for line in lines:
        if line == "":
            if not prev_empty:
                cleaned_lines.append(line)
            prev_empty = True
        else:
            cleaned_lines.append(line)
            prev_empty = False

    return "\n".join(cleaned_lines)
