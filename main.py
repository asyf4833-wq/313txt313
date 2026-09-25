import re
import hashlib
import base64
import json
import secrets
import string
import urllib.request

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    def ar(t):
        return get_display(arabic_reshaper.reshape(str(t)))
except:
    def ar(t):
        return str(t)

Window.clearcolor = get_color_from_hex('#0a1929')

GREEN = get_color_from_hex('#00e676')
BLUE = get_color_from_hex('#1976d2')
RED = get_color_from_hex('#d32f2f')
WHITE = (1, 1, 1, 1)
DARK = get_color_from_hex('#1e3a5f')


def check_password_strength(pw):
    score = 0
    notes = []
    if len(pw) >= 12: score += 2
    elif len(pw) >= 8: score += 1
    else: notes.append("- قصيرة جداً")
    if re.search(r"[A-Z]", pw): score += 1
    else: notes.append("- بدون حرف كبير")
    if re.search(r"[a-z]", pw): score += 1
    else: notes.append("- بدون حرف صغير")
    if re.search(r"\d", pw): score += 1
    else: notes.append("- بدون رقم")
    if re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=]", pw): score += 2
    else: notes.append("- بدون رمز خاص")
    common = ["123456", "password", "qwerty", "111111", "abc123"]
    if pw.lower() in common:
        score = 0
        notes.append("! كلمة مرور شائعة")
    return score, notes


def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))


def check_url(url):
    suspicious = ["bit.ly", "tinyurl", "free-", "-login", "-verify", "-secure"]
    score = 0
    reasons = []
    for s in suspicious:
        if s in url.lower():
            score += 1
            reasons.append(s)
    if url.count("-") > 3:
        score += 1
        reasons.append("شرطات كثيرة")
    if len(url) > 75:
        score += 1
        reasons.append("طويل جداً")
    if not url.startswith("https://"):
        score += 1
        reasons.append("بدون HTTPS")
    if score >= 3:
        return "خطر مرتفع", reasons
    elif score >= 1:
        return "مشبوه", reasons
    return "آمن", []


def get_ip_info():
    try:
        url = "http://ip-api.com/json/?fields=status,country,city,isp,query,proxy"
        req = urllib.request.Request(url, headers={"User-Agent": "CyberApp"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except:
        return None


def hash_all(text):
    return {
        "MD5": hashlib.md5(text.encode()).hexdigest(),
        "SHA1": hashlib.sha1(text.encode()).hexdigest(),
        "SHA256": hashlib.sha256(text.encode()).hexdigest(),
    }


def b64_encode(text):
    return base64.b64encode(text.encode()).decode()


def b64_decode(text):
    try:
        return base64.b64decode(text.encode()).decode()
    except:
        return None


def make_btn(text, cb, color=None):
    btn = Button(
        text=ar(text),
        size_hint_y=None,
        height=55,
        background_color=color or BLUE,
        background_normal='',
        font_size='16sp',
        color=WHITE
    )
    btn.bind(on_press=cb)
    return btn


class ResultPopup(Popup):
    def __init__(self, title, message, **kw):
        super().__init__(**kw)
        self.title = ar(title)
        self.size_hint = (0.92, 0.75)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        scroll = ScrollView()
        label = Label(
            text=ar(message),
            size_hint_y=None,
            halign='right',
            valign='top',
            color=WHITE,
            font_size='14sp'
        )
        label.bind(
            width=lambda *x: setattr(label, 'text_size', (label.width, None)),
            texture_size=lambda *x: setattr(label, 'height', label.texture_size[1])
        )
        scroll.add_widget(label)
        layout.add_widget(scroll)

        close_btn = Button(text=ar('إغلاق'), size_hint_y=None, height=50,
                          background_color=RED, background_normal='')
        close_btn.bind(on_press=self.dismiss)
        layout.add_widget(close_btn)

        self.content = layout


class InputPopup(Popup):
    def __init__(self, title, hint, callback, **kw):
        super().__init__(**kw)
        self.title = ar(title)
        self.callback = callback
        self.size_hint = (0.92, 0.5)

        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        self.input = TextInput(
            hint_text=ar(hint),
            multiline=False,
            size_hint_y=None,
            height=55,
            background_color=DARK,
            foreground_color=WHITE
        )
        layout.add_widget(self.input)

        btn = Button(text=ar('تأكيد'), size_hint_y=None, height=50,
                    background_color=BLUE, background_normal='')
        btn.bind(on_press=self.submit)
        layout.add_widget(btn)

        cancel = Button(text=ar('إلغاء'), size_hint_y=None, height=50,
                       background_color=RED, background_normal='')
        cancel.bind(on_press=self.dismiss)
        layout.add_widget(cancel)

        self.content = layout

    def submit(self, instance):
        text = self.input.text
        self.dismiss()
        if text:
            self.callback(text)


class MainScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical', padding=15, spacing=8)

        root.add_widget(Label(
            text=ar('تطبيق الأمن السيبراني'),
            font_size='26sp',
            size_hint_y=None,
            height=70,
            color=GREEN,
            bold=True
        ))

        scroll = ScrollView()
        inner = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8)
        inner.bind(minimum_height=inner.setter('height'))

        inner.add_widget(make_btn('فحص قوة كلمة المرور', self.op_password))
        inner.add_widget(make_btn('توليد كلمة مرور قوية', self.op_generate))
        inner.add_widget(make_btn('فحص رابط مشبوه', self.op_url))
        inner.add_widget(make_btn('معلومات IP والموقع', self.op_ip))
        inner.add_widget(make_btn('توليد Hash', self.op_hash))
        inner.add_widget(make_btn('Base64 تشفير', self.op_b64e))
        inner.add_widget(make_btn('Base64 فك التشفير', self.op_b64d))

        scroll.add_widget(inner)
        root.add_widget(scroll)
        self.add_widget(root)

    def op_password(self, x):
        InputPopup('فحص كلمة المرور', 'اكتب كلمة المرور', self.do_password).open()

    def do_password(self, pw):
        score, notes = check_password_strength(pw)
        if score >= 6:
            status = 'قوية'
        elif score >= 4:
            status = 'متوسطة'
        else:
            status = 'ضعيفة'
        msg = f'النتيجة: {score}/7\nالحالة: {status}\n\n'
        msg += '\n'.join(notes) if notes else 'ممتاز!'
        ResultPopup('النتيجة', msg).open()

    def op_generate(self, x):
        pw = generate_password(16)
        ResultPopup('كلمة مرور مولدة', pw).open()

    def op_url(self, x):
        InputPopup('فحص رابط', 'الصق الرابط', self.do_url).open()

    def do_url(self, url):
        result, reasons = check_url(url)
        msg = f'النتيجة: {result}\n'
        if reasons:
            msg += '\nالأسباب:\n- ' + '\n- '.join(reasons)
        ResultPopup('نتيجة الفحص', msg).open()

    def op_ip(self, x):
        info = get_ip_info()
        if info and info.get('status') == 'success':
            msg = f"IP: {info.get('query')}\n"
            msg += f"الدولة: {info.get('country')}\n"
            msg += f"المدينة: {info.get('city')}\n"
            msg += f"المزود: {info.get('isp')}\n"
            msg += f"VPN: {'نعم' if info.get('proxy') else 'لا'}"
            ResultPopup('معلومات الاتصال', msg).open()
        else:
            ResultPopup('خطأ', 'فشل الاتصال بالإنترنت').open()

    def op_hash(self, x):
        InputPopup('توليد Hash', 'اكتب النص', self.do_hash).open()

    def do_hash(self, text):
        h = hash_all(text)
        msg = '\n'.join([f"{k}: {v}" for k, v in h.items()])
        ResultPopup('Hashes', msg).open()

    def op_b64e(self, x):
        InputPopup('تشفير Base64', 'اكتب النص', self.do_b64e).open()

    def do_b64e(self, text):
        ResultPopup('الناتج', b64_encode(text)).open()

    def op_b64d(self, x):
        InputPopup('فك Base64', 'الصق النص المشفر', self.do_b64d).open()

    def do_b64d(self, text):
        res = b64_decode(text)
        ResultPopup('الناتج', res if res else 'نص غير صحيح').open()


class CyberApp(App):
    def build(self):
        self.title = 'Cyber Security App'
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        return sm


if __name__ == '__main__':
    CyberApp().run()
