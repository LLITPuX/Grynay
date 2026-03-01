---
trigger: model_decision
description: Схема бази даних для графа Grynya_v2.0
globs: **/*.py, **/*.md, **/*.json
---

# Схема Графа Пам'яті "Grynya_v2.0"

Цей документ описує поточний стан схеми графа `Grynya_v2.0` для бази даних FalkorDB. Знімок зроблено 2026-03-01. Схема перебуває в активному рефакторингу.

## Вузли (Nodes)

Лише типи, що мають реальні екземпляри у графі.

| Тип вузла | Відомі атрибути | Екземпляри (`id` → `name` : `description`) |
| :--- | :--- | :--- |
| `:Year` | `id`, `name`, `value` | `year_2026` → `2026` |
| `:Day` | `id`, `name`, `date` | `d_2026_02_28` → `d_28` |
| `:Conceptions` | `id`, `name`, `description` | `id_agents` → `AGENTS` : "Перелік агентів що належать до екосистеми" |
| | | `id_agents_state` → `AGENTS_STATE` : "Стан агента що завантажується автоматично через МСР" |
| `:Agents` | `id`, `name`, `description` | `id_cursa4` → `Cursa4` : "Агент вбудований у Cursor IDE" |
| | | `id_clim` → `Clim` : "Нейронне ядро у LLM_provider_MCP" |
| `:SubConceptions` | `id`, `name`, `description` | `id_context` → `CONTEXT` : "Структурований опис останніх подій" |
| | | `id_tasks` → `TASKS` : "Перелік пріоритетних завдань" |
| | | `id_rules` → `RULES` : "Системні правила та директиви" |
| | | `id_pole` → `ROLE` : "Роль та Особистість" |
| | | `id_skills` → `SKILLS` : "Перелік навичок агентів" |

## Зв'язки (Relationships)

Лише ті, що мають реальні екземпляри у графі.

| Тип зв'язку | Від | До | Атрибути | Екземпляри |
| :--- | :--- | :--- | :--- | :--- |
| `[:MONTH]` | `:Year` | `:Day` | `number` (integer) | `year_2026` → `d_2026_02_28` (number: 2) |
| `[:REFERS_TO]` | `:Conceptions` | `:Agents` | `id` | `id_agents` → `id_cursa4` |
| | | | | `id_agents` → `id_clim` |
| `[:BLOCK_1]` | `:Conceptions` | `:SubConceptions` | — | `id_agents_state` → `id_pole` |
| `[:BLOCK_2]` | `:Conceptions` | `:SubConceptions` | `id` | `id_agents_state` → `id_rules` |
| `[:BLOCK_3]` | `:Conceptions` | `:SubConceptions` | — | `id_agents_state` → `id_tasks` |
| `[:BLOCK_4]` | `:Conceptions` | `:SubConceptions` | `id` | `id_agents_state` → `id_context` |
| `[:BLOCK_5]` | `:Conceptions` | `:SubConceptions` | `id` | `id_agents_state` → `id_skills` |
