# План Модернізації GraphRAG Скіллів

**Специфікація:** `docs/specs/2026-02-24-graphrag-skills-adaptation.md`
**Сесія планування:** session_006
**Дата створення:** 2026-02-24
**Виконавець:** Гриня (AI-агент)
**Оцінка трудовитрат:** ~12-16 годин (2-3 робочих сесії)

---

## Мета

Трансформувати два generic GraphRAG скілли в **вбудовані знання агента**, адаптовані під систему Grynya (FalkorDB, Docker, MCP, Cypher). Після модернізації будь-який LLM-агент, підключений до воркспейсу, зможе якісно будувати та оцінювати граф без додаткових інструкцій.

---

## Майлстоуни

| # | Майлстоун | Критерії Успіху |
|---|-----------|-----------------|
| M1 | Реструктуризація файлів | Generic ресурси ізольовані в `references/`, нова структура директорій створена |
| M2 | Grynya-specific ресурси | 4 нових файли створені, прив'язані до `grynya-schema.md` |
| M3 | SKILL.md переписані | Обидва SKILL.md українською, з Grynya-адаптованим workflow |
| M4 | Інтеграція та валідація | Cross-references з memory-manager, агент може пройти повний workflow |

---

## Фаза 1: Реструктуризація (M1) — ~1.5 год

**Мета:** Підготувати файлову структуру, ізолювати generic ресурси.

| # | Задача | Трудовитрати | Залежність | Критерії Виконання |
|---|--------|-------------|------------|-------------------|
| 1.1 | **Створити `references/` в обох скіллах** | 10 хв | — | Директорії існують |
| 1.2 | **Перемістити generic ресурси evaluation** | 15 хв | 1.1 | `methodology.md` та `reasoning-patterns.md` в `references/` |
| 1.3 | **Перемістити generic ресурси system-design** | 15 хв | 1.1 | `methodology.md`, `technology-stacks.md`, `domain-patterns.md` в `references/` |
| 1.4 | **Верифікувати evaluators/** | 10 хв | — | `rubric_evaluation.json` та `rubric_system_design.json` залишаються на місці |

**Деталі:**
- Evaluators залишаються в `resources/evaluators/` (universal, не потребують переміщення)
- Посилання в SKILL.md поки не оновлюємо — це буде у Фазі 3

### Поточна → Цільова структура

```
graphrag-evaluation/resources/           graphrag-evaluation/resources/
├── evaluators/                          ├── evaluators/
│   └── rubric_evaluation.json           │   └── rubric_evaluation.json
├── methodology.md          ──→          ├── grynya-methodology.md     (НОВЕ)
└── reasoning-patterns.md   ──→          ├── grynya-reasoning.md       (НОВЕ)
                                         └── references/
                                             ├── methodology.md
                                             └── reasoning-patterns.md

graphrag-system-design/resources/        graphrag-system-design/resources/
├── evaluators/                          ├── evaluators/
│   └── rubric_system_design.json        │   └── rubric_system_design.json
├── domain-patterns.md      ──→          ├── grynya-stack.md           (НОВЕ)
├── methodology.md          ──→          ├── grynya-patterns.md        (НОВЕ)
└── technology-stacks.md    ──→          └── references/
                                             ├── methodology.md
                                             ├── technology-stacks.md
                                             └── domain-patterns.md
```

---

## Фаза 2: Grynya-Specific Ресурси (M2) — ~6-8 год

**Мета:** Створити 4 адаптовані файли з прив'язкою до конкретної інфраструктури Grynya.

| # | Задача | Трудовитрати | Залежність | Критерії Виконання |
|---|--------|-------------|------------|-------------------|
| 2.1 | **Створити `grynya-methodology.md`** (evaluation) | 2 год | 1.2 | Як оцінювати граф Grynya: конкретні Cypher-запити, прив'язка до `grynya-schema.md`, чек-лист оцінки |
| 2.2 | **Створити `grynya-reasoning.md`** (evaluation) | 1.5 год | 1.2 | Патерни міркувань для графа пам'яті: temporal, session-based, entity-linking |
| 2.3 | **Створити `grynya-stack.md`** (system-design) | 1.5 год | 1.3 | Опис нашого стеку: FalkorDB (RedisGraph fork), Docker Compose, MCP bridge, Cypher, обмеження та можливості |
| 2.4 | **Створити `grynya-patterns.md`** (system-design) | 2 год | 1.3-2.3 | Патерн Activity-Centric Memory Agent, адаптований з Enterprise domain-patterns |

**Джерела для кожного файлу:**

| Файл | Основне джерело | Додаткові джерела |
|------|----------------|-------------------|
| `grynya-methodology.md` | `references/methodology.md` (фільтровано) | `grynya-schema.md`, результати аудиту (audit_2026-02-24) |
| `grynya-reasoning.md` | `references/reasoning-patterns.md` (фільтровано) | Хронологічна модель сесій, NEXT-ланцюги |
| `grynya-stack.md` | `references/technology-stacks.md` (FalkorDB секція) | Docker Compose конфіг, MCP спека |
| `grynya-patterns.md` | `references/domain-patterns.md` (Enterprise секція) | Поточна `grynya-schema.md`, протоколи `/db`, `/sa`, `/ss` |

**Обмеження:**
- Кожен файл **< 200 рядків**
- Мова: **українська** (крім code blocks)
- Жодних посилань на конкретний LLM або IDE

---

## Фаза 3: Переписування SKILL.md (M3) — ~3-4 год

**Мета:** Переписати обидва SKILL.md українською з адаптованим workflow.

| # | Задача | Трудовитрати | Залежність | Критерії Виконання |
|---|--------|-------------|------------|-------------------|
| 3.1 | **Переписати SKILL.md graphrag-evaluation** | 1.5 год | 2.1, 2.2 | Українською, workflow посилається на `grynya-methodology.md` та `grynya-reasoning.md`, generic у `references/` як "додаткове читання" |
| 3.2 | **Переписати SKILL.md graphrag-system-design** | 1.5 год | 2.3, 2.4 | Українською, workflow посилається на `grynya-stack.md` та `grynya-patterns.md` |
| 3.3 | **Адаптувати Output Templates (P1)** | 1 год | 3.1, 3.2 | Видалити нерелевантні секції (HIPAA, Pinecone), спростити під контекст Grynya |

**Ключові зміни в workflow:**

Було (generic):
```
Step 1: Identify Evaluation Scope → "Define what aspects..."
Step 3: Choose technology stack → "Consider Neo4j, Pinecone, LangChain..."
```

Стане (адаптовано):
```
Крок 1: Визначити Обсяг Оцінки → "Перевір grynya-schema.md, визнач які аспекти..."
Крок 3: Перевірити Стек → "Наш стек: FalkorDB + Docker + MCP (див. grynya-stack.md)"
```

---

## Фаза 4: Інтеграція та Валідація (M4) — ~1.5 год

**Мета:** Зв'язати все воєдино, валідувати результат.

| # | Задача | Трудовитрати | Залежність | Критерії Виконання |
|---|--------|-------------|------------|-------------------|
| 4.1 | **Додати cross-reference в `memory-manager` SKILL.md** | 15 хв | 3.1, 3.2 | Секція "Рекомендоване Читання" з посиланнями на graphrag-скілли |
| 4.2 | **Додати cross-reference між evaluation та system-design (P2)** | 15 хв | 3.1, 3.2 | Кожен скілл знає про інший |
| 4.3 | **Валідація: тестовий прохід evaluation** | 30 хв | 4.1 | Агент читає SKILL.md → виконує workflow → отримує результат без зовнішніх інструкцій |
| 4.4 | **Git commit & push** | 10 хв | 4.3 | Всі зміни зафіксовані |

---

## Карта Залежностей

```
1.1 ──→ 1.2 ──→ 2.1 ──→ 3.1 ──→ 4.1 ──→ 4.3 ──→ 4.4
 │              2.2 ──↗        4.2 ──↗
 └──→ 1.3 ──→ 2.3 ──→ 3.2 ──↗
              2.4 ──↗  3.3 ──↗
```

**Критичний шлях:** 1.1 → 1.2 → 2.1 → 3.1 → 4.1 → 4.3 → 4.4

---

## Ризики та Мітигація

| Ризик | Вплив | Імовірність | Мітигація |
|-------|-------|-------------|-----------|
| Grynya-specific файли перевищують 200 рядків | Середній | Середня | Виносити деталі в інлайн-коментарі у Cypher, уникати дублювання з schema |
| Втрата корисного generic контенту при адаптації | Середній | Низька | Generic залишається в `references/`, завжди доступний для глибшого аналізу |
| Розбіжність між schema та grynya-specific ресурсами | Високий | Низька | У кожному файлі — посилання на `grynya-schema.md` як source of truth |
| Контекстне перевантаження агента | Високий | Середня | Ізоляція generic в `references/`, Grynya-файли < 200 рядків |

---

## Пріоритети (за специфікацією)

### P0 — Фази 1-3 (обов'язково)
- [x] ~~Виправлення протоколів memory-manager~~ *(виконано до плану)*
- [ ] Реструктуризація файлів (1.1-1.4)
- [ ] 4 Grynya-specific ресурси (2.1-2.4)
- [ ] 2 SKILL.md переписані (3.1-3.2)
- [ ] Cross-reference в memory-manager (4.1)

### P1 — Частина Фази 3
- [ ] Адаптація Output Templates (3.3)

### P2 — Фаза 4
- [ ] Cross-reference між скіллами (4.2)
- [ ] Секція "Поточний стан Grynya" в ресурсах (може бути додана в 2.x)

---

## Порядок Виконання (Рекомендація)

**Сесія A** (~4 год): Фаза 1 + Задачі 2.1, 2.3 (структура + два основних ресурси)
**Сесія B** (~4 год): Задачі 2.2, 2.4 + Фаза 3 (решта ресурсів + SKILL.md)
**Сесія C** (~2 год): Фаза 4 (інтеграція, валідація, commit)

Або одна довга сесія з перервами. Порядок гнучкий, головне — дотримуватися залежностей.
