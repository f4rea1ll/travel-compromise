# API Contract — Travel Compromise

Base URL (dev): `http://localhost:8000`

## POST /session/create
Создаёт новую сессию на двоих.

**Response 200:**
```json
{
  "session_id": "a1b2c3d4",
  "participant_1_link": "/session/a1b2c3d4/join/1",
  "participant_2_link": "/session/a1b2c3d4/join/2"
}
```

## POST /session/{session_id}/join/{participant_number}
Отправка данных одного участника. `participant_number` — 1 или 2.

**Request body:**
```json
{
  "origin_city": "Москва",
  "budget": 15000,
  "vibe_tags": ["chill", "food"],
  "must_haves": ["no_transfers"],
  "departure_date": "2026-09-05",
  "return_date": "2026-09-07"
}
```
`vibe_tags` — из списка: `chill`, `adventure`, `culture`, `food`, `nature`, `budget`
`must_haves` — из списка: `no_transfers`, `budget_stay`, `food_nearby`

**Response 200:**
```json
{"status": "ok", "message": "Данные участника 1 сохранены"}
```

## GET /session/{session_id}/status
Проверка, кто уже заполнил анкету (без раскрытия данных).

**Response 200:**
```json
{
  "session_id": "a1b2c3d4",
  "participant_1_submitted": true,
  "participant_2_submitted": false
}
```

## GET /session/{session_id}/result — В РАЗРАБОТКЕ (готово к ~15:00)
Вернёт топ-3 направления с разбивкой по каждому участнику. Структура ответа будет добавлена сюда по готовности.