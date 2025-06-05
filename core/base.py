import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from pathlib import Path
import time
import random
from core.logger import Log


class Base:
    def __init__(self, proxy: str | None, use_headless: bool, final_screenshot_required: bool, timeout: float):
        """
        Базовый класс для всех ботов. Создаёт директории, инициализирует логгер и драйвер.
        """
        self.PROJECT_ROOT = Path(__file__).resolve().parent.parent
        self.screenshot_path = self.PROJECT_ROOT / 'screenshots'
        self.screenshot_path.mkdir(parents=True, exist_ok=True)

        class_name = self.__class__.__name__
        self.log = Log(self.PROJECT_ROOT, class_name)

        self.proxy = proxy
        self.use_headless = use_headless
        self.final_screenshot_required = final_screenshot_required
        self.timeout = 2 * timeout if self.proxy else timeout
        self.driver = self._init_driver()

    def _init_driver(self):
        """
        Инициализирует undetected_chromedriver с заданными опциями.
        Учитывает режим headless и настройки прокси.
        """
        options = uc.ChromeOptions()

        if self.use_headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--start-maximized")
        
        # Используется всегда для защиты от сохранения сессий/куков
        options.add_argument("--incognito")

        if self.proxy:
            if "//" not in self.proxy:
                self.proxy = f"http://{self.proxy}"
            options.add_argument(f'--proxy-server={self.proxy}')

        driver = uc.Chrome(options=options)
        
        if not self.use_headless:
            driver.maximize_window()

        return driver

    def _wait_random_delay(self, min: float = 1, max: float = 3):
        """Случайная задержка между действиями, имитирует поведение человека."""
        delay = random.uniform(min, max)
        time.sleep(delay)

    def _click_like_human(self, element: WebElement):
        """
        Кликает по элементу, предварительно перемещая к нему курсор и делая паузу.
        """
        self._move_mouse_smoothly_to(element)
        self._wait_random_delay()

        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(element).click().perform()
        except Exception as e:
            raise RuntimeError("Ошибка при клике") from e

    def _move_mouse_smoothly_to(self, element: WebElement):
        """
        Плавно двигает мышку в центр элемента с помощью CDP.
        Полезно для обхода антибот-защиты.
        """
        rect = self.driver.execute_script("""
            const rect = arguments[0].getBoundingClientRect();
            return {x: rect.left + rect.width / 2, y: rect.top + rect.height / 2};
        """, element)

        self.log.log_info(f"Двигаем мышь в координаты: x={rect['x']}, y={rect['y']}")

        self.driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
            "type": "mouseMoved",
            "x": int(rect['x']),
            "y": int(rect['y']),
            "button": "none"
        })

    def _scroll_page(self, direction: str | None = None, method: str = 'mouse'):
        """
        Скроллирует страницу вверх/вниз по шагам, либо мышкой, либо клавишами.

        :param direction: 'up' | 'down' | None — в None пролистывает в обе стороны
        :param method: 'mouse' (по умолчанию) или 'keyboard'
        """
        directions = ['down', 'up'] if direction is None else [direction]

        for dir in directions:
            while True:
                current_pos = self.driver.execute_script("return window.scrollY")

                if method == 'mouse':
                    js = "window.scrollBy(0, 300);" if dir == 'down' else "window.scrollBy(0, -300);"
                    self.driver.execute_script(js)
                else:
                    key = Keys.PAGE_DOWN if dir == 'down' else Keys.PAGE_UP
                    ActionChains(self.driver).send_keys(key).perform()

                self._wait_random_delay(0.3, 0.7)

                new_pos = self.driver.execute_script("return window.scrollY")
                if abs(new_pos - current_pos) <= 0:
                    break

    def _input_text(self, element: WebElement, text: str):
        """
        Очищает поле и вводит текст, с логированием ошибок.
        """
        try:
            element.clear()
            element.send_keys(text)
        except Exception as e:
            self.log.log_error(f"Ошибка при вводе текста: {text}", e)