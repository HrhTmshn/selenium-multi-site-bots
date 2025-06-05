from argparse import ArgumentParser
from bots.saucedemo_bot import SaucedemoBot

def parse_args():
    parser = ArgumentParser(description="Run Saucedemo automation bot.")

    parser.add_argument(
        "--usernames",
        nargs="+",
        help="Один или несколько логинов (по умолчанию: все доступные)",
        default=None
    )
    parser.add_argument(
        "--password",
        help="Пароль пользователя (по умолчанию: secret_sauce)",
        default="secret_sauce"
    )
    parser.add_argument(
        "--proxy",
        help="Прокси-сервер в формате http://user:pass@ip:port или ip:port",
        default=None
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Запуск в headless-режиме (без браузера)"
    )
    parser.add_argument(
        "--screenshot",
        action="store_true",
        help="Сохранять финальный скриншот после каждой сессии"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10,
        help="Таймаут ожидания элементов (секунды, по умолчанию: 10)"
    )

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    bot = SaucedemoBot(
        usernames=args.usernames,
        password=args.password,
        proxy=args.proxy,
        use_headless=args.headless,
        final_screenshot_required=args.screenshot,
        timeout=args.timeout
    )
    bot.run()