# coding=utf-8
from pathlib import Path
import re
import threading
import time

import pyperclip

# 最新のChrome環境に合わせたドライバが必要(実行する環境のChromeに依存するので注意)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def esc_paper(text):
    text = re.sub(r"^ +", "", text)
    # http fileパス network pathでの発動を禁止
    m = re.search(r"^(http|[a-zA-Z]:[/\\]|\\\\)", text)
    if m:
        return False

    text = re.sub(r"[-  0-9、。・]", "", text)
    if len(text) < 2:
        return False

    return True


def normalize_paper(text):
    new = re.sub(r"[\r\n]+", "", text)
    new = re.sub(r"[ 　]+", " ", new)
    new = re.sub("\. ", ".\n", new)
    return new


class TranslateCopy(threading.Thread):
    def __init__(self):
        super().__init__()
        self.pre_clipboard_data = ""
        self.clipboard_check_time = 5
        self.selenium_checkpath_retrycnt = 10

        # DeepL
        self.translate_url = "https://www.deepl.com/translator"
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        self.desired_caps = options.to_capabilities()

        # ChromePATH
        chrome_driver_path = Path().absolute()
        self.chrome_driver_path = chrome_driver_path / Path("chrome_driver/chromedriver.exe")
        self.driver = webdriver.Chrome(executable_path=str(self.chrome_driver_path), desired_capabilities=self.desired_caps)
        # 翻訳サイトをヘッドレスブラウザに流す
        self.driver.get(self.translate_url)

    def __del__(self):
        print("finish TranslateCopy")
        self.driver.quit()

    def __exit__(self):
        print("exit TranslateCopy")
        self.driver.quit()

    def run(self):
        while True:
            try:
                self.translate_main()
            except:
                self.driver.quit()
                break
            time.sleep(self.clipboard_check_time)

    def call_chromedriver(self):
        # chrome driverのXボタン検知用
        try:
            _ = self.driver.window_handles
        except:
            # 再度実行させる
            self.driver = webdriver.Chrome(executable_path=str(self.chrome_driver_path), desired_capabilities=self.desired_caps)
            # 翻訳サイトをヘッドレスブラウザに流す
            self.driver.get(self.translate_url)

    def check_view_xpath(self, path):
        def wait_check_view_xpath(driver, p):
            try:
                # TimeoutException前に最大10秒間待機する
                # WebDriverWait:正常に返されるまで500ミリ秒ごとにExpectedConditionを呼び出す(default)
                element_check = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, p)))
                return element_check
            except Exception as ex:
                print("not fount id: ", p, ex)
                return None

        flg_wait = True
        cnt = 0
        while flg_wait:
            # WEB画面をロードするタイミングでWAITが足りない場合があるので指定回数リトライする
            if cnt >= self.selenium_checkpath_retrycnt:
                break

            result = wait_check_view_xpath(self.driver, path)
            if result:
                try:
                    return self.driver.find_element_by_xpath(path)
                except Exception as ex:
                    print("click method error id :", path, ex)
            cnt += 1
        raise Exception("cnt_over")

    def translate_main(self):
        # クリップボード取得
        copy_text = str(pyperclip.paste())
        if len(copy_text) == 0:
            return

        # 前回コピーとの差分チェック
        if self.pre_clipboard_data == copy_text[:10]:
            return

        # http:などで動かしたくない
        if not esc_paper(copy_text):
            return

        # 前処理
        new_text_lines = normalize_paper(copy_text)
        if len(new_text_lines) == 0:
            return

        # normalize結果でも前回コピー品と比較しておく
        if self.pre_clipboard_data == new_text_lines[:10]:
            return

        # 次回発動しないようにコピー情報を記録
        self.pre_clipboard_data = new_text_lines[:10]

        # ChromeDriverが存在するか？
        self.call_chromedriver()

        # text input
        try:
            # DeepLの翻訳は自動認識まかせ
            elm = self.check_view_xpath('//*[@id="dl_translator"]/div[1]/div[3]/div[2]/div/textarea')
            elm.clear()
            elm.send_keys(new_text_lines)
        except Exception as ex:
            if ex.args[0] == "cnt_over":
                raise ex
            print("get xpath exception:", ex)
            self.pre_clipboard_data = ""


def main():
    th = TranslateCopy()
    th.start()


if __name__ == "__main__":
    main()
