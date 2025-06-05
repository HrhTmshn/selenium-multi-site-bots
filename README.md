# Saucedemo Automation Bot

Автоматизация пользовательского взаимодействия на сайте [saucedemo.com](https://www.saucedemo.com) с помощью Selenium.

Проект написан на Python и предназначен для тестирования, отладки и демонстрации UI-функциональности интернет-магазина. Бот может логиниться под разными пользователями, сортировать товары, добавлять и удалять их из корзины, проходить оформление заказа и снимать скриншоты на каждом этапе.

---

### 🛠️ Стек технологий

- [Python 3.10+](https://www.python.org/downloads/)
- [undetected-chromedriver (uc)](https://pypi.org/project/undetected-chromedriver/) — обход антибот-защиты
- [Selenium WebDriver](https://pypi.org/project/selenium/)
- [Colorama](https://pypi.org/project/colorama/) — логирование
- Встроенные: `argparse`, `logging`, `pathlib`, `random` — для CLI, логов и утилит
---

### 🚀 Возможности

- Работа с прокси (в том числе headless)
- Логин под несколькими пользователями
- Сортировка товаров
- Добавление и удаление товаров из корзины
- Оформление заказа (полностью)
- Сохранение скриншотов по этапам (опционально)
- CLI-интерфейс

---

### 📦 Установка и запуск

1. Клонируйте репозиторий:

```bash
git clone https://github.com/yourname/saucedemo-bot.git
cd saucedemo-bot
```

2. Создайте и активируйте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # или .\venv\Scripts\activate на Windows
```

3. Установите зависимости:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Запуск с аргументами:

```bash
python run.py \
    --usernames standard_user problem_user \
    --use-headless \
    --final-screenshot \
    --proxy http://login:pass@ip:port
```

---

### ⚙️ Аргументы запуска

| Аргумент             | Описание                                               |
| -------------------- | ------------------------------------------------------ |
| `--usernames`        | Логины пользователей (через пробел или один логин)     |
| `--password`         | Пароль (по умолчанию: `secret_sauce`)                  |
| `--proxy`            | Прокси в формате `http://user:pass@ip:port`            |
| `--use-headless`     | Запуск браузера в headless-режиме                      |
| `--final-screenshot` | Сохранять финальные скриншоты                          |
| `--timeout`          | Таймаут ожидания элементов (по умолчанию: `10` секунд) |

---

### 🖼 Пример использования

```bash
python run.py --usernames standard_user visual_user --headless --screenshot
```

---

### 🧪 Поддерживаемые пользователи

- standard_user
- locked_out_user
- problem_user
- performance_glitch_user
- error_user
- visual_user

---

### ⚠️ Заметки

- Бот предназначен для демонстрации навыков автоматизации и тестирования.
- Использование в коммерческих или продакшн-целях не предполагается.
- Скрипт безопасен и не нарушает условий использования сайта saucedemo.com (сайт предоставлен как playground для QA- и Selenium-тестов).

---

### 📄 Лицензия

Проект распространяется **только в образовательных целях**.  
Любое коммерческое использование, распространение или модификация — **запрещены**.

Подробнее — в [LICENSE](./LICENSE).