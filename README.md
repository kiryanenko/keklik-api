# Keklik API 

[![Build Status](https://travis-ci.com/kiryanenko/keklik-api.svg?branch=master)](https://travis-ci.com/kiryanenko/keklik-api)

**API:** http://api.keklik.xyz

**Dev API:** https://keklik-api.herokuapp.com

# WebSocket API

## Общий порядок

1. Установить WebSocket соединение `ws://api.keklik.xyz/?session_key=<КЛЮЧ_СЕССИИ>`
2. Подписаться на издателей *(подписки, события, экшены, сигналы)*

    **Запрос:**
    
    ```json
    {
      "stream": "games",
      "payload": {
        "action": "subscribe",
        "pk": 1,
        "data": {
          "action": "Название экшена"
        },
        "request_id": "Идентификатор запроса (не обязательно)"
      }
    }
    ```
    
    **Ответ:**
    
    ```json
    {
      "stream": "games", 
      "payload": {
        "errors": [], 
        "data": {"action": "Название экшена"}, 
        "action": "subscribe", 
        "response_status": 200, 
        "request_id": "Идентификатор запроса"
      }
    }
    ```
    
3. Следить за приходом сообщений от издателей *(событий)*

    **Ответ:**
    
    ```json
    {
      "stream": "games",
      "payload": {
        "action": "Название экшена",
        "pk": 1,
        "data": {}, 
        "model": "api.game"
      }
    }
    ```

## Экшены (запросы)

### Присоединиться к игре `join`

**Запрос:**

```json
{
  "stream": "games",
  "payload": {
    "action": "join",
    "pk": 1,
    "request_id": "Идентификатор запроса (не обязательно)"
  }
}
```

**Ответ:**

```json
{
  "stream": "games",
  "payload": {
    "errors": [], 
    "data": GAME_SNAPSHOT, 
    "action": "join", 
    "response_status": 200, 
    "request_id": "Идентификатор запроса"
  }
}
```

## Подписки

### 
    **Запрос:**

    ```json
    {
      "stream": "games",
      "payload": {
        "action": "join",
        "pk": 1,
        "request_id": "Идентификатор запроса (не обязательно)"
      }
    }
    ```

    **Ответ:**
    
    ```json
    {
      "stream": "games",
      "payload": {
        "errors": [], 
        "data": {
          "id": 1,
          "quiz": {
            "id": 1,
            "title": "string",
            "description": "string",
            "user": {
              "username": "string",
              "email": "user@example.com",
              "phone": "string",
              "last_name": "string",
              "first_name": "string",
              "patronymic": "string",
              "gender": "M",
              "birth_date": "2018-10-15",
              "rating": 1000
            },
            "tags": [
              "string"
            ],
            "questions": [
              {
                "id": 1,
                "number": 1,
                "type": "single",
                "question": "string",
                "variants": [
                  {
                    "id": 1,
                    "variant": "string"
                  }
                ],
                "answer": [1],
                "timer": 60,
                "points": 10
              }
            ],
            "rating": 1000,
            "version_date": "2018-10-15T22:09:17.751Z"
          },
          "title": "string",
          "user": {
            "username": "string",
            "email": "user@example.com",
            "phone": "string",
            "last_name": "string",
            "first_name": "string",
            "patronymic": "string",
            "gender": "M",
            "birth_date": "2018-10-15",
            "rating": 1000
          },
          "players": [
            {
              "id": 1,
              "user": {
                "username": "string",
                "email": "user@example.com",
                "phone": "string",
                "last_name": "string",
                "first_name": "string",
                "patronymic": "string",
                "gender": "M",
                "birth_date": "2018-10-15",
                "rating": 1000
              },
              "created_at": "2018-10-15T22:09:17.751Z",
              "finished_at": null
            }
          ],
          "online": true,
          "state": "players_waiting",
          "current_question": null,
          "timer_on": false,
          "timer": 60,
          "created_at": "2018-10-15T22:09:17.751Z",
          "updated_at": "2018-10-15T22:09:17.751Z",
          "finished_at": null
        }, 
        "action": "subscribe", 
        "response_status": 200, 
        "request_id": "Идентификатор запроса"
      }
    }
    ```
    
4. 

## Для учителя


