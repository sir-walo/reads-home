"""READS Home Reading Assistant - offline Kivy app (Android + desktop test mode)."""
import json
import os
import random
import time

from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import platform

import metrics

ON_ANDROID = platform == "android"
HERE = os.path.dirname(os.path.abspath(__file__))

KV = """
BoxLayout:
    orientation: 'vertical'
    padding: dp(10)
    spacing: dp(8)
    Label:
        text: '[b]READS Home Reading[/b]'
        markup: True
        font_size: '22sp'
        size_hint_y: None
        height: dp(40)
    BoxLayout:
        size_hint_y: None
        height: dp(44)
        spacing: dp(8)
        Spinner:
            id: grade
            text: '4'
            values: [str(g) for g in range(1, 13)]
            on_text: app.new_story()
        Spinner:
            id: cat
            text: 'English'
            values: ['English', 'Filipino']
            on_text: app.new_story()
    Label:
        id: title
        text: ''
        size_hint_y: None
        height: dp(28)
        italic: True
    ScrollView:
        Label:
            id: story
            text: ''
            font_size: '20sp'
            size_hint_y: None
            height: self.texture_size[1] + dp(20)
            text_size: self.width - dp(10), None
            halign: 'left'
            valign: 'top'
    TextInput:
        id: typed
        hint_text: 'DESKTOP TEST ONLY: type what you "read"'
        size_hint_y: None
        height: 0
        opacity: 0
        multiline: False
    BoxLayout:
        size_hint_y: None
        height: dp(52)
        spacing: dp(8)
        Button:
            id: start
            text: 'Start Reading'
            background_color: .2, .7, .3, 1
            on_release: app.start_reading()
        Button:
            id: stop
            text: 'Finish Reading'
            disabled: True
            background_color: .2, .4, .9, 1
            on_release: app.stop_reading()
    Label:
        id: status
        text: ''
        size_hint_y: None
        height: dp(26)
    ScrollView:
        Label:
            id: report
            markup: True
            text: ''
            size_hint_y: None
            height: self.texture_size[1] + dp(10)
            text_size: self.width - dp(10), None
            halign: 'left'
            valign: 'top'
"""

COLORS = {"correct": "22aa22", "mispronounced": "e0a000", "omitted": "dd2222",
          "inserted": "777777"}


class Recognizer:
    """Wraps Android's built-in SpeechRecognizer (offline if language pack installed)."""

    def __init__(self, language):
        self.language = language
        self.segments = []
        self.active = False
        self.rec = None
        self.listener = None

    def start(self):
        from android.permissions import Permission, request_permissions
        request_permissions([Permission.RECORD_AUDIO], lambda p, g: self._begin())

    def _begin(self):
        from android.runnable import run_on_ui_thread

        @run_on_ui_thread
        def go():
            from jnius import PythonJavaClass, autoclass, java_method
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            SR = autoclass("android.speech.SpeechRecognizer")
            Intent = autoclass("android.content.Intent")
            RS = autoclass("android.speech.RecognizerIntent")
            outer = self

            class L(PythonJavaClass):
                __javainterfaces__ = ["android/speech/RecognitionListener"]
                __javacontext__ = "app"

                @java_method("(Landroid/os/Bundle;)V")
                def onReadyForSpeech(self, b): pass
                @java_method("()V")
                def onBeginningOfSpeech(self): pass
                @java_method("(F)V")
                def onRmsChanged(self, f): pass
                @java_method("([B)V")
                def onBufferReceived(self, b): pass
                @java_method("()V")
                def onEndOfSpeech(self): pass
                @java_method("(ILandroid/os/Bundle;)V")
                def onEvent(self, i, b): pass
                @java_method("(Landroid/os/Bundle;)V")
                def onPartialResults(self, b): pass

                @java_method("(I)V")
                def onError(self, code):
                    # 6 = speech timeout, 7 = no match -> just keep listening
                    outer._restart()

                @java_method("(Landroid/os/Bundle;)V")
                def onResults(self, b):
                    arr = b.getStringArrayList(SR.RESULTS_RECOGNITION)
                    if arr is not None and arr.size() > 0:
                        outer.segments.append(str(arr.get(0)))
                    outer._restart()

            self.listener = L()
            self.intent = Intent(RS.ACTION_RECOGNIZE_SPEECH)
            self.intent.putExtra(RS.EXTRA_LANGUAGE_MODEL, RS.LANGUAGE_MODEL_FREE_FORM)
            self.intent.putExtra(RS.EXTRA_LANGUAGE, self.language)
            self.intent.putExtra(RS.EXTRA_PREFER_OFFLINE, True)
            self.intent.putExtra(RS.EXTRA_PARTIAL_RESULTS, True)
            self.rec = SR.createSpeechRecognizer(PythonActivity.mActivity)
            self.rec.setRecognitionListener(self.listener)
            self.active = True
            self.rec.startListening(self.intent)

        go()

    def _restart(self):
        if not self.active:
            return
        from android.runnable import run_on_ui_thread

        @run_on_ui_thread
        def again():
            if self.active and self.rec:
                self.rec.startListening(self.intent)

        Clock.schedule_once(lambda dt: again(), 0.15)

    def stop(self):
        from android.runnable import run_on_ui_thread
        self.active = False

        @run_on_ui_thread
        def halt():
            if self.rec:
                self.rec.stopListening()
                self.rec.destroy()
                self.rec = None

        halt()
        return " ".join(self.segments)


class ReadsApp(App):
    title = "READS Home Reading"

    def build(self):
        with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as f:
            self.stories = json.load(f)
        self.root_w = Builder.load_string(KV)
        self.recognizer = None
        self.started = 0
        Clock.schedule_once(lambda dt: self.new_story(), 0)
        if not ON_ANDROID:  # desktop testing helper
            ti = self.root_w.ids.typed
            ti.height, ti.opacity = 40, 1
        return self.root_w

    def new_story(self):
        ids = self.root_w.ids
        pool = [s for s in self.stories
                if str(s["grade"]) == ids.grade.text and s["category"] == ids.cat.text]
        self.current = random.choice(pool) if pool else None
        ids.story.text = self.current["content"] if self.current else \
            "No story for this grade/category. Add one to stories.json."
        ids.title.text = self.current["title"] if self.current else ""
        ids.report.text = ""
        ids.start.disabled = self.current is None

    def start_reading(self):
        ids = self.root_w.ids
        ids.start.disabled, ids.stop.disabled = True, False
        ids.status.text = "Recording... read the story aloud"
        ids.report.text = ""
        self.started = time.time()
        if ON_ANDROID:
            lang = "fil-PH" if ids.cat.text == "Filipino" else "en-US"
            self.recognizer = Recognizer(lang)
            self.recognizer.start()

    def stop_reading(self):
        ids = self.root_w.ids
        seconds = time.time() - self.started
        spoken = self.recognizer.stop() if (ON_ANDROID and self.recognizer) else ids.typed.text
        ids.start.disabled, ids.stop.disabled = False, True
        ids.status.text = ""
        if not spoken.strip():
            ids.report.text = "No speech detected. Please try again."
            return
        m = metrics.calculate(self.current["content"], spoken, seconds)
        mark = lambda items: " ".join(
            f"[color={COLORS[t]}]{w}[/color]" for t, w in items)
        ids.report.text = (
            f"[b]WPM:[/b] {m['wpm']}   [b]Accuracy:[/b] {m['accuracy']}%\n"
            f"[b]Omissions:[/b] {m['omissions']}   [b]Insertions:[/b] {m['insertions']}   "
            f"[b]Repetitions:[/b] {m['repetitions']}   [b]Mispronounced:[/b] {m['mispronounced']}\n\n"
            f"[b]Story:[/b]\n{mark(m['original'])}\n\n[b]Your reading:[/b]\n{mark(m['spoken'])}\n\n"
            "[color=22aa22]green[/color]=correct  [color=e0a000]orange[/color]=mispronounced  "
            "[color=dd2222]red[/color]=omitted  [color=777777]gray[/color]=inserted")
        self.save_log(m)

    def save_log(self, m):
        """Local progress log the teacher can collect later (no network)."""
        path = os.path.join(self.user_data_dir, "progress.jsonl")
        rec = {k: m[k] for k in ("wpm", "accuracy", "omissions", "insertions", "repetitions")}
        rec.update(story=self.current["id"], ts=time.strftime("%Y-%m-%d %H:%M"))
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")


if __name__ == "__main__":
    ReadsApp().run()
