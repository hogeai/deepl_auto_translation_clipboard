# deepl_auto_translation_clipboard

Clipboardを監視し英語テキストの場合DeepLの翻訳へ自動的にテキストを流し込みます。
Clipboard監視による翻訳処理は、前回発火と差分がある場合のみ発動します。

## need module
### ChromeDriver
- [Downloads - ChromeDriver - WebDriver for Chrome](http://chromedriver.chromium.org/downloads)
    - ChromeVersionを確認し、一致するChromeDriverをインストールして下さい

### pip install
- 以下を利用しています
```
pip install selenium
pip install pyperclip
```

## Other
- [hogeai/deepl_auto_translation_shortcutkey](https://github.com/hogeai/deepl_auto_translation_shortcutkey)
    - C-c,C-bで発動します
- [hogeai/deepl_auto_translation_clipboard](https://github.com/hogeai/deepl_auto_translation_clipboard)
    - C-cを監視し英語の場合、発動します。(ThisProject)

