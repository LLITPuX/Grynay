# Протокол `/db` (Початок нової сесії)

Цей протокол використовується для ініціалізації нової гілки розмови.

**Тригер:** Команда `/db "текст запиту"` від користувача.
**Семантика:** `/db` відкриває нову сесію у графі `Grynya`.

## Твої дії (Формування JSON для `memory_bridge.py`)

Щоб відкрити сесію, ти маєш згенерувати JSON (згідно з `grynya-schema.md`) та передати його скрипту.

> [!CAUTION]
> **КРИТИЧНЕ ПРАВИЛО: `/db` = Request + Response + Analysis.**
> Протокол `/db` ЗАВЖДИ створює три вузли одночасно: `:Request`, `:Response` та `:Analysis`.
> Агент НІКОЛИ не може створити сесію без збереження своєї першої відповіді та аналізу.
> Якщо ти не створив Response і Analysis при `/db` — це помилка протоколу.

### Крок 0: Верифікація ланцюга сесій (ОБОВ'ЯЗКОВО)

Перед створенням нової сесії:
1. **Визнач ID останньої сесії** запитом до графа:
   ```powershell
   docker exec falkordb redis-cli GRAPH.QUERY Grynya "MATCH (s:Session) RETURN s.id ORDER BY s.id DESC LIMIT 1"
   ```
2. **Перевір інкрементальність:** Новий `session_ID` має бути послідовним (session_005 → session_006).
3. **Збережи ID попередньої сесії** — він потрібен для NEXT-зв'язку.

### Крок 1: Створи вузол `:Session`

Блок `session` в JSON з атрибутами `id`, `name`, `topic` (коротко), `status: 'active'`, `trigger: '/db'`.

### Крок 2: Створи вузол `:Request`

Збережи текст запиту від користувача.

### Крок 3: Створи вузол `:Response`

> [!IMPORTANT]
> **ОБОВ'ЯЗКОВО!** Збережи ПОВНИЙ текст своєї відповіді. Не відкладай це "на потім".

Атрибути: `id`, `name`, `author: 'Grynya'`, `summary` (коротко), `full_text` (ПОВНИЙ текст СЛОВО В СЛОВО), `type: 'text'`.

### Крок 4: Створи вузол `:Analysis`

> [!IMPORTANT]
> **ОБОВ'ЯЗКОВО!** Кожен Response має супроводжуватися Analysis.

Атрибути: `id`, `name`, `type: 'response_analysis'`, `verdict`, `rules_used`, `errors` (порожній масив якщо немає), `lessons`.
Зв'язки: `ANALYZES` → Response, `PART_OF` → Session.

### Крок 5: Витягни сутності (`:Entity`)

Уважно проаналізуй запит користувача ТА свою відповідь. Витягни **УСІ** значущі концепції, технології чи правила.

### Крок 6: Налаштуй Зв'язки (`relations`)

*   Request `PART_OF` Session.
*   Response `PART_OF` Session.
*   Response `RESPONDS_TO` Request.
*   Analysis `PART_OF` Session.
*   Analysis `ANALYZES` Response.
*   Session `INVOLVES` Entity.
*   Request, Response, Analysis `MENTIONS` Entity.

### Крок 7: Налаштуй Хронологію (`chronology`)

*   Вкажи поточний рік (`year`), дату (`date`), час (`time`).
*   Вкажи `day_id` (наприклад, `d_2026_02_22`).
*   Створи `next_links`:
    *   Від попередньої сесії (`session_X`) до нової (`session_Y`) — **використай ID з Кроку 0!**
    *   Від нової сесії до Request.
    *   Від Request до Response.
    *   Від Response до Analysis.
*   Онови `last_event_id` на ID Analysis (НЕ Response!).

**Виконання:** Передай JSON скрипту `memory_bridge.py` через `run_command`. 

> [!IMPORTANT]
> **Очищення:** Якщо використовувався тимчасовий файл, видали його одразу після завершення `run_command`.
