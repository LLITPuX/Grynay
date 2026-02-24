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
Виклич інструмент `mcp_falkordb_add_node` послідовно для кожного з трьох нових вузлів, передаючи їх атрибути (у словнику `node_data`), `day_id`, `time` та необхідні базові зв'язки (до конкретної `Session`, а також `FEEDBACK_ON` / `RESPONDS_TO` / `ANALYZES` та `NEXT` для хронологічного ланцюга).

**1. Feedback:**
- Атрибути: `id`, `text`.
- Зв'язки: `PART_OF` (target: Session), `FEEDBACK_ON` (target: ID попереднього Analysis або Response), `NEXT` (source_id: ID попереднього Analysis).

**2. Response:** 
- Атрибути: `id`, `name`, `author: 'Grynya'`, `summary`, `full_text` (ПОВНИЙ текст СЛОВО В СЛОВО), `type: 'text'`.
- Зв'язки: `PART_OF` (target: Session), `RESPONDS_TO` (target: Feedback), `NEXT` (source_id: Feedback).

**3. Analysis:**
- Атрибути: `id`, `name`, `type: 'response_analysis'`, `verdict`, `rules_used`, `errors`, `lessons`.
- Зв'язки: `PART_OF` (target: Session), `ANALYZES` (target: Response), `NEXT` (source_id: Response).

### Крок 2: Витяг та пакетне збереження сутностей (batch tools)
1. ОБОВ'ЯЗКОВО! Проаналізуй обмін репліками та витягни або онови УСІ релевантні сутності (`Entity` - не лише нові, а й ті що вже згадувалися).
2. Виклич інструмент `mcp_falkordb_batch_add_nodes`, передавши `node_type: "Entity"` та масив цих сутностей у параметр `nodes`.
3. Після цього виклич інструмент `mcp_falkordb_batch_link_nodes` передавши масив усіх релейшенів для сутностей: `INVOLVED_IN` (target: Session), `MENTIONS` (source: Feedback/Response/Analysis, target: Entity).

### Крок 3: Оновлення LAST_EVENT
Виклич інструмент `mcp_falkordb_update_last_event`, передавши `session_id` та `event_id` (ID щойно створеного Analysis-вузла).

**Виконання:** Поверни користувачу підтвердження "✅ Артефакти збережено [ID вузлів]".
