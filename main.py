"""READS Home Reading Assistant - offline Kivy app (Android + desktop test mode).

Four tasks:
  Task 1 - 100 sight words
  Task 2 - 100 basic sight word phrases
  Task 3 - 100 basic sight word sentences
  Task 4 - short story + 5 random multiple choice questions (score kept, retake below 80%)
"""
import json
import os
import random
import time

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.utils import platform

import metrics

ON_ANDROID = platform == "android"
HERE = os.path.dirname(os.path.abspath(__file__))
PASS_MARK = 80

KV = """
ScreenManager:
    Screen:
        name: 'home'
        BoxLayout:
            orientation: 'vertical'
            padding: dp(12)
            spacing: dp(8)
            Image:
                source: app.logo_path
                size_hint_y: None
                height: dp(90)
                allow_stretch: True
                keep_ratio: True
            Label:
                text: '[b]Project_READS Home Reading[/b]'
                markup: True
                font_size: '24sp'
                size_hint_y: None
                height: dp(44)
            Label:
                id: home_msg
                text: 'Tap a task to begin.'
                italic: True
                size_hint_y: None
                height: dp(26)
            Label:
                id: home_scores
                markup: True
                text: ''
                font_size: '17sp'
                text_size: self.width, None
                halign: 'left'
                valign: 'top'
                size_hint_y: None
                height: dp(110)
            Button:
                text: 'Task 1: 100 Sight Words'
                size_hint_y: None
                height: dp(56)
                background_color: .2, .6, .9, 1
                on_release: app.open_task(1)
            Button:
                text: 'Task 2: 100 Sight Word Phrases'
                size_hint_y: None
                height: dp(56)
                background_color: .2, .7, .3, 1
                on_release: app.open_task(2)
            Button:
                text: 'Task 3: 100 Sight Word Sentences'
                size_hint_y: None
                height: dp(56)
                background_color: .9, .6, .2, 1
                on_release: app.open_task(3)
            Button:
                text: 'Task 4: Short Story + 5 Questions'
                size_hint_y: None
                height: dp(56)
                background_color: .7, .3, .7, 1
                on_release: app.open_task(4)
            Label:
                id: home_status
                text: ''
                size_hint_y: None
                height: dp(26)
            Label:
                text: 'Developed by Erlhan'
                italic: True
                font_size: '13sp'
                color: .6, .6, .6, 1
                size_hint_y: None
                height: dp(22)

    Screen:
        name: 'items'
        BoxLayout:
            orientation: 'vertical'
            padding: dp(12)
            spacing: dp(8)
            Label:
                id: item_title
                text: ''
                bold: True
                font_size: '19sp'
                size_hint_y: None
                height: dp(30)
            Label:
                id: item_progress
                text: ''
                size_hint_y: None
                height: dp(26)
            Label:
                id: item_instruction
                text: ''
                italic: True
                text_size: self.width, None
                halign: 'left'
                size_hint_y: None
                height: dp(50)
            ScrollView:
                Label:
                    id: item_text
                    text: ''
                    font_size: '36sp'
                    halign: 'center'
                    valign: 'middle'
                    size_hint_y: None
                    height: max(self.texture_size[1] + dp(30), dp(140))
                    text_size: self.width - dp(20), None
            Label:
                id: item_count
                text: ''
                size_hint_y: None
                height: dp(26)
            BoxLayout:
                size_hint_y: None
                height: dp(64)
                spacing: dp(8)
                Button:
                    text: 'X  Not yet'
                    background_color: .85, .2, .2, 1
                    on_release: app.mark_item(False)
                Button:
                    text: 'OK  Read it'
                    background_color: .2, .7, .3, 1
                    on_release: app.mark_item(True)
            Button:
                text: 'Back to Home'
                size_hint_y: None
                height: dp(46)
                on_release: app.go_home()

    Screen:
        name: 'score'
        BoxLayout:
            orientation: 'vertical'
            padding: dp(16)
            spacing: dp(10)
            Label:
                id: score_title
                text: ''
                bold: True
                font_size: '20sp'
                text_size: self.width, None
                halign: 'center'
                size_hint_y: None
                height: dp(56)
            Label:
                id: score_value
                markup: True
                text: ''
                font_size: '52sp'
                size_hint_y: None
                height: dp(80)
            Label:
                id: score_detail
                markup: True
                text: ''
                font_size: '18sp'
                text_size: self.width, None
                halign: 'center'
                valign: 'top'
                size_hint_y: None
                height: dp(150)
            Button:
                id: score_retake
                text: 'Retake (need 80% to pass)'
                size_hint_y: None
                height: dp(56)
                background_color: .9, .5, .2, 1
                on_release: app.retake()
            Button:
                text: 'Back to Home'
                size_hint_y: None
                height: dp(56)
                on_release: app.go_home()

    Screen:
        name: 'story'
        BoxLayout:
            orientation: 'vertical'
            padding: dp(10)
            spacing: dp(6)
            Label:
                id: story_title
                text: ''
                bold: True
                font_size: '20sp'
                size_hint_y: None
                height: dp(30)
            Label:
                id: story_instruction
                text: ''
                italic: True
                text_size: self.width, None
                halign: 'left'
                size_hint_y: None
                height: dp(40)
            ScrollView:
                Label:
                    id: story_text
                    text: ''
                    font_size: '19sp'
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
                height: dp(50)
                spacing: dp(8)
                Button:
                    id: read_start
                    text: 'Read Aloud'
                    background_color: .2, .7, .3, 1
                    on_release: app.start_reading()
                Button:
                    id: read_stop
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
                id: report_scroll
                size_hint_y: None
                height: 0
                Label:
                    id: report
                    markup: True
                    text: ''
                    size_hint_y: None
                    height: self.texture_size[1] + dp(10)
                    text_size: self.width - dp(10), None
                    halign: 'left'
                    valign: 'top'
            BoxLayout:
                size_hint_y: None
                height: dp(56)
                spacing: dp(8)
                Button:
                    text: 'Start Quiz'
                    background_color: .7, .3, .7, 1
                    on_release: app.start_quiz()
                Button:
                    text: 'Home'
                    on_release: app.go_home()

    Screen:
        name: 'quiz'
        BoxLayout:
            orientation: 'vertical'
            padding: dp(12)
            spacing: dp(8)
            Label:
                id: q_progress
                text: ''
                size_hint_y: None
                height: dp(26)
            Label:
                id: q_text
                text: ''
                font_size: '22sp'
                text_size: self.width, None
                halign: 'left'
                valign: 'top'
                size_hint_y: None
                height: max(dp(90), self.texture_size[1] + dp(10))
            Button:
                id: opt0
                text: ''
                size_hint_y: None
                height: dp(64)
                text_size: self.width - dp(20), None
                halign: 'left'
                on_release: app.answer(0)
            Button:
                id: opt1
                text: ''
                size_hint_y: None
                height: dp(64)
                text_size: self.width - dp(20), None
                halign: 'left'
                on_release: app.answer(1)
            Button:
                id: opt2
                text: ''
                size_hint_y: None
                height: dp(64)
                text_size: self.width - dp(20), None
                halign: 'left'
                on_release: app.answer(2)
            Button:
                id: opt3
                text: ''
                size_hint_y: None
                height: dp(64)
                text_size: self.width - dp(20), None
                halign: 'left'
                on_release: app.answer(3)
            Label:
                id: q_feedback
                text: ''
                bold: True
                size_hint_y: None
                height: dp(30)
            Button:
                text: 'Back to Home'
                size_hint_y: None
                height: dp(46)
                on_release: app.go_home()

    Screen:
        name: 'result'
        BoxLayout:
            orientation: 'vertical'
            padding: dp(16)
            spacing: dp(10)
            Label:
                id: result_title
                text: ''
                bold: True
                font_size: '20sp'
                text_size: self.width, None
                halign: 'center'
                size_hint_y: None
                height: dp(56)
            Label:
                id: result_score
                markup: True
                text: ''
                font_size: '52sp'
                size_hint_y: None
                height: dp(80)
            Label:
                id: result_detail
                markup: True
                text: ''
                font_size: '18sp'
                text_size: self.width, None
                halign: 'center'
                valign: 'top'
                size_hint_y: None
                height: dp(150)
            Button:
                id: result_retake
                text: 'Retake Quiz (need 80% to pass)'
                size_hint_y: None
                height: dp(56)
                background_color: .9, .5, .2, 1
                on_release: app.retake()
            Button:
                text: 'Try Another Story'
                size_hint_y: None
                height: dp(56)
                background_color: .7, .3, .7, 1
                on_release: app.open_task(4)
            Button:
                text: 'Back to Home'
                size_hint_y: None
                height: dp(56)
                on_release: app.go_home()
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


def set_visible(btn, show):
    """Show/hide a button that has size_hint_y: None."""
    btn.opacity = 1 if show else 0
    btn.disabled = not show
    btn.height = dp(56) if show else 0


class ReadsApp(App):
    title = "Project_READS Home Reading"
    icon = os.path.join(HERE, "erlhan.png")   # window icon on desktop

    def build(self):
        self.logo_path = os.path.join(HERE, "erlhan.png")
        with open(os.path.join(HERE, "tasks.json"), encoding="utf-8") as f:
            self.data = json.load(f)
        self.pass_mark = self.data.get("pass_mark", PASS_MARK)
        self.root_w = Builder.load_string(KV)
        self.scores = self.load_scores()
        self.recognizer = None
        self.started = 0.0
        self.task = 0
        self.items, self.pos, self.correct = [], 0, 0
        self.story = None
        self.quiz, self.qpos, self.qcorrect, self.answered = [], 0, 0, False
        if not ON_ANDROID:  # desktop testing helper
            ti = self.root_w.ids.typed
            ti.height, ti.opacity = 40, 1
        self.refresh_home()
        return self.root_w

    # ---------------------------------------------------------------- home
    def refresh_home(self):
        lines = []
        for n, key in enumerate(("task1", "task2", "task3", "task4"), start=1):
            rec = self.scores.get(key)
            if rec:
                state = ("[color=22aa22]PASS[/color]" if rec.get("passed")
                         else "[color=dd2222]NOT YET[/color]")
                lines.append(f"[b]Task {n}:[/b] best {rec.get('best', 0)}% - {state}")
            else:
                lines.append(f"[b]Task {n}:[/b] not taken yet")
        self.root_w.ids.home_scores.text = "\n".join(lines)

    def go_home(self):
        self.refresh_home()
        self.root_w.current = "home"

    # ------------------------------------------------------------ tasks 1-3
    def open_task(self, n):
        self.task = n
        if n in (1, 2, 3):
            self.items = list(self.data[f"task{n}"]["items"])
            self.pos, self.correct = 0, 0
            self.show_item()
            self.root_w.current = "items"
        else:
            self.new_story()

    def show_item(self):
        ids = self.root_w.ids
        d = self.data[f"task{self.task}"]
        ids.item_title.text = d["title"]
        ids.item_instruction.text = d["instruction"]
        ids.item_progress.text = f"Item {self.pos + 1} of {len(self.items)}"
        ids.item_text.text = str(self.items[self.pos])
        ids.item_count.text = f"Read correctly: {self.correct}"

    def mark_item(self, ok):
        if ok:
            self.correct += 1
        self.pos += 1
        if self.pos >= len(self.items):
            self.finish_items()
        else:
            self.show_item()

    def finish_items(self):
        total = len(self.items)
        score = round(100.0 * self.correct / total)
        key = f"task{self.task}"
        self.save_score(key, score)
        passed = score >= self.pass_mark
        ids = self.root_w.ids
        color = "22aa22" if passed else "dd2222"
        ids.score_title.text = self.data[key]["title"]
        ids.score_value.text = f"[color={color}]{score}%[/color]"
        if passed:
            detail = (f"Read correctly: {self.correct} of {total}\n\n"
                      "[color=22aa22][b]PASSED[/b][/color] - great job!")
        else:
            detail = (f"Read correctly: {self.correct} of {total}\n\n"
                      f"[color=dd2222][b]NEED {self.pass_mark}% TO PASS[/b][/color]\n"
                      "Tap retake to try again.")
        ids.score_detail.text = detail
        set_visible(ids.score_retake, not passed)
        self.root_w.current = "score"

    # -------------------------------------------------------------- task 4
    def new_story(self):
        self.story = random.choice(self.data["task4"]["stories"])
        ids = self.root_w.ids
        ids.story_title.text = self.story["title"]
        ids.story_instruction.text = (
            "Read the story aloud (Read Aloud), then tap Start Quiz. "
            "You need 80% to pass.")
        ids.story_text.text = self.story["content"]
        ids.report.text = ""
        ids.report_scroll.height = 0
        ids.status.text = ""
        ids.read_start.disabled = False
        ids.read_stop.disabled = True
        self.root_w.current = "story"

    def start_quiz(self):
        bank = self.story["questions"]
        self.quiz = random.sample(bank, min(5, len(bank)))
        self.qpos, self.qcorrect, self.answered = 0, 0, False
        self.show_question()
        self.root_w.current = "quiz"

    def show_question(self):
        ids = self.root_w.ids
        q = self.quiz[self.qpos]
        self.answered = False
        ids.q_progress.text = f"Question {self.qpos + 1} of {len(self.quiz)}"
        ids.q_text.text = q["q"]
        ids.q_feedback.text = ""
        for i in range(4):
            b = ids[f"opt{i}"]
            b.text = f"{chr(65 + i)}. {q['options'][i]}"
            b.disabled = False
            b.background_color = .93, .93, .93, 1

    def answer(self, i):
        if self.answered:
            return
        self.answered = True
        q = self.quiz[self.qpos]
        good = i == q["answer"]
        if good:
            self.qcorrect += 1
        ids = self.root_w.ids
        for j in range(4):
            b = ids[f"opt{j}"]
            b.disabled = True
            if j == q["answer"]:
                b.background_color = .2, .7, .3, 1
            elif j == i:
                b.background_color = .85, .2, .2, 1
        ids.q_feedback.text = ("[color=22aa22]Correct![/color]" if good
                               else "[color=dd2222]Not correct.[/color]")
        Clock.schedule_once(lambda dt: self.next_question(), 1.0)

    def next_question(self):
        self.qpos += 1
        if self.qpos >= len(self.quiz):
            self.finish_quiz()
        else:
            self.show_question()

    def finish_quiz(self):
        total = len(self.quiz)
        score = round(100.0 * self.qcorrect / total)
        self.save_score("task4", score,
                        extra={"story": self.story["id"], "last_correct": self.qcorrect})
        passed = score >= self.pass_mark
        ids = self.root_w.ids
        color = "22aa22" if passed else "dd2222"
        ids.result_title.text = self.story["title"]
        ids.result_score.text = f"[color={color}]{score}%[/color]"
        if passed:
            detail = (f"Correct answers: {self.qcorrect} of {total}\n\n"
                      "[color=22aa22][b]PASSED[/b][/color] - great job!")
        else:
            detail = (f"Correct answers: {self.qcorrect} of {total}\n\n"
                      f"[color=dd2222][b]NEED {self.pass_mark}% TO PASS[/b][/color]\n"
                      "Tap retake to try 5 new questions.")
        ids.result_detail.text = detail
        set_visible(ids.result_retake, not passed)
        self.root_w.current = "result"

    # ------------------------------------------------------------- retake
    def retake(self):
        if self.task == 4:
            self.start_quiz()          # 5 new random questions, same story
        else:
            self.open_task(self.task)  # start the list again from item 1

    # ------------------------------------------------- speech read-aloud
    def start_reading(self):
        ids = self.root_w.ids
        ids.read_start.disabled = True
        ids.read_stop.disabled = False
        ids.status.text = "Recording... read the story aloud"
        ids.report.text = ""
        ids.report_scroll.height = 0
        self.started = time.time()
        if ON_ANDROID:
            self.recognizer = Recognizer("en-US")
            self.recognizer.start()

    def stop_reading(self):
        ids = self.root_w.ids
        seconds = time.time() - self.started
        spoken = self.recognizer.stop() if (ON_ANDROID and self.recognizer) else ids.typed.text
        ids.read_start.disabled = False
        ids.read_stop.disabled = True
        ids.status.text = ""
        if not spoken.strip():
            ids.status.text = "No speech detected. Please try again."
            return
        m = metrics.calculate(self.story["content"], spoken, seconds)
        mark = lambda items: " ".join(
            f"[color={COLORS[t]}]{w}[/color]" for t, w in items)
        ids.report.text = (
            f"[b]WPM:[/b] {m['wpm']}   [b]Accuracy:[/b] {m['accuracy']}%\n"
            f"[b]Omissions:[/b] {m['omissions']}   [b]Insertions:[/b] {m['insertions']}   "
            f"[b]Repetitions:[/b] {m['repetitions']}   [b]Mispronounced:[/b] {m['mispronounced']}\n\n"
            f"[b]Story:[/b]\n{mark(m['original'])}\n\n[b]Your reading:[/b]\n{mark(m['spoken'])}\n\n"
            "[color=22aa22]green[/color]=correct  [color=e0a000]orange[/color]=mispronounced  "
            "[color=dd2222]red[/color]=omitted  [color=777777]gray[/color]=inserted")
        ids.report_scroll.height = dp(180)
        self.save_log(m)

    # ------------------------------------------------------------ storage
    def load_scores(self):
        path = os.path.join(self.user_data_dir, "scores.json")
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    return json.load(f)
            except (ValueError, OSError):
                pass
        return {}

    def save_score(self, key, score, extra=None):
        passed = score >= self.pass_mark
        rec = self.scores.get(key, {"attempts": 0, "best": 0, "passed": False})
        rec["attempts"] = rec.get("attempts", 0) + 1
        rec["best"] = max(rec.get("best", 0), score)
        rec["passed"] = bool(rec.get("passed")) or passed
        rec["last"] = score
        rec["at"] = time.strftime("%Y-%m-%d %H:%M")
        if extra:
            rec.update(extra)
        self.scores[key] = rec
        path = os.path.join(self.user_data_dir, "scores.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.scores, f, indent=2)
        self.log_record({"kind": "task_score", "task": key, "score": score,
                         "passed": passed, "attempts": rec["attempts"],
                         "ts": time.strftime("%Y-%m-%d %H:%M")})
        self.refresh_home()

    def log_record(self, rec):
        """Local progress log the teacher can collect later (no network)."""
        path = os.path.join(self.user_data_dir, "progress.jsonl")
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")

    def save_log(self, m):
        rec = {k: m[k] for k in ("wpm", "accuracy", "omissions", "insertions", "repetitions")}
        rec.update(kind="reading", story=self.story["id"],
                   ts=time.strftime("%Y-%m-%d %H:%M"))
        self.log_record(rec)


if __name__ == "__main__":
    ReadsApp().run()
