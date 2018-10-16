# Keklik API 

[![Build Status](https://travis-ci.com/kiryanenko/keklik-api.svg?branch=master)](https://travis-ci.com/kiryanenko/keklik-api)

**API:** http://api.keklik.xyz

**Dev API:** https://keklik-api.herokuapp.com

# WebSocket API

## Для ученика

1. Установить WebSocket соединение `ws://api.keklik.xyz`
2. Подписаться на обновления

    **Запрос:**
    
    ```json
    {
      "stream": "games",
      "payload": {
        "action": "subscribe",
        "pk": 1,
        "data": {
          "action": "update"
        }
      }
    }
    ```
    
    **Ответ:**
    
    ```json
    {
      "stream": "games", 
      "payload": {
        "errors": [], 
        "data": {"action": "update"}, 
        "action": "subscribe", 
        "response_status": 200, 
        "request_id": null
      }
    }
    ```
    
3. Присоединиться к игре

    **Запрос:**

    ```json
    {
      "stream": "games",
      "payload": {
        "action": "join",
        "pk": 1
      }
    }
    ```

    **Ответ:**
    
    ```json
    {
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
    }
    ```
    
4. 

## Для учителя


