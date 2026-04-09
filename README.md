# Memoriki

Персональная база знаний с настоящей памятью. Связка [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) (Andrej Karpathy) + [MemPalace](https://github.com/milla-jovovich/mempalace) (MCP-сервер).

Wiki дает структуру. MemPalace дает память.

## Проблема

- **LLM Wiki без MemPalace** = библиотека без каталога. Поиск - только grep по словам.
- **MemPalace без Wiki** = поисковик без книг. Семантический поиск по куче сырых обрывков.
- **Вместе** = структурированные знания + семантический поиск + граф связей.

## Три слоя знаний

| Слой | Что делает | Инструмент |
|------|-----------|------------|
| **Wiki** | Структура, [[wiki-links]], YAML frontmatter, index | Markdown + Obsidian |
| **MemPalace Drawers** | Семантический поиск по содержимому | `mempalace_search` |
| **MemPalace KG** | Граф связей между сущностями с датами | `mempalace_kg_query` |

## Архитектура

```
memoriki/
  raw/                    # Твои источники (статьи, заметки, транскрипты)
  wiki/                   # LLM-генерируемая wiki
    index.md              # Каталог всех страниц
    log.md                # Лог операций (append-only)
    entities/             # Люди, компании, продукты
    concepts/             # Идеи, паттерны, фреймворки
    sources/              # Саммари каждого источника
    synthesis/            # Кросс-анализ, сравнения
  mempalace.yaml          # Конфигурация MemPalace
  CLAUDE.md               # Схема и правила для LLM
  idea-file.md            # Оригинальная идея Karpathy (reference)
```

## Быстрый старт

```bash
# 1. Склонировать
git clone https://github.com/AyanbekDos/memoriki.git my-knowledge-base
cd my-knowledge-base

# 2. Установить MemPalace
pip install mempalace
mempalace init .

# 3. Подключить MemPalace к Claude Code
claude mcp add mempalace -- python -m mempalace.mcp_server

# 4. Положить первый источник
cp ~/some-article.md raw/

# 5. Запустить Claude Code и начать ingest
claude
# > Прочитай raw/some-article.md и разложи по wiki
```

## Операции

- **Ingest** - кинуть файл в `raw/`, сказать LLM прочитать и разложить по wiki
- **Query** - задать вопрос, LLM найдет страницы и синтезирует ответ
- **Lint** - проверка здоровья: противоречия, сироты, пробелы в знаниях

## Совместимость

Работает с любым LLM-агентом, поддерживающим MCP:
- **Claude Code** - используй `CLAUDE.md`
- **OpenAI Codex** - переименуй `CLAUDE.md` в `AGENTS.md`
- **Cursor, Gemini CLI** и другие MCP-совместимые

## Примеры использования

- **Стартапер**: customer discovery, интервью, конкуренты, пивоты - все в одном месте
- **Исследователь**: статьи, papers, заметки - wiki с синтезом накапливает знания
- **Студент**: конспекты лекций, книги, проекты - структурированная "вторая память"
- **Команда**: Slack-треды, созвоны, решения - wiki которую ведет AI

## License

MIT

## Credits

- [Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) - оригинальная идея LLM Wiki
- [MemPalace](https://github.com/milla-jovovich/mempalace) - MCP-сервер для семантического поиска и графа знаний
- [Claude Code](https://claude.com/claude-code) - LLM-агент
