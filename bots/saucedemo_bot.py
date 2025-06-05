from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, NoAlertPresentException
from selenium.webdriver.remote.webelement import WebElement
import random
from core.base import Base


class SaucedemoBot(Base):
    def __init__(
            self,
            usernames: str | list = None,
            password: str = "secret_sauce",
            proxy: str | None = None,
            use_headless: bool = False,
            final_screenshot_required: bool = False,
            timeout: float = 10
        ):
        """
        Основной класс бота для сайта saucedemo.com

        :param usernames: Один логин или список логинов
        :param password: Пароль
        :param proxy: Прокси-сервер (если используется)
        :param use_headless: Запуск без UI
        :param final_screenshot_required: Делать ли финальный скриншот
        :param timeout: Таймаут ожидания элементов
        """
        super().__init__(
            proxy=proxy,
            use_headless=use_headless,
            final_screenshot_required=final_screenshot_required,
            timeout=timeout
        )
        usernames = usernames if usernames else [
            "standard_user", "locked_out_user", "problem_user",
             "performance_glitch_user", "error_user", "visual_user"
        ]
        self.usernames = [usernames] if isinstance(usernames, str) else usernames
        self.password = password

    def run(self):
        if self.proxy:
            self._check_proxy()
        for username in self.usernames:
            self.username = username
            success = self._login()

            if success:
                self._perform_post_login_actions()
            elif self.final_screenshot_required:
                self._save_screenshot("login_error")
        self.log.log_time("Общее время выполнения бота: ")
        self.driver.quit()

    def _save_screenshot(self, step : str = "finish"):
        """Сохраняет скриншот под осмысленным именем"""
        class_name = self.__class__.__name__.lower()
        username = self.username.lower()
        screenshot_name = f'{class_name}_{username}_{step.lower()}_{self.log.session_starttime.strftime("%Y_%m_%d_%H_%M_%S")}.png'
        screenshot_path = self.screenshot_path / screenshot_name
        self.driver.save_screenshot(str(screenshot_path))
        self.log.log_info(f"Скриншот сохранён:\n{screenshot_path}")

    def _check_proxy(self):
        """Проверка работоспособности прокси через сайт pool.proxyspace.pro"""
        try:
            self.log.log_info("Проверка прокси...")
            self.driver.get("https://pool.proxyspace.pro")
            proxy = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "pre"))).text.strip()
            self.log.log_info(f"Ваш прокси: {proxy}")
        except TimeoutException:
            self.log.log_error("Не удалось проверить прокси! Timeout.")
        except Exception as e:
            self.log.log_error("При проверке прокси произошла ошибка: ", e)

    def _login(self) -> bool:
        """Выполняет логин под текущим self.username"""
        self.log.log_info("Открытие сайта...")
        self.driver.get("https://www.saucedemo.com/")

        try:
            self.log.log_info(f"Производим логин юзера: {self.username}")
            username_label = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, "user-name")))
            password_label = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, "password")))
            login_button = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, "login-button")))
            self._input_text(username_label, self.username)
            self._input_text(password_label, self.password)
            self._click_like_human(login_button)
            self.log.log_info("Форма логина отправлена")

            error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".error-message-container.error")
            if error_elements:
                error_texts = error_elements[0].text.strip()
                raise ValueError(f"Ошибка при авторизации: {error_texts}")

            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "inventory_list")))
            self.log.log_info("Успешный вход.")
            return True
        except ValueError as e:
            self.log.log_error("", e)
            return False
        except Exception as e:
            self.log.log_error("Не удалось выполнить вход: ", e)
            return False

    def _perform_post_login_actions(self):
        """Последовательное выполнение всех этапов пользовательского взаимодействия после входа"""
        self.log.log_info("Производим имитацию пользователя на сайте.")
        self._apply_product_sorting()
        self._reset_application_state()
        self._open_cart_and_continue()
        self._click_each_product()
        self._process_cart_and_checkout()
        if self._fill_and_submit_order_form():
            if self._complete_checkout_step_two():
                self._complete_checkout_confirmation()
        self._perform_logout()

    def _apply_product_sorting(self):
        """Случайным образом применяет одну из сортировок товаров."""
        try:
            self._scroll_page('up')
            self.log.log_info("Применяем сортировку:")

            sort_element = WebDriverWait(self.driver, self.timeout/2).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product_sort_container")))
            self._click_like_human(sort_element)
            self.log.log_info("Открываем список")
            self._wait_random_delay(0.2, 0.5)

            span_locator = (By.CSS_SELECTOR, "span.active_option")
            current_span = self.driver.find_element(*span_locator)
            current_text = current_span.text.strip()

            select = Select(sort_element)
            all_options = select.options

            remaining_options = [opt for opt in all_options if opt.text.strip() != current_text]
            target_option = random.choice(remaining_options)
            target_text = target_option.text

            current_selected = select.first_selected_option.text
            max_attempts = len(all_options)
            attempts = 0
            self.log.log_info(f"Выбираем сортировку {target_text}")
            while current_selected != target_text and attempts < max_attempts:
                sort_element.send_keys(Keys.ARROW_DOWN)

                current_selected = select.first_selected_option.text
                attempts += 1

            sort_element.send_keys(Keys.ENTER)

            WebDriverWait(self.driver, self.timeout).until(lambda d: d.find_element(
                *span_locator).text.strip() != current_text)
            self.log.log_info(f"Выбрана сортировка: «{target_text}»")
        except UnexpectedAlertPresentException as e:
            try:
                alert = self.driver.switch_to.alert
                alert.accept()
            except NoAlertPresentException:
                pass
            finally:
                self.log.log_error("Не удалось выбрать сортировку! Alert.")
                self.log.log_warning(f"[ALERT] Обнаружен alert с текстом: «{e.alert_text}»")
        except TimeoutException:
            self.log.log_error("Не удалось выбрать сортировку! Timeout.")
        except Exception as e:
            self.log.log_error("При выборе сортировки произошла ошибка: ", e)

    def _reset_application_state(self):
        """Сбрасывает состояние приложения через меню"""
        try:
            self.log.log_info(f"Открываем меню")
            menu_btn = self.driver.find_element(By.ID, "react-burger-menu-btn")
            self._click_like_human(menu_btn)
            self._wait_random_delay()

            self.log.log_info(f"Нажимаем Reset App State")
            reset_btn = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.ID, "reset_sidebar_link")))
            self._click_like_human(reset_btn)
            self._wait_random_delay()
        except Exception as e:
            self.log.log_error(f"Ошибка при сбросе состояния приложения: ", e)

    def _open_cart_and_continue(self):
        """Открывает корзину, проверяет содержимое и возвращается назад"""
        try:
            self.log.log_info(f"Проверяем корзину")
            cart_icon = self.driver.find_element(By.CLASS_NAME, "shopping_cart_link")
            self._click_like_human(cart_icon)
            self._wait_random_delay()

            self._scroll_page('down')
            cart_count_elem = self.driver.find_elements(By.CLASS_NAME, "shopping_cart_badge")
            self.log.log_info(f"В корзине {cart_count_elem} товаров" if cart_count_elem else f"Корзина пуста")

            self.log.log_info(f"Выходим из корзины")
            continue_btn = self.driver.find_element(By.ID, "continue-shopping")
            self._click_like_human(continue_btn)
            self._wait_random_delay()
        except Exception as e:
            self.log.log_error(f"Произошла ошибка в корзине: ", e)

    def _click_each_product(self):
        """Проходит по каждому товару и добавляет в корзину, если ещё не добавлен."""
        products = self.driver.find_elements(By.CLASS_NAME, "inventory_item")
        for product in products:
            try:
                button = product.find_element(By.TAG_NAME, "button")
                if button.text.lower() == "add to cart":
                    name = product.find_element(By.CLASS_NAME, "inventory_item_name").text.strip()
                    self.log.log_info(f"Выбираем продукт: {name}")
                    self._click_like_human(button)
                    WebDriverWait(product, self.timeout/2).until(
                        lambda p: p.find_element(By.TAG_NAME, "button").text.lower().strip() == "remove")
            except TimeoutException:
                self.log.log_error(f"Выбрать продукт {name} не удалось!")
                continue
            except Exception as e:
                self.log.log_error(f"При выборе продукта {name} произошла ошибка: ", e)
                continue

    def _process_cart_and_checkout(self):
        """Удаляет случайные товары из корзины и начинает процесс оформления"""
        try:
            self.log.log_info(f"Проверяем корзину")
            cart_icon = self.driver.find_element(By.CLASS_NAME, "shopping_cart_link")
            cart_count_elem = cart_icon.find_element(By.CSS_SELECTOR, "span.shopping_cart_badge")
            count = int(cart_count_elem.text) if cart_count_elem else 0
            self._click_like_human(cart_icon)
            self._wait_random_delay()

            if count > 1:
                
                remove_items = self.driver.find_elements(By.CLASS_NAME, "cart_item")
                remove_count = random.randint(1, count - 1)
                to_remove = random.sample(remove_items, remove_count)
                for item in to_remove:
                    productname = item.find_element(By.CLASS_NAME, "inventory_item_name").text.strip()
                    btn = item.find_element(By.CLASS_NAME, "cart_button")
                    self.log.log_info(f"Удаляем ненужный товар: {productname}")
                    self._click_like_human(btn)
                    self._wait_random_delay()

            self._scroll_page('down')

            self.log.log_info(f"Нажимаем Checkout")
            checkout_btn = self.driver.find_element(By.ID, "checkout")
            self._click_like_human(checkout_btn)
            self._wait_random_delay()
        except Exception as e:
            self.log.log_error(f"Ошибка при обработке корзины: ", e)

    def _fill_and_submit_order_form(self) -> bool:
        """Заполняет форму заказа и переходит к следующему шагу"""
        try:
            firstname_label = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, "first-name")))
            lastname_label = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, "last-name")))
            postal_code_label = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, "postal-code")))
            continue_button = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, "continue")))

            firstname, lastname, postal_code = "Adam", "Tom", "123456"
            self.log.log_info(
                f"Заполняем заказ данными: First Name = {firstname}, Last Name = {lastname}, Postal Code = {postal_code}.")
            
            self._input_text(firstname_label, firstname)
            self._input_text(lastname_label, lastname)
            self._input_text(postal_code_label, postal_code)

            self._wait_random_delay()
            self._click_like_human(continue_button)
            self.log.log_info(f"Форма оформления заказа отправлена")

            error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".error-message-container.error")
            if error_elements:
                error_texts = error_elements[0].text.strip()
                raise ValueError(f"Ошибка заполнения формы: {error_texts}")
            return True
        except ValueError as e:
            self.log.log_error("", e)

            if self.final_screenshot_required:
                self._save_screenshot("order_form_error")
            return False
        except Exception as e:
            self.log.log_error(f"Ошибка при оформлении заказа: ", e)
            return False

    def _complete_checkout_step_two(self):
        """Завершает второй шаг оформления заказа"""
        try:
            summary_container = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "checkout_summary_container")))

            total_items = len(summary_container.find_elements(By.CSS_SELECTOR, ".cart_item"))
            self.log.log_info(f"Количество товаров в корзине: {total_items}")

            self._scroll_page('down')

            self.log.log_info(f"Нажимаем Finish")
            finish_btn = self.driver.find_element(By.ID, "finish")
            self._click_like_human(finish_btn)
            self._wait_random_delay()

            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, "back-to-products")))
            return True
        except TimeoutException:
            self.log.log_error(f"Кнопка Finish не нажимаеться! Timeout.")

            if self.final_screenshot_required:
                self._save_screenshot("step_two_error")
            return False
        except Exception as e:
            self.log.log_error("Ошибка при 2 шаге оформления заказа: ", e)
            return False

    def _complete_checkout_confirmation(self):
        """Подтверждает заказ и возвращается на главную страницу"""
        try:
            back_home_btn = self.driver.find_element(By.ID, "back-to-products")
            if self.final_screenshot_required:
                self._save_screenshot("finish")

            self._scroll_page('down')

            self.log.log_info(f"Возвращаемся к продуктам.")
            self._click_like_human(back_home_btn)
            self._wait_random_delay()

        except Exception as e:
            self.log.log_error("Ошибка при завершении оформления заказа: ", e)

    def _perform_logout(self):
        """Выход из аккаунта через меню"""
        self.log.log_info(f"Выходим из системы.")
        menu_btn = self.driver.find_element(By.ID, "react-burger-menu-btn")
        self._click_like_human(menu_btn)
        self._wait_random_delay()

        logout_btn = WebDriverWait(self.driver, self.timeout/2).until(
            EC.element_to_be_clickable((By.ID, "logout_sidebar_link"))
        )
        self._click_like_human(logout_btn)
        self._wait_random_delay()

if __name__ == '__main__':
    bot = SaucedemoBot()
    bot.run()