# Протокол `/sa` (Продовження сесії)

Цей протокол використовується для продовження відкритої теми.

**Тригер:** Команда `/sa "коментар"` від користувача.
**Семантика:** `/sa` продовжує активну сесію, зберігаючи логічний зв'язок з контекстом.

> [!CAUTION]
> **КРИТИЧНЕ ПРАВИЛО: `/sa` = Feedback + Response + Analysis.**
> Протокол `/sa` ЗАВЖДИ створює три вузли одночасно: `:Feedback`, `:Response` та `:Analysis`.
> Агент НІКОЛИ не може зберегти фідбек без своєї відповіді та аналізу.
> Analysis — це НЕ опція. Без нього хронологічний ланцюг розривається.

## Твої дії (Взаємодія з MCP)

Ти маєш використати нативні інструменти (tools) MCP-сервера для збереження трьох нових вузлів та оновлення графа.

### Крок 1: Збереження вузлів тріади (Feedback, Response, Analysis)
Виклич інструмент `mcp_falkordb_add_node` послідовно для кожного з трьох нових вузлів, передаючи їх атрибути, `day_id`, `time` та необхідні БАЗОВІ зв'язки (до `Session`, а також `FEEDBACK_ON`, `RESPONDS_TO`, `ANALYZES` через параметр `relations`).
> **УВАГА:** ЗАБОРОНЕНО передавати зв'язки `NEXT` через параметр `relations` інструменту `add_node`, оскільки він не підтримує `source_id` для вхідних ребер! Всі `NEXT` створюються окремим кроком 1.1.

**1. Feedback:**
- Атрибути: `id`, `text`.
- Зв'язки (у параметрі `relations`): `PART_OF` (target: Session), `FEEDBACK_ON` (target: ID попереднього Analysis або Response).

**2. Response:** 
- Атрибути: `id`, `name`, `author: 'Grynya'`, `summary`, `full_text` (ПОВНИЙ текст СЛОВО В СЛОВО), `type: 'text'`.
- Зв'язки (у параметрі `relations`): `PART_OF` (target: Session), `RESPONDS_TO` (target: Feedback).

**3. Analysis:**
- Атрибути: `id`, `name`, `type: 'response_analysis'`, `verdict`, `rules_used`, `errors`, `lessons`.
- Зв'язки (у параметрі `relations`): `PART_OF` (target: Session), `ANALYZES` (target: Response).

### Крок 1.1: Створення хронологічного ланцюжка `NEXT`
ОБОВ'ЯЗКОВО виклич інструмент `mcp_falkordb_batch_link_nodes` та передай масив зв'язків `NEXT`, явно вказуючи `source_id` та `target_id`:
1. Від попередньої події (`Analysis` або `Response` попереднього кроку) до щойно створеного `Feedback` (або `Response`, якщо фідбеку не було).
2. Від `Feedback` до `Response`.
3. Від `Response` до `Analysis`.

### Крок 2: Витяг та пакетне збереження сутностей (batch tools)
1. ОБОВ'ЯЗКОВО! Проаналізуй обмін репліками та витягни або онови УСІ релевантні сутності (`Entity` - не лише нові, а й ті що вже згадувалися).
2. Виклич інструмент `mcp_falkordb_batch_add_nodes`, передавши `node_type: "Entity"` та масив цих сутностей у параметр `nodes`.
3. Після цього виклич інструмент `mcp_falkordb_batch_link_nodes` передавши масив усіх релейшенів для сутностей: `INVOLVED_IN` (target: Session), `MENTIONS` (source: Feedback/Response/Analysis, target: Entity).

### Крок 3: Оновлення LAST_EVENT
Виклич інструмент `mcp_falkordb_update_last_event`, передавши `session_id` та `event_id` (ID щойно створеного Analysis-вузла).

**Виконання:** Поверни користувачу підтвердження "✅ Артефакти збережено [ID вузлів]".
