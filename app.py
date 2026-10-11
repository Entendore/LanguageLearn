import sys
import re
import json
import html
import random
from pathlib import Path
from datetime import date, timedelta

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QLineEdit, QScrollArea, QStackedWidget,
    QFrame, QGridLayout, QTextBrowser, QTableWidget, QTableWidgetItem,
    QHeaderView, QListWidget, QMessageBox, QFileDialog, QPlainTextEdit,
    QDialog, QProgressBar, QCompleter, QMenu, QRadioButton, QButtonGroup,
    QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QAction

try:
    from PyQt6.QtTextToSpeech import QTextToSpeech
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# ============================== Data ==============================
PATTERN = re.compile(r"\{(\w+)\}")
POINTS = {"good": 10, "warn": 2, None: 6, "auto": 0}

ACHIEVEMENTS = {
    "first_story": ("✍️", "First Creation", "Complete your very first Mad Lib."),
    "streak_3":   ("🔥", "On Fire", "Reach a 3-day learning streak."),
    "stories_10": ("📚", "Bookworm", "Create 10 Mad Libs."),
    "perfect":    ("💯", "Grammar Pro", "Get a perfect score on a story (no warnings)."),
    "creator":    ("🛠️", "Architect", "Write your own custom story template."),
    "quiz_master":("🧠", "Scholar", "Answer 10 quiz questions correctly.")
}

WORD_TYPES = {
    "noun":        ("Noun", "A person, place, or thing", "dog, teacher, park"),
    "plural_noun": ("Plural Noun", "More than one thing", "dogs, parks, books"),
    "verb":        ("Verb", "An action word (base form)", "run, eat, dance"),
    "verb_past":   ("Verb (past)", "An action that already happened", "ran, ate, danced"),
    "verb_ing":    ("Verb (-ing)", "An ongoing action", "running, eating"),
    "adjective":   ("Adjective", "Describes a noun", "big, happy, green"),
    "adverb":      ("Adverb", "Describes a verb, often ends in -ly", "quickly, softly"),
    "name":        ("Name", "A person's name", "Maria, Tom, Grandma"),
    "place":       ("Place", "A location", "library, beach, kitchen"),
    "animal":      ("Animal", "Any animal", "elephant, cat, parrot"),
    "food":        ("Food", "Something to eat or drink", "pizza, soup, banana"),
    "exclamation": ("Exclamation", "An excited word or phrase", "Wow! Oh no!"),
    "number":      ("Number", "Any number", "7, twenty, 100"),
    "color":       ("Color", "A color", "blue, purple, golden"),
    "occupation":  ("Occupation", "A job", "doctor, pilot, chef"),
    "emotion":     ("Emotion", "A feeling", "excited, nervous"),
    "object":      ("Object", "An everyday thing", "umbrella, phone, spoon"),
}

# Common misspellings dictionary for smart spell check
COMMON_MISSPELLINGS = {
    "teh": "the", "recieve": "receive", "definately": "definitely", "seperate": "separate",
    "occured": "occurred", "untill": "until", "wich": "which", "becuase": "because",
    "alot": "a lot", "thier": "their", "freind": "friend", "wierd": "weird",
    "belive": "believe", "neccessary": "necessary", "tommorow": "tomorrow",
    "tounge": "tongue", "familair": "familiar", "embarass": "embarrass",
    "arguement": "argument", "enviroment": "environment", "goverment": "government",
    "independant": "independent", "maintainance": "maintenance", "priviledge": "privilege",
    "rythm": "rhythm", "succesful": "successful", "truely": "truly"
}

WORD_OF_THE_DAY = [
    ("Ephemeral", "Lasting for a very short time."),
    ("Serendipity", "The occurrence of events by chance in a happy or beneficial way."),
    ("Eloquent", "Fluent or persuasive in speaking or writing."),
    ("Resilient", "Able to withstand or recover quickly from difficult conditions."),
    ("Curious", "Eager to know or learn something."),
    ("Meticulous", "Showing great attention to detail; very careful and precise."),
    ("Vibrant", "Full of energy and life."),
    ("Cozy", "Giving a feeling of comfort, warmth, and relaxation.")
]

# Quiz Question Bank
QUIZ_BANK = [
    {"q": "Choose the correct spelling:", "options": ["definately", "definitely", "definatly"], "ans": "definitely", "exp": "Think of 'finite' inside the word."},
    {"q": "Choose the correct spelling:", "options": ["seperate", "seperete", "separate"], "ans": "separate", "exp": "Remember: 'par' means equal/even, which is how things are separated."},
    {"q": "Choose the correct spelling:", "options": ["recieve", "receive", "receeve"], "ans": "receive", "exp": "Rule: 'I before E, except after C'."},
    {"q": "Choose the correct word: 'I am going to ___ store.'", "options": ["there", "their", "they're"], "ans": "there", "exp": "'There' refers to a place."},
    {"q": "Choose the correct word: 'This is ___ book.'", "options": ["there", "their", "they're"], "ans": "their", "exp": "'Their' shows possession (belongs to them)."},
    {"q": "Choose the correct word: '___ going to the park.'", "options": ["there", "their", "they're"], "ans": "they're", "exp": "'They're' is a contraction for 'they are'."},
    {"q": "Choose the correct word: '___ my best friend.'", "options": ["Your", "You're"], "ans": "You're", "exp": "'You're' is a contraction for 'you are'."},
    {"q": "Choose the correct word: 'Is this ___ jacket?'", "options": ["Your", "You're"], "ans": "Your", "exp": "'Your' shows possession."},
    {"q": "What is the past tense of 'go'?", "options": ["goed", "went", "gone"], "ans": "went", "exp": "'Go' is an irregular verb."},
    {"q": "What is the past tense of 'eat'?", "options": ["eated", "ate", "eaten"], "ans": "ate", "exp": "'Eat' is an irregular verb."},
    {"q": "What is the plural of 'child'?", "options": ["childs", "childrens", "children"], "ans": "children", "exp": "'Child' has an irregular plural form."},
    {"q": "What is the plural of 'city'?", "options": ["citys", "cities", "cityes"], "ans": "cities", "exp": "Words ending in consonant+y change to -ies."},
    {"q": "Which word is an adjective?", "options": ["run", "beautiful", "quickly"], "ans": "beautiful", "exp": "Adjectives describe nouns."},
    {"q": "Which word is an adverb?", "options": ["happy", "sing", "softly"], "ans": "softly", "exp": "Adverbs often end in -ly and describe verbs."},
    {"q": "Which word is a noun?", "options": ["jump", "elephant", "green"], "ans": "elephant", "exp": "Nouns are people, places, or things."},
]

RANDOM_WORDS = {
    "noun":        ["dragon", "backpack", "sandwich", "volcano", "pillow", "banana"],
    "plural_noun": ["penguins", "pancakes", "socks", "rockets", "cupcakes", "robots"],
    "verb":        ["gallop", "sneeze", "juggle", "moonwalk", "whisper", "cartwheel"],
    "verb_past":   ["danced", "tiptoed", "sprinted", "wiggled", "teleported", "zoomed"],
    "verb_ing":    ["singing", "tap-dancing", "burping", "floating", "somersaulting", "snoring"],
    "adjective":   ["gigantic", "purple", "slimy", "hilarious", "sparkly", "grumpy"],
    "adverb":      ["quickly", "silently", "clumsily", "dramatically", "gracefully", "wildly"],
    "name":        ["Alex", "Grandma Rosie", "Captain Max", "Professor Leo", "Mia", "Uncle Bob"],
    "place":       ["library", "the Moon", "volcano", "supermarket", "castle", "water park"],
    "animal":      ["penguin", "flamingo", "llama", "hedgehog", "octopus", "goat"],
    "food":        ["spaghetti", "ice cream", "pickles", "pizza", "watermelon", "hot chocolate"],
    "exclamation": ["Wow!", "Oh no!", "Holy moly!", "Yikes!", "Amazing!", "Oops!"],
    "number":      ["7", "twenty-three", "100", "1,000", "42", "eighty"],
    "color":       ["neon green", "purple", "golden", "invisible", "sparkly pink", "blue"],
    "occupation":  ["zookeeper", "astronaut", "chef", "firefighter", "magician", "librarian"],
    "emotion":     ["excited", "nervous", "confused", "delighted", "suspicious", "sleepy"],
    "object":      ["umbrella", "trombone", "rubber duck", "toaster", "skateboard", "pillow"],
}

STORIES = [
    {"title": "A Day at the Zoo",
     "text": ("Yesterday, my friend {name} and I went to the {adjective} zoo. "
              "The first animal we saw was a {animal} {verb_ing} very {adverb}. "
              "Suddenly, a {color} {animal} stole my {food} and ran toward the {place}! "
              "The {occupation} just laughed and said, \u201c{exclamation} That happens "
              "here every single day!\u201d On the way home, we stopped to {verb} in the park.")},
    {"title": "The First Day of School",
     "text": ("On the first day of school, I woke up feeling very {emotion}. "
              "I put on my {adjective} clothes, grabbed my {object}, and walked to the {place}. "
              "My teacher, Ms. {name}, asked everyone to {verb} their {plural_noun}. "
              "At lunch, I shared my {food} with the class pet, a very {adjective} {animal}. "
              "When the final bell rang, I {verb_past} all the way home.")},
    {"title": "The Mysterious Letter",
     "text": ("One {adjective} morning, {name} found a {color} envelope under the {object}. "
              "Inside was a short message: \u201cMeet me at the {place} at {number} o\u2019clock "
              "\u2014 and bring {plural_noun}.\u201d Feeling {emotion}, {name} packed a bag with "
              "{food} and {verb_past} out the door. Waiting at the {place} was a friendly "
              "{occupation} holding a {animal} on a leash. \u201cPerfect timing,\u201d they said. "
              "\u201cWe are about to {verb}!\u201d")},
    {"title": "My Dream Vacation",
     "text": ("If I could travel anywhere, I would go to {place} with my best friend {name}. "
              "We would sleep in a {adjective} hotel, eat {food} every morning, and ride a "
              "{animal} across the mountains. Every day we would {verb} {adverb}, and every "
              "evening we would watch the {color} sunset together. After {number} wonderful "
              "days, we would come home \u2014 {emotion}, but very happy.")},
    {"title": "The Lost Robot",
     "text": ("Once upon a time, a small robot named {name} lived in a {adjective} laboratory. "
              "One night, it decided to {verb} out into the world to search for {plural_noun}. "
              "On the way, a {animal} shouted, \u201c{exclamation} You dropped your {object}!\u201d "
              "The robot felt so {emotion} that it started {verb_ing} right there in the street. "
              "Together they walked to the {place}, and from that day on, they were best friends.")},
    {"title": "The Cooking Disaster",
     "text": ("Today I decided to cook {food} for my family. First, I {verb_past} to the "
              "{place} to buy {plural_noun} and a {color} {object}. My {adjective} kitchen "
              "quickly filled with smoke, and my {animal} ran away {adverb}. "
              "\u201c{exclamation}\u201d shouted {name}. \u201cWhat are you {verb_ing}?\u201d "
              "In the end, we ordered {food} \u2014 it was delicious, and I was {emotion} again.")},
]

IRREGULAR_PLURALS = {"children", "people", "men", "women", "feet", "teeth", "mice", "geese", "fish", "sheep"}
IRREGULAR_VERBS_PAST = {"ran", "ate", "sang", "went", "came", "saw", "did", "made", "took", "got", "gave", "find", "found", "thought", "told", "became", "felt", "left", "kept", "held", "brought", "began", "bought", "caught", "chose", "drew", "drove", "fell", "flew", "grew", "knew", "lost", "met", "paid", "read", "rode", "said", "sold", "sat", "slept", "spoke", "spent", "stood", "swam", "taught", "threw", "wore", "wrote", "won", "built"}
IRREGULAR_ADVERBS = {"fast", "hard", "well", "late", "early", "high", "low", "far", "soon", "now", "always", "never", "often", "sometimes", "again", "together", "very", "too", "almost", "yesterday", "today"}
WORD_NUMBERS = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "twenty", "thirty", "fifty", "hundred", "thousand", "million", "dozen", "couple", "half"}

CHECK_SETS = {
    "verb": {"run", "eat", "walk", "talk", "jump", "sing", "read", "write", "sleep", "play", "make", "go", "come", "see", "take", "get", "give", "find", "dance", "laugh", "cry", "smile", "shout", "whisper", "climb", "kick", "carry", "open", "close", "help", "love", "watch", "listen", "learn", "study", "cook", "clean", "wash", "call", "ask", "answer", "visit", "travel", "move", "stop", "start", "finish", "try", "use", "show"},
    "adjective": {"big", "small", "tall", "short", "long", "fast", "slow", "hot", "cold", "warm", "new", "old", "young", "happy", "sad", "angry", "tired", "hungry", "beautiful", "clean", "dirty", "easy", "loud", "quiet", "strong", "weak", "rich", "poor", "brave", "shy", "smart", "funny", "kind", "bright", "dark", "delicious", "wonderful", "amazing", "boring", "interesting", "expensive", "cheap", "tiny", "huge", "gigantic", "sparkly", "grumpy", "purple", "slimy"},
    "animal": {"dog", "cat", "bird", "fish", "horse", "cow", "pig", "sheep", "goat", "chicken", "duck", "rabbit", "mouse", "snake", "turtle", "frog", "bear", "lion", "tiger", "elephant", "monkey", "zebra", "giraffe", "wolf", "fox", "deer", "owl", "eagle", "parrot", "penguin", "flamingo", "llama", "hedgehog", "octopus", "shark", "whale", "dolphin", "dragon", "unicorn", "dinosaur", "kangaroo", "koala", "panda", "bat", "spider", "bee", "butterfly", "snail", "crab"},
    "food": {"pizza", "burger", "sandwich", "salad", "soup", "rice", "pasta", "spaghetti", "noodles", "bread", "cheese", "egg", "chicken", "taco", "sushi", "curry", "pancakes", "waffles", "yogurt", "apple", "banana", "orange", "grape", "strawberry", "watermelon", "pineapple", "mango", "carrot", "potato", "tomato", "cake", "cookie", "pie", "ice cream", "chocolate", "candy", "donut", "popcorn", "pickles", "honey", "juice", "milk", "tea", "coffee", "hot chocolate"},
    "color": {"red", "blue", "green", "yellow", "orange", "purple", "pink", "brown", "black", "white", "gray", "gold", "golden", "silver", "violet", "turquoise", "navy", "beige", "lavender", "rainbow"},
    "occupation": {"doctor", "nurse", "teacher", "engineer", "lawyer", "police officer", "firefighter", "chef", "cook", "waiter", "farmer", "carpenter", "plumber", "electrician", "pilot", "astronaut", "sailor", "scientist", "programmer", "artist", "musician", "singer", "dancer", "actor", "writer", "photographer", "librarian", "zookeeper", "veterinarian", "dentist", "baker", "bus driver", "magician", "clown", "athlete", "coach", "architect", "accountant", "cashier", "manager"},
    "emotion": {"happy", "sad", "angry", "excited", "nervous", "scared", "afraid", "brave", "calm", "worried", "proud", "surprised", "shocked", "confused", "bored", "tired", "sleepy", "hungry", "lonely", "grateful", "jealous", "curious", "hopeful", "disappointed", "frustrated", "annoyed", "delighted", "joyful", "cheerful", "suspicious", "relaxed", "stressed", "silly"},
    "object": {"umbrella", "phone", "keys", "wallet", "glasses", "watch", "hat", "scarf", "shoes", "socks", "shirt", "jacket", "bag", "backpack", "book", "pen", "pencil", "paper", "notebook", "scissors", "brush", "comb", "toothbrush", "towel", "pillow", "blanket", "chair", "table", "lamp", "mirror", "clock", "cup", "plate", "spoon", "fork", "pan", "toaster", "television", "camera", "computer", "laptop", "guitar", "skateboard", "bicycle", "rubber duck", "ladder", "bucket", "broom"},
}

def validate_word(t, w):
    w = w.strip()
    if not w: return None, ""
    wl = w.lower()
    alpha = w.replace(" ", "").replace("-", "").replace("'", "").isalpha()

    # Global Common Misspelling Check
    if wl in COMMON_MISSPELLINGS:
        return "warn", f"Spelling: Did you mean '{COMMON_MISSPELLINGS[wl]}'?"

    if t == "plural_noun":
        if not alpha: return "warn", "Plural nouns are usually plain words (no numbers)."
        if wl in IRREGULAR_PLURALS: return "good", "Looks like an irregular plural noun!"
        if wl.endswith("ies") and len(wl) > 3: return "good", "Nice plural (y -> ies)!"
        if wl.endswith("s") and not wl.endswith("ys"):
            if len(wl) > 2 and wl[-2] not in "aeiou" and wl[-1] == 'y':
                return "warn", "Spelling tip: Words ending in consonant+y change to -ies (e.g., city -> cities)."
            return "good", "Looks like a plural noun!"
        return "warn", "Most plural nouns end in -s (or are irregular: children, feet…)."
    
    if t == "verb_past":
        if not alpha: return "warn", "Verbs are action words — avoid numbers here."
        if wl in IRREGULAR_VERBS_PAST: return "good", "Looks like an irregular past tense!"
        if wl.endswith("ied") and len(wl) > 3: return "good", "Nice past tense (y -> ied)!"
        if wl.endswith("ed"):
            if len(wl) > 2 and wl[-3] == wl[-2] and wl[-1] == 'd': # e.g., walkked
                return "warn", "Spelling tip: Don't double the consonant unless the verb ends in CVC (e.g., stop -> stopped)."
            return "good", "Looks like past tense!"
        return "warn", "Past verbs usually end in -ed or are irregular (ran, ate, went…)."
    
    if t == "verb_ing":
        if not alpha: return "warn", "Verbs are action words — avoid numbers here."
        if wl.endswith("ing") and len(wl) > 4:
            if len(wl) > 4 and wl[-4] == wl[-3] and wl[-2:] == "ng": # e.g., runninging
                pass # It's valid
            return "good", "Nice -ing form!"
        return "warn", "This form should end in -ing (running, eating, dancing…)."
    
    if t == "adverb":
        if not alpha: return "warn", "Adverbs are usually plain words."
        if wl.endswith("ly") or wl in IRREGULAR_ADVERBS: return "good", "Looks like an adverb!"
        return "warn", "Many adverbs end in -ly (quickly, softly, happily…)."
    
    if t == "number":
        if any(ch.isdigit() for ch in w) or wl in WORD_NUMBERS: return "good", "Good number!"
        return "warn", "Try a number like 7, 25, or twenty."
    
    if t == "exclamation":
        if w.endswith(("!", "?", "...")): return "good", "Great exclamation!"
        return "warn", "Exclamations often end with ! (Wow!)"
    
    if t == "name":
        parts = w.split()
        if parts and all(p[0].isupper() for p in parts if p): return "good", "Names start with a capital letter!"
        return "warn", "Names usually start with a capital letter (Maria)."
    
    if t in CHECK_SETS:
        if wl in CHECK_SETS[t]: return "good", f"\u201c{w}\u201d is a great {WORD_TYPES[t][0].lower()}!"
        if not alpha: return "warn", "Usually a plain word without numbers."
        return None, ""
    
    if not alpha: return "warn", "Usually a plain word without numbers."
    return None, ""

def style_edit(edit, status):
    colors = {"good": "#43a047", "warn": "#ef6c00"}
    if status in colors:
        edit.setStyleSheet(f"border: 2px solid {colors[status]}; border-radius: 6px;")
    else:
        edit.setStyleSheet("")

# ============================== Persistence ==============================
class Storage:
    DEFAULT = {
        "stats": {"score": 0, "stories": 0, "words": 0, "streak": 0, "last_day": "", "by_type": {}},
        "settings": {"difficulty": "easy", "theme": "light"},
        "saved": [],
        "custom": [],
        "history": {t: [] for t in WORD_TYPES},
        "achievements": [],
        "quiz_correct": 0
    }

    def __init__(self, path: Path):
        self.path = path
        self.data = json.loads(json.dumps(self.DEFAULT))
        if path.exists():
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
                for k, v in loaded.items():
                    if k in self.data:
                        if isinstance(v, dict) and isinstance(self.data[k], dict):
                            self.data[k].update(v)
                        else:
                            self.data[k] = v
                for t in WORD_TYPES:
                    self.data["history"].setdefault(t, [])
            except Exception:
                pass

    def save(self):
        try:
            self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    def unlock_achievement(self, key):
        if key not in self.data["achievements"] and key in ACHIEVEMENTS:
            self.data["achievements"].append(key)
            self.save()
            return True
        return False

    def record_story(self, results, score):
        st = self.data["stats"]
        st["score"] += score
        st["stories"] += 1
        st["words"] += len(results)
        is_perfect = True
        for t, status in results:
            if status is not None and status != "auto":
                rec = st["by_type"].setdefault(t, {"tried": 0, "good": 0})
                rec["tried"] += 1
                if status == "good":
                    rec["good"] += 1
                else:
                    is_perfect = False
            elif status == "auto":
                is_perfect = False

        for t, w, status, _ in results:
            if w and status not in ("auto", None):
                if w not in self.data["history"][t]:
                    self.data["history"][t].append(w)
                    if len(self.data["history"][t]) > 50:
                        self.data["history"][t].pop(0)

        self.unlock_achievement("first_story")
        if st["stories"] >= 10: self.unlock_achievement("stories_10")
        if is_perfect and len(results) > 0: self.unlock_achievement("perfect")
        self._touch_streak()
        self.save()

    def record_quiz_correct(self):
        self.data["quiz_correct"] += 1
        if self.data["quiz_correct"] >= 10:
            self.unlock_achievement("quiz_master")
        self.save()

    def _touch_streak(self):
        st = self.data["stats"]
        today = date.today()
        if st.get("last_day") == today.isoformat(): return
        yesterday = (today - timedelta(days=1)).isoformat()
        st["streak"] = st.get("streak", 0) + 1 if st.get("last_day") == yesterday else 1
        st["last_day"] = today.isoformat()
        if st["streak"] >= 3: self.unlock_achievement("streak_3")

    def reset_stats(self):
        self.data["stats"] = json.loads(json.dumps(self.DEFAULT["stats"]))
        self.data["quiz_correct"] = 0
        self.save()

# ============================== Text-to-speech ==============================
class Speaker:
    def __init__(self):
        self.engine = None
        if TTS_AVAILABLE:
            try:
                self.engine = QTextToSpeech()
                for v in self.engine.voices():
                    if v.locale().name().startswith("en"):
                        self.engine.setVoice(v)
                        break
                self.engine.setRate(-0.1)
            except Exception:
                self.engine = None

    @property
    def available(self): return self.engine is not None

    def say(self, text):
        if self.engine:
            self.engine.stop()
            self.engine.say(text)

    def stop(self):
        if self.engine: self.engine.stop()

# ============================== Mad Libs Widget ==============================
class MadlibWidget(QWidget):
    def __init__(self, storage: Storage, speaker: Speaker):
        super().__init__()
        self.storage = storage
        self.speaker = speaker
        self.story = None
        self.inputs = []
        self.last_results = []

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_start_page())
        page1, self._input_refs = self._build_input_page()
        self.stack.addWidget(page1)
        self.stack.addWidget(self._build_result_page())
        
        self.input_title = self._input_refs["title"]
        self.input_hint = self._input_refs["hint"]
        self.input_progress = self._input_refs["progress"]
        self.input_count = self._input_refs["count"]
        self.fill_random_btn = self._input_refs["random"]
        self.form_scroll = self._input_refs["scroll"]

        layout = QVBoxLayout(self)
        layout.addWidget(self.stack)
        self.refresh_stories()

    def _build_start_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        title = QLabel("🎲 Mad Libs — English Practice")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        intro = QLabel("Fill in words without seeing the story, then reveal the silly result.\nSmart grammar & spelling checks give instant feedback and points!")
        intro.setAlignment(Qt.AlignmentFlag.AlignCenter)
        intro.setStyleSheet("color:#555; font-size:13px;")

        # Word of the Day
        wod_word, wod_def = random.choice(WORD_OF_THE_DAY)
        wod_box = QFrame()
        wod_box.setStyleSheet("QFrame { background:#fff8e1; border:1px solid #ffe082; border-radius:8px; padding: 10px; }")
        wod_layout = QVBoxLayout(wod_box)
        wod_title = QLabel("💡 Word of the Day")
        wod_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        wod_title.setStyleSheet("color:#ef6c00;")
        wod_word_lbl = QLabel(f"<b style='font-size:14px;'>{wod_word}</b>")
        wod_def_lbl = QLabel(wod_def)
        wod_def_lbl.setWordWrap(True)
        wod_def_lbl.setStyleSheet("font-size:12px;")
        wod_layout.addWidget(wod_title)
        wod_layout.addWidget(wod_word_lbl)
        wod_layout.addWidget(wod_def_lbl)

        self.story_combo = QComboBox()
        self.story_combo.setFixedWidth(340)
        self.story_combo.setMinimumHeight(36)

        diff_row = QHBoxLayout()
        diff_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        diff_label = QLabel("Difficulty:")
        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["😀 Easy — examples & helper buttons", "🙂 Normal — hints only", "😱 Hard — no help at all!"])
        diff = self.storage.data["settings"].get("difficulty", "easy")
        self.diff_combo.setCurrentIndex({"easy": 0, "normal": 1, "hard": 2}.get(diff, 0))
        self.diff_combo.currentIndexChanged.connect(self._save_difficulty)
        self.diff_combo.setMinimumHeight(34)
        diff_row.addWidget(diff_label)
        diff_row.addWidget(self.diff_combo)

        start_btn = QPushButton("✏️  Start Filling Words")
        start_btn.setMinimumHeight(42)
        start_btn.clicked.connect(self.start_story)

        surprise_btn = QPushButton("🎲 Surprise Me! (all random words)")
        surprise_btn.setMinimumHeight(42)
        surprise_btn.setStyleSheet("QPushButton { background-color: #7b57c9; } QPushButton:hover { background-color: #6a49b0; }")
        surprise_btn.clicked.connect(self.surprise_me)

        layout.addWidget(title)
        layout.addWidget(intro)
        layout.addWidget(wod_box, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.story_combo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(diff_row)
        layout.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(surprise_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        return page

    def _save_difficulty(self, idx):
        self.storage.data["settings"]["difficulty"] = ["easy", "normal", "hard"][idx]
        self.storage.save()

    def refresh_stories(self):
        self.story_combo.clear()
        self.story_combo.addItem("🎲 Random Story")
        for s in STORIES + self.storage.data["custom"]:
            marker = "✏️" if s in self.storage.data["custom"] else "📖"
            self.story_combo.addItem(f"{marker} {s['title']}")

    def _selected_story(self):
        idx = self.story_combo.currentIndex()
        pool = STORIES + self.storage.data["custom"]
        return random.choice(pool) if idx == 0 else pool[idx - 1]

    def _build_input_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        self.input_title = QLabel()
        self.input_title.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        self.input_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_hint = QLabel()
        self.input_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_hint.setStyleSheet("color:#777; font-size:12px;")

        self.input_progress = QProgressBar()
        self.input_progress.setTextVisible(False)
        self.input_progress.setFixedHeight(8)
        self.input_count = QLabel()
        self.input_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_count.setStyleSheet("color:#666; font-size:11px;")

        self.form_scroll = QScrollArea()
        self.form_scroll.setWidgetResizable(True)

        buttons = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.fill_random_btn = QPushButton("🎲 Fill Random Words")
        self.fill_random_btn.clicked.connect(self.fill_all_random)
        create_btn = QPushButton("✨ Create My Story!")
        create_btn.setStyleSheet("QPushButton { background-color: #4caf50; } QPushButton:hover { background-color: #43a047; }")
        create_btn.clicked.connect(self.create_story)
        for b in (back_btn, self.fill_random_btn, create_btn): b.setMinimumHeight(40)
        buttons.addWidget(back_btn)
        buttons.addStretch()
        buttons.addWidget(self.fill_random_btn)
        buttons.addWidget(create_btn)

        layout.addWidget(self.input_title)
        layout.addWidget(self.input_hint)
        layout.addWidget(self.input_progress)
        layout.addWidget(self.input_count)
        layout.addWidget(self.form_scroll, stretch=1)
        layout.addLayout(buttons)

        refs = {"title": self.input_title, "hint": self.input_hint, "progress": self.input_progress, "count": self.input_count, "random": self.fill_random_btn, "scroll": self.form_scroll}
        return page, refs

    def _prepare_input_page(self, story):
        self.story = story
        diff = self.storage.data["settings"].get("difficulty", "easy")
        show_examples = diff == "easy"
        show_desc = diff in ("easy", "normal")
        show_dice = diff == "easy"
        self.fill_random_btn.setEnabled(diff != "hard")

        self.input_title.setText(f"📖 {story['title']}")
        hints = {"easy": "Descriptions and examples are shown. Green = looks right!", "normal": "Type a word for each part of speech. Green = looks right!", "hard": "No hints, no helpers — you're on your own!"}
        self.input_hint.setText(hints[diff])

        self.inputs = []
        blanks = PATTERN.findall(story["text"])
        totals = {t: blanks.count(t) for t in set(blanks)}
        seen = {}

        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(10)
        grid.setContentsMargins(6, 6, 6, 6)

        for i, type_key in enumerate(blanks):
            label, description, examples = WORD_TYPES[type_key]
            seen[type_key] = seen.get(type_key, 0) + 1
            if totals[type_key] > 1: label = f"{label}  #{seen[type_key]}"

            box = QFrame()
            box.setStyleSheet("QFrame { background:#f8fafd; border:1px solid #dbe4ef; border-radius:8px; }")
            v = QVBoxLayout(box)
            v.setContentsMargins(10, 8, 10, 8)
            v.setSpacing(3)

            name_lbl = QLabel(label)
            name_lbl.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            v.addWidget(name_lbl)
            if show_desc:
                desc_lbl = QLabel(description)
                desc_lbl.setWordWrap(True)
                desc_lbl.setStyleSheet("color:#667; font-size:11px;")
                v.addWidget(desc_lbl)

            row = QHBoxLayout()
            edit = QLineEdit()
            edit.setPlaceholderText(f"e.g., {examples}" if show_examples else "Type a word…")
            edit.setMinimumHeight(32)
            
            history = self.storage.data["history"].get(type_key, [])
            if history:
                completer = QCompleter(history)
                completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                completer.setFilterMode(Qt.MatchFlag.MatchContains)
                edit.setCompleter(completer)

            row.addWidget(edit, stretch=1)

            if show_dice:
                dice = QPushButton("🎲")
                dice.setFixedWidth(40)
                dice.setToolTip("Give me a word!")
                dice.clicked.connect(lambda _=False, t=type_key, e=edit: self._fill_one(t, e))
                row.addWidget(dice)

            v.addLayout(row)
            self.inputs.append((type_key, edit))
            grid.addWidget(box, i // 2, i % 2)

        self.form_scroll.setWidget(container)

        edits = [e for _, e in self.inputs]
        for i, (t, edit) in enumerate(self.inputs):
            edit.editingFinished.connect(lambda t=t, e=edit: self._check_field(t, e))
            edit.textChanged.connect(self._update_progress)
            if i + 1 < len(edits): edit.returnPressed.connect(lambda e=edits[i + 1]: e.setFocus())
            else: edit.returnPressed.connect(self.create_story)

        self._update_progress()
        self.stack.setCurrentIndex(1)
        if edits: edits[0].setFocus()

    def _fill_one(self, t, edit):
        edit.setText(random.choice(RANDOM_WORDS[t]))
        self._check_field(t, edit)

    def _check_field(self, t, edit):
        status, tip = validate_word(t, edit.text())
        style_edit(edit, status)
        edit.setToolTip(tip)

    def _update_progress(self):
        total = len(self.inputs)
        filled = sum(1 for _, e in self.inputs if e.text().strip())
        self.input_progress.setMaximum(max(total, 1))
        self.input_progress.setValue(filled)
        self.input_count.setText(f"{filled} / {total} words filled")

    def fill_all_random(self):
        for t, e in self.inputs:
            e.setText(random.choice(RANDOM_WORDS[t]))
            self._check_field(t, e)

    def _build_result_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        self.result_title = QLabel()
        self.result_title.setFont(QFont("Arial", 17, QFont.Weight.Bold))
        self.result_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.score_label = QLabel()
        self.score_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_label.setStyleSheet("color:#2e7d32;")

        self.result_browser = QTextBrowser()
        self.result_browser.setFont(QFont("Arial", 13))
        self.result_browser.setOpenExternalLinks(False)

        self.result_note = QLabel()
        self.result_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_note.setStyleSheet("color:#b06000; font-size:12px;")

        audio_row = QHBoxLayout()
        self.read_btn = QPushButton("🔊 Read Aloud")
        self.read_btn.setMinimumHeight(38)
        self.read_btn.clicked.connect(self.read_aloud)
        stop_btn = QPushButton("⏹ Stop")
        stop_btn.setMinimumHeight(38)
        stop_btn.clicked.connect(self.speaker.stop)
        if not self.speaker.available:
            self.read_btn.setEnabled(False)
            self.read_btn.setToolTip("Text-to-speech is not available on this system")
        audio_row.addWidget(self.read_btn)
        audio_row.addWidget(stop_btn)
        audio_row.addStretch()

        buttons = QHBoxLayout()
        save_btn = QPushButton("💾 Save to My Stories")
        save_btn.setStyleSheet("QPushButton { background-color: #7b57c9; } QPushButton:hover { background-color: #6a49b0; }")
        save_btn.clicked.connect(self.save_story)
        copy_btn = QPushButton("📋 Copy")
        copy_btn.clicked.connect(self.copy_story)
        again_btn = QPushButton("🔁 Try Again")
        again_btn.clicked.connect(self.play_again)
        new_btn = QPushButton("📖 New Story")
        new_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        for b in (save_btn, copy_btn, again_btn, new_btn): b.setMinimumHeight(40)
        buttons.addWidget(save_btn)
        buttons.addWidget(copy_btn)
        buttons.addWidget(again_btn)
        buttons.addWidget(new_btn)

        layout.addWidget(self.result_title)
        layout.addWidget(self.score_label)
        layout.addWidget(self.result_browser, stretch=1)
        layout.addWidget(self.result_note)
        layout.addLayout(audio_row)
        layout.addLayout(buttons)
        return page

    def start_story(self): self._prepare_input_page(self._selected_story())

    def surprise_me(self):
        self._prepare_input_page(self._selected_story())
        self.fill_all_random()
        self.create_story()

    def create_story(self):
        if self.story is None: return
        words, results, auto_filled = [], [], 0
        for t, edit in self.inputs:
            w = edit.text().strip()
            if not w:
                w = random.choice(RANDOM_WORDS[t])
                auto_filled += 1
                status, tip = "auto", ""
            else:
                status, tip = validate_word(t, w)
            words.append((t, w, status, tip))
            results.append((t, w, status, tip))

        score = sum(POINTS.get(s, 0) for _, _, s, _ in results)
        self.last_results = results

        word_iter_plain = iter(words)
        self.last_plain = PATTERN.sub(lambda m: next(word_iter_plain)[1], self.story["text"])

        word_iter_html = iter(words)
        def html_replacer(match):
            t, w, s, tip = next(word_iter_html)
            safe_w = html.escape(w)
            return f'<span style="background-color:#ffe3ee; color:#c2185b; font-weight:bold;">{safe_w}</span>'
        
        escaped_story_text = html.escape(self.story["text"])
        story_html = PATTERN.sub(html_replacer, escaped_story_text)

        icons = {"good": "✅", "warn": "⚠️", "auto": "🎲", None: "➖"}
        recap = "".join(
            f"• {icons.get(s, '➖')} <b>{WORD_TYPES.get(t, (t,))[0]}</b> — {html.escape(w)}"
            + (f'<br>&nbsp;&nbsp;&nbsp;<i style="color:#b06000;">{html.escape(tip)}</i>' if s == "warn" and tip else "")
            + ("<i style='color:#888;'> (filled for you)</i>" if s == "auto" else "")
            + "<br>" for t, w, s, tip in results)

        self.result_title.setText(f"📖 {self.story['title']}")
        self.score_label.setText(f"⭐ +{score} points")
        self.result_browser.setHtml(f'<p style="line-height:1.6;">{story_html}</p><hr><p><b>📚 Your words & grammar check:</b><br>{recap}</p>')
        self.result_note.setText(f"(We randomly filled {auto_filled} empty field(s) for you — no points for those)" if auto_filled else "")

        self.storage.record_story([(t, s) for t, _, s, _ in results], score)
        streak = self.storage.data["stats"]["streak"]
        if streak > 1:
            self.result_note.setText((self.result_note.text() + "  " if self.result_note.text() else "") + f"🔥 {streak}-day learning streak!")

        self.speaker.stop()
        self.stack.setCurrentIndex(2)

    def read_aloud(self): self.speaker.say(self.last_plain)
    def copy_story(self): QApplication.clipboard().setText(self.last_plain)

    def save_story(self):
        self.storage.data["saved"].append({
            "title": self.story["title"],
            "text": self.last_plain,
            "score": sum(POINTS.get(s, 0) for _, _, s, _ in self.last_results),
            "date": date.today().isoformat(),
            "words": [[t, w] for t, w, _, _ in self.last_results],
        })
        self.storage.save()
        QMessageBox.information(self, "Saved", "Story saved!\nSee it in the 📕 My Stories tab.")

    def play_again(self):
        for _, edit in self.inputs:
            edit.clear()
            edit.setStyleSheet("")
            edit.setToolTip("")
        self._update_progress()
        self.stack.setCurrentIndex(1)
        if self.inputs: self.inputs[0][1].setFocus()

# ============================== Practice Quiz Tab ==============================
class QuizWidget(QWidget):
    def __init__(self, storage: Storage, speaker: Speaker):
        super().__init__()
        self.storage = storage
        self.speaker = speaker
        self.current_q = None
        self.score = 0
        self.asked_indices = set()

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("🎯 Practice Quiz")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.score_lbl = QLabel("Session Score: 0")
        self.score_lbl.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_lbl.setStyleSheet("color:#2e7d32;")

        self.question_box = QGroupBox("Question")
        q_layout = QVBoxLayout(self.question_box)
        
        self.question_lbl = QLabel("Click 'Start Quiz' to begin!")
        self.question_lbl.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        q_layout.addWidget(self.question_lbl)

        self.options_group = QButtonGroup(self)
        self.options_layout = QVBoxLayout()
        for i in range(3):
            btn = QRadioButton()
            btn.setVisible(False)
            btn.clicked.connect(self.check_answer)
            self.options_group.addButton(btn, i)
            self.options_layout.addWidget(btn)
        q_layout.addLayout(self.options_layout)

        self.feedback_lbl = QLabel("")
        self.feedback_lbl.setFont(QFont("Arial", 12))
        self.feedback_lbl.setWordWrap(True)
        self.feedback_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        q_layout.addWidget(self.feedback_lbl)

        btn_row = QHBoxLayout()
        self.next_btn = QPushButton("Next Question ➡️")
        self.next_btn.setEnabled(False)
        self.next_btn.setMinimumHeight(40)
        self.next_btn.clicked.connect(self.next_question)
        
        start_btn = QPushButton("🔄 Start New Quiz")
        start_btn.setMinimumHeight(40)
        start_btn.clicked.connect(self.start_quiz)
        
        btn_row.addWidget(start_btn)
        btn_row.addWidget(self.next_btn)

        layout.addWidget(title)
        layout.addWidget(self.score_lbl)
        layout.addWidget(self.question_box)
        layout.addStretch()
        layout.addLayout(btn_row)

    def start_quiz(self):
        self.score = 0
        self.asked_indices.clear()
        self.score_lbl.setText("Session Score: 0")
        self.next_question()

    def next_question(self):
        self.feedback_lbl.setText("")
        self.next_btn.setEnabled(False)
        
        available = [i for i in range(len(QUIZ_BANK)) if i not in self.asked_indices]
        if not available:
            self.question_lbl.setText("🎉 You finished all questions! Great job!")
            for btn in self.options_group.buttons():
                btn.setVisible(False)
            return

        idx = random.choice(available)
        self.asked_indices.add(idx)
        self.current_q = QUIZ_BANK[idx]

        self.question_lbl.setText(self.current_q["q"])
        for i, opt in enumerate(self.current_q["options"]):
            btn = self.options_group.button(i)
            btn.setText(opt)
            btn.setVisible(True)
            btn.setEnabled(True)
            btn.setChecked(False)

    def check_answer(self):
        selected_id = self.options_group.checkedId()
        if selected_id == -1: return

        selected_text = self.current_q["options"][selected_id]
        correct_ans = self.current_q["ans"]

        for btn in self.options_group.buttons():
            btn.setEnabled(False)

        if selected_text == correct_ans:
            self.score += 1
            self.score_lbl.setText(f"Session Score: {self.score}")
            self.feedback_lbl.setText(f"✅ Correct! {self.current_q['exp']}")
            self.feedback_lbl.setStyleSheet("color:#2e7d32;")
            self.storage.record_quiz_correct()
        else:
            self.feedback_lbl.setText(f"❌ Oops! The correct answer was: '{correct_ans}'.\n{self.current_q['exp']}")
            self.feedback_lbl.setStyleSheet("color:#c62828;")
        
        if self.speaker.available:
            self.speaker.say(correct_ans)

        self.next_btn.setEnabled(True)

# ============================== Saved-Story Dialog ==============================
class StoryDialog(QDialog):
    def __init__(self, record, speaker, parent=None):
        super().__init__(parent)
        self.record = record
        self.speaker = speaker
        self.setWindowTitle(record["title"])
        self.resize(560, 460)

        layout = QVBoxLayout(self)
        header = QLabel(f"📖 {record['title']}")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        meta = QLabel(f"{record['date']}   ·   ⭐ {record['score']} points")
        meta.setStyleSheet("color:#777;")

        browser = QTextBrowser()
        words_html = "".join(f"• <b>{WORD_TYPES.get(t, (t,))[0]}</b> — {html.escape(w)}<br>" for t, w in record["words"])
        browser.setHtml(f'<p style="line-height:1.6;">{html.escape(record["text"])}</p><hr><p><b>📚 Words used:</b><br>{words_html}</p>')

        buttons = QHBoxLayout()
        read_btn = QPushButton("🔊 Read Aloud")
        read_btn.setEnabled(speaker.available)
        read_btn.clicked.connect(lambda: speaker.say(record["text"]))
        
        export_html_btn = QPushButton("📄 Export HTML")
        export_html_btn.clicked.connect(self.export_html)
        
        copy_btn = QPushButton("📋 Copy")
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(record["text"]))
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        buttons.addWidget(read_btn)
        buttons.addWidget(export_html_btn)
        buttons.addWidget(copy_btn)
        buttons.addStretch()
        buttons.addWidget(close_btn)

        layout.addWidget(header)
        layout.addWidget(meta)
        layout.addWidget(browser, stretch=1)
        layout.addLayout(buttons)

    def export_html(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Story as HTML", f"{self.record['title']}.html", "HTML files (*.html)")
        if not path: return
        words_html = "".join(f"<li><b>{WORD_TYPES.get(t, (t,))[0]}</b>: {html.escape(w)}</li>" for t, w in self.record["words"])
        full_html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{html.escape(self.record['title'])}</title></head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; line-height: 1.6;">
    <h1>{html.escape(self.record['title'])}</h1>
    <p style="color:#666;">Date: {self.record['date']} | Score: {self.record['score']} pts</p>
    <hr>
    <p>{html.escape(self.record['text'])}</p>
    <hr>
    <h3>Words Used:</h3>
    <ul>{words_html}</ul>
</body>
</html>"""
        Path(path).write_text(full_html, encoding="utf-8")
        QMessageBox.information(self, "Exported", f"Story exported successfully to:\n{path}")

# ============================== My Stories Tab ==============================
class MyStoriesWidget(QWidget):
    def __init__(self, storage: Storage, speaker: Speaker):
        super().__init__()
        self.storage = storage
        self.speaker = speaker
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        title = QLabel("📕 My Story Collection")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.open_selected)

        self.empty_label = QLabel("No saved stories yet.\nCreate one in the 🎲 Mad Libs tab!")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color:#999; font-size:13px;")

        buttons = QHBoxLayout()
        open_btn = QPushButton("📖 Read")
        del_btn = QPushButton("🗑 Delete")
        export_btn = QPushButton("💾 Export All to File")
        clear_btn = QPushButton("Clear All")
        for b in (open_btn, del_btn, export_btn, clear_btn): b.setMinimumHeight(38)
        open_btn.clicked.connect(self.open_selected)
        del_btn.clicked.connect(self.delete_selected)
        export_btn.clicked.connect(self.export_all)
        clear_btn.clicked.connect(self.clear_all)
        buttons.addWidget(open_btn)
        buttons.addWidget(del_btn)
        buttons.addStretch()
        buttons.addWidget(export_btn)
        buttons.addWidget(clear_btn)

        layout.addWidget(title)
        layout.addWidget(self.empty_label)
        layout.addWidget(self.list_widget, stretch=1)
        layout.addLayout(buttons)
        self.refresh()

    def refresh(self):
        self.list_widget.clear()
        saved = self.storage.data["saved"]
        self.empty_label.setVisible(not saved)
        self.list_widget.setVisible(bool(saved))
        for rec in reversed(saved):
            self.list_widget.addItem(f"📖 {rec['title']}   ·   {rec['date']}   ·   ⭐ {rec['score']} pts")

    def _selected_record(self):
        idx = self.list_widget.currentRow()
        saved = self.storage.data["saved"]
        if idx < 0: return None
        return saved[len(saved) - 1 - idx]

    def open_selected(self):
        rec = self._selected_record()
        if rec: StoryDialog(rec, self.speaker, self).exec()

    def delete_selected(self):
        rec = self._selected_record()
        if not rec: return
        if QMessageBox.question(self, "Delete", f"Delete \u201c{rec['title']}\u201d?") == QMessageBox.StandardButton.Yes:
            self.storage.data["saved"].remove(rec)
            self.storage.save()
            self.refresh()

    def clear_all(self):
        if not self.storage.data["saved"]: return
        if QMessageBox.question(self, "Clear All", "Delete ALL saved stories?") == QMessageBox.StandardButton.Yes:
            self.storage.data["saved"] = []
            self.storage.save()
            self.refresh()

    def export_all(self):
        saved = self.storage.data["saved"]
        if not saved:
            QMessageBox.information(self, "Export", "Nothing to export yet.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Stories", "my_madlibs.txt", "Text files (*.txt)")
        if not path: return
        lines = []
        for rec in saved:
            lines += [f"=== {rec['title']} === ({rec['date']}, {rec['score']} pts)", ""]
            lines += [rec["text"], ""]
            lines += [f"  - {WORD_TYPES.get(t, (t,))[0]}: {w}" for t, w in rec["words"]]
            lines += ["", ""]
        Path(path).write_text("\n".join(lines), encoding="utf-8")
        QMessageBox.information(self, "Export", f"Saved {len(saved)} stories to:\n{path}")

# ============================== Story Editor Tab ==============================
class StoryEditorWidget(QWidget):
    story_added = pyqtSignal()

    def __init__(self, storage: Storage):
        super().__init__()
        self.storage = storage
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        title = QLabel("✏️ Write Your Own Story")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        help_lbl = QLabel("Write a story and leave blanks like {noun}, {adjective}, {verb_past}… Use the buttons below to insert them. Your story appears in the Mad Libs picker!")
        help_lbl.setWordWrap(True)
        help_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        help_lbl.setStyleSheet("color:#666;")

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Story title (e.g., My Birthday Party)")
        self.title_edit.setMinimumHeight(34)

        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText("Once upon a time, a {adjective} {animal} met {name} at the {place}…")
        self.text_edit.setMinimumHeight(180)

        insert_row = QHBoxLayout()
        insert_lbl = QLabel("Insert blank:")
        self.type_combo = QComboBox()
        self.type_combo.addItems([f"{{{k}}} — {WORD_TYPES[k][0]}" for k in WORD_TYPES])
        insert_btn = QPushButton("➕ Insert")
        insert_btn.clicked.connect(self.insert_placeholder)
        insert_row.addWidget(insert_lbl)
        insert_row.addWidget(self.type_combo, stretch=1)
        insert_row.addWidget(insert_btn)

        self.count_lbl = QLabel("Blanks: 0")
        self.count_lbl.setStyleSheet("color:#777;")
        self.text_edit.textChanged.connect(self.update_count)

        save_btn = QPushButton("💾 Save My Story")
        save_btn.setStyleSheet("QPushButton { background-color: #4caf50; } QPushButton:hover { background-color: #43a047; }")
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.save_story)

        custom_title = QLabel("Your custom stories:")
        custom_title.setStyleSheet("font-weight:bold; margin-top:6px;")
        self.custom_list = QListWidget()
        self.custom_list.setMaximumHeight(110)
        remove_btn = QPushButton("🗑 Remove Selected Story")
        remove_btn.clicked.connect(self.remove_custom)

        layout.addWidget(title)
        layout.addWidget(help_lbl)
        layout.addWidget(self.title_edit)
        layout.addWidget(self.text_edit, stretch=1)
        layout.addLayout(insert_row)
        layout.addWidget(self.count_lbl)
        layout.addWidget(save_btn)
        layout.addWidget(custom_title)
        layout.addWidget(self.custom_list)
        layout.addWidget(remove_btn)
        self.refresh_custom()

    def insert_placeholder(self):
        text = self.type_combo.currentText().split("}")[0] + "}"
        cursor = self.text_edit.textCursor()
        cursor.insertText(text)
        self.text_edit.setFocus()

    def update_count(self):
        self.count_lbl.setText(f"Blanks: {len(PATTERN.findall(self.text_edit.toPlainText()))}")

    def save_story(self):
        t = self.title_edit.text().strip()
        text = self.text_edit.toPlainText().strip()
        blanks = PATTERN.findall(text)
        unknown = [b for b in blanks if b not in WORD_TYPES]
        if not t: QMessageBox.warning(self, "Missing", "Please give your story a title."); return
        if not text: QMessageBox.warning(self, "Missing", "Please write some story text."); return
        if unknown: QMessageBox.warning(self, "Unknown blanks", "These placeholders are not recognized:\n{" + "}, {".join(set(unknown)) + "}"); return
        if len(blanks) < 3: QMessageBox.warning(self, "Too few blanks", "Add at least 3 blanks ({noun}, {adjective}…) to make it fun!"); return
        
        self.storage.data["custom"].append({"title": t, "text": text})
        self.storage.save()
        self.storage.unlock_achievement("creator")
        self.title_edit.clear()
        self.text_edit.clear()
        self.refresh_custom()
        self.story_added.emit()
        QMessageBox.information(self, "Saved!", f"“{t}” added!\nPlay it in the 🎲 Mad Libs tab.")

    def remove_custom(self):
        idx = self.custom_list.currentRow()
        custom = self.storage.data["custom"]
        if 0 <= idx < len(custom):
            if QMessageBox.question(self, "Remove", f"Remove “{custom[idx]['title']}”?") == QMessageBox.StandardButton.Yes:
                custom.pop(idx)
                self.storage.save()
                self.refresh_custom()
                self.story_added.emit()

    def refresh_custom(self):
        self.custom_list.clear()
        for s in self.storage.data["custom"]:
            n = len(PATTERN.findall(s["text"]))
            self.custom_list.addItem(f"✏️ {s['title']}  ({n} blanks)")

# ============================== Grammar Guide Tab ==============================
class GuideWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        tabs.addTab(self._build_pos_tab(), "Parts of Speech")
        tabs.addTab(self._build_irregular_tab(), "Irregular Verbs")
        tabs.addTab(self._build_mistakes_tab(), "Common Mistakes")
        tabs.addTab(self._build_spelling_tab(), "Spelling Rules")
        layout.addWidget(tabs)

    def _build_pos_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        search = QLineEdit()
        search.setPlaceholderText("🔍 Search a part of speech (e.g., 'adverb')…")
        self.search = search

        self.table = QTableWidget(len(WORD_TYPES), 3)
        self.table.setHorizontalHeaderLabels(["Part of Speech", "What it is", "Examples"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for row, (label, description, examples) in enumerate(WORD_TYPES.values()):
            for col, text in enumerate((label, description, examples)):
                item = QTableWidgetItem(text)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                self.table.setItem(row, col, item)
        self.table.resizeRowsToContents()

        search.textChanged.connect(self._filter)
        layout.addWidget(search)
        layout.addWidget(self.table)
        return page

    def _filter(self, text):
        text = text.lower()
        for row in range(self.table.rowCount()):
            match = any(text in (self.table.item(row, c).text().lower() if self.table.item(row, c) else "") for c in range(3))
            self.table.setRowHidden(row, not match)

    def _build_irregular_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        note = QLabel("💡 These verbs don't follow the “-ed” rule — memorize them!")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note.setStyleSheet("color:#666;")

        pairs = [("go", "went"), ("eat", "ate"), ("run", "ran"), ("see", "saw"), ("take", "took"), ("make", "made"), ("buy", "bought"), ("sing", "sang"), ("drink", "drank"), ("swim", "swam"), ("write", "wrote"), ("ride", "rode"), ("fly", "flew"), ("sleep", "slept"), ("give", "gave"), ("find", "found"), ("bring", "brought"), ("teach", "taught"), ("think", "thought"), ("throw", "threw")]

        rows = (len(pairs) + 1) // 2
        table = QTableWidget(rows, 4)
        table.setHorizontalHeaderLabels(["Verb", "Past", "Verb", "Past"])
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for i, (base, past) in enumerate(pairs):
            r, c = i % rows, (i // rows) * 2
            table.setItem(r, c, QTableWidgetItem(base))
            item = QTableWidgetItem(past)
            item.setForeground(QColor("#2e7d32"))
            table.setItem(r, c + 1, item)

        layout.addWidget(note)
        layout.addWidget(table)
        return page

    def _build_mistakes_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        note = QLabel("💡 These are words that sound the same but have different meanings and spellings!")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note.setStyleSheet("color:#666; font-weight:bold;")

        mistakes = [
            ("There", "Refers to a place.", "Look over there!"),
            ("Their", "Shows possession (belongs to them).", "It is their car."),
            ("They're", "Contraction for 'they are'.", "They're going home."),
            ("Your", "Shows possession (belongs to you).", "Is this your book?"),
            ("You're", "Contraction for 'you are'.", "You're my best friend."),
            ("Its", "Shows possession (belongs to it).", "The dog wagged its tail."),
            ("It's", "Contraction for 'it is' or 'it has'.", "It's raining outside."),
            ("To", "Direction or action.", "I went to the store."),
            ("Too", "Means 'also' or 'excessively'.", "I want to come, too! That's too hot."),
            ("Two", "The number 2.", "I have two cats.")
        ]

        table = QTableWidget(len(mistakes), 3)
        table.setHorizontalHeaderLabels(["Word", "Rule / Meaning", "Example"])
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for r, (word, rule, ex) in enumerate(mistakes):
            word_item = QTableWidgetItem(word)
            word_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            table.setItem(r, 0, word_item)
            table.setItem(r, 1, QTableWidgetItem(rule))
            ex_item = QTableWidgetItem(ex)
            ex_item.setForeground(QColor("#ef6c00"))
            table.setItem(r, 2, ex_item)
        
        table.resizeRowsToContents()

        layout.addWidget(note)
        layout.addWidget(table)
        return page

    def _build_spelling_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        note = QLabel("💡 General rules to help you spell tricky words correctly!")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note.setStyleSheet("color:#666; font-weight:bold;")

        rules = [
            ("I before E", "Write 'i' before 'e' except after 'c', or when sounded like 'a' as in 'neighbor' and 'weigh'.", "believe, receive, weight"),
            ("Change Y to I", "When adding a suffix like -ed, -er, or -es to a word ending in a consonant + y, change the y to i.", "cry -> cried, baby -> babies"),
            ("Double Consonants", "For short words (CVC), double the final consonant before adding a suffix starting with a vowel.", "run -> running, sit -> sitting"),
            ("Silent E", "Keep the silent 'e' when adding a suffix starting with a consonant. Drop it if the suffix starts with a vowel.", "careful -> cared, making"),
            ("Plural -s vs -es", "Add '-es' to words ending in s, ss, sh, ch, x, or z.", "buses, boxes, watches")
        ]

        table = QTableWidget(len(rules), 3)
        table.setHorizontalHeaderLabels(["Rule", "Explanation", "Examples"])
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for r, (rule, expl, ex) in enumerate(rules):
            word_item = QTableWidgetItem(rule)
            word_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            table.setItem(r, 0, word_item)
            table.setItem(r, 1, QTableWidgetItem(expl))
            ex_item = QTableWidgetItem(ex)
            ex_item.setForeground(QColor("#2e7d32"))
            table.setItem(r, 2, ex_item)
        
        table.resizeRowsToContents()

        layout.addWidget(note)
        layout.addWidget(table)
        return page

# ============================== Progress Tab ==============================
class ProgressWidget(QWidget):
    def __init__(self, storage: Storage):
        super().__init__()
        self.storage = storage
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel("📈 My Progress")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        stats_grid = QGridLayout()
        stats_grid.setSpacing(14)
        self.big_labels = {}
        stats = [("⭐", "Total Score", "score"), ("📖", "Stories Created", "stories"), ("✏️", "Words Practiced", "words"), ("🔥", "Day Streak", "streak")]
        for col, (icon, name, key) in enumerate(stats):
            box = QFrame()
            box.setStyleSheet("QFrame { background:#f8fafd; border:1px solid #dbe4ef; border-radius:10px; }")
            v = QVBoxLayout(box)
            v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_lbl = QLabel("0")
            value_lbl.setFont(QFont("Arial", 24, QFont.Weight.Bold))
            value_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_lbl.setStyleSheet("color:#2a6fb0;")
            name_lbl = QLabel(f"{icon} {name}")
            name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_lbl.setStyleSheet("color:#666;")
            v.addWidget(value_lbl)
            v.addWidget(name_lbl)
            self.big_labels[key] = value_lbl
            stats_grid.addWidget(box, 0, col)

        acc_title = QLabel("Grammar accuracy by part of speech:")
        acc_title.setStyleSheet("font-weight:bold;")
        self.acc_table = QTableWidget(0, 4)
        self.acc_table.setHorizontalHeaderLabels(["Part of Speech", "Practiced", "Likely Correct", "Accuracy"])
        self.acc_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.acc_table.setAlternatingRowColors(True)
        self.acc_table.verticalHeader().setVisible(False)
        self.acc_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        ach_title = QLabel("🏆 Achievements")
        ach_title.setStyleSheet("font-weight:bold;")
        self.ach_layout = QHBoxLayout()
        
        layout.addWidget(title)
        layout.addLayout(stats_grid)
        layout.addWidget(acc_title)
        layout.addWidget(self.acc_table, stretch=1)
        layout.addWidget(ach_title)
        layout.addLayout(self.ach_layout)
        
        reset_btn = QPushButton("🗑 Reset Progress")
        reset_btn.clicked.connect(self.reset_progress)
        layout.addWidget(reset_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.refresh()

    def refresh(self):
        st = self.storage.data["stats"]
        for key, lbl in self.big_labels.items():
            lbl.setText(str(st.get(key, 0)))

        by_type = st.get("by_type", {})
        rows = [(t, rec) for t, rec in by_type.items() if rec["tried"] > 0]
        rows.sort(key=lambda x: -x[1]["tried"])
        self.acc_table.setRowCount(len(rows))
        for i, (t, rec) in enumerate(rows):
            pct = int(rec["good"] / rec["tried"] * 100)
            values = [WORD_TYPES.get(t, (t,))[0], str(rec["tried"]), str(rec["good"]), f"{pct}%"]
            for c, v in enumerate(values):
                item = QTableWidgetItem(v)
                if c == 3:
                    if pct >= 70: item.setForeground(QColor("#2e7d32"))
                    elif pct >= 40: item.setForeground(QColor("#ef6c00"))
                    else: item.setForeground(QColor("#c62828"))
                self.acc_table.setItem(i, c, item)

        while self.ach_layout.count():
            child = self.ach_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        unlocked = self.storage.data.get("achievements", [])
        for key, (icon, name, desc) in ACHIEVEMENTS.items():
            frame = QFrame()
            frame.setFixedSize(100, 110)
            frame_layout = QVBoxLayout(frame)
            frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            icon_lbl = QLabel(icon)
            icon_lbl.setFont(QFont("Arial", 28))
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            name_lbl = QLabel(name)
            name_lbl.setWordWrap(True)
            name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_lbl.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            
            if key in unlocked:
                frame.setStyleSheet("QFrame { background:#e8f5e9; border: 2px solid #43a047; border-radius: 10px; }")
                name_lbl.setStyleSheet("color: #2e7d32;")
                frame.setToolTip(desc)
            else:
                frame.setStyleSheet("QFrame { background:#f5f5f5; border: 1px dashed #bbb; border-radius: 10px; }")
                icon_lbl.setStyleSheet("color: #ccc;")
                name_lbl.setStyleSheet("color: #999;")
                frame.setToolTip("Locked: " + desc)
                
            frame_layout.addWidget(icon_lbl)
            frame_layout.addWidget(name_lbl)
            self.ach_layout.addWidget(frame)
            
        self.ach_layout.addStretch()

    def reset_progress(self):
        if QMessageBox.question(self, "Reset Progress", "Reset score, stats, and streak?") == QMessageBox.StandardButton.Yes:
            self.storage.reset_stats()
            self.refresh()

# ============================== Main Window ==============================
class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Mad Libs — Learn English with PyQt6")
        self.resize(840, 700)

        self.storage = Storage(Path(__file__).parent / "madlibs_data.json")
        self.speaker = Speaker()

        menubar = self.menuBar()
        view_menu = menubar.addMenu("View")
        
        self.theme_action = QAction("🌙 Dark Mode", self)
        self.theme_action.setCheckable(True)
        self.theme_action.setChecked(self.storage.data["settings"].get("theme") == "dark")
        self.theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.theme_action)

        self.tabs = QTabWidget()
        self.madlib_tab = MadlibWidget(self.storage, self.speaker)
        self.stories_tab = MyStoriesWidget(self.storage, self.speaker)
        self.editor_tab = StoryEditorWidget(self.storage)
        self.guide_tab = GuideWidget()
        self.quiz_tab = QuizWidget(self.storage, self.speaker)
        self.progress_tab = ProgressWidget(self.storage)

        self.tabs.addTab(self.madlib_tab, "🎲 Mad Libs")
        self.tabs.addTab(self.quiz_tab, "🎯 Practice Quiz")
        self.tabs.addTab(self.stories_tab, "📕 My Stories")
        self.tabs.addTab(self.editor_tab, "✏️ Story Editor")
        self.tabs.addTab(self.guide_tab, "📚 Grammar Guide")
        self.tabs.addTab(self.progress_tab, "📈 My Progress")

        self.editor_tab.story_added.connect(self.madlib_tab.refresh_stories)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.setCentralWidget(self.tabs)
        
        self.apply_theme()

    def toggle_theme(self):
        is_dark = self.theme_action.isChecked()
        self.storage.data["settings"]["theme"] = "dark" if is_dark else "light"
        self.storage.save()
        self.apply_theme()

    def apply_theme(self):
        is_dark = self.storage.data["settings"].get("theme") == "dark"
        self.theme_action.setText("☀️ Light Mode" if is_dark else "🌙 Dark Mode")
        
        if is_dark:
            self.app.setStyleSheet("""
                QMainWindow { background: #1e1e2e; }
                QTabWidget::pane { border: 1px solid #45475a; border-radius: 6px; background: #181825; }
                QTabBar::tab { padding: 9px 18px; background: #313244; border: 1px solid #45475a; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; font-size: 13px; color: #cdd6f4; }
                QTabBar::tab:selected { background: #89b4fa; font-weight: bold; color: #11111b; }
                QWidget { color: #cdd6f4; }
                QPushButton { background-color: #89b4fa; color: #11111b; border: none; border-radius: 6px; padding: 8px 14px; font-size: 13px; }
                QPushButton:hover { background-color: #74c7ec; }
                QPushButton:disabled { background-color: #45475a; color: #6c7086; }
                QLineEdit, QPlainTextEdit, QComboBox, QTextBrowser { border: 1px solid #45475a; border-radius: 6px; padding: 6px 8px; font-size: 13px; background: #313244; color: #cdd6f4; }
                QLineEdit:focus, QPlainTextEdit:focus { border: 2px solid #89b4fa; }
                QTableWidget { border: 1px solid #45475a; border-radius: 6px; background: #181825; gridline-color: #45475a; }
                QHeaderView::section { background: #313244; padding: 6px; border: none; font-weight: bold; color: #cdd6f4; }
                QProgressBar { background: #313244; border: none; border-radius: 4px; }
                QProgressBar::chunk { background: #a6e3a1; border-radius: 4px; }
                QListWidget { border: 1px solid #45475a; border-radius: 6px; background: #181825; font-size: 13px; color: #cdd6f4; }
                QListWidget::item:selected { background-color: #89b4fa; color: #11111b; }
                QListWidget::item:hover { background-color: #313244; }
                QTableWidget::item:selected { background-color: #89b4fa; color: #11111b; }
                QMenu { background: #181825; color: #cdd6f4; border: 1px solid #45475a; }
                QMenu::item:selected { background: #89b4fa; color: #11111b; }
                QRadioButton { color: #cdd6f4; spacing: 8px; padding: 4px; }
                QRadioButton::indicator { width: 14px; height: 14px; border-radius: 7px; border: 2px solid #cdd6f4; background: transparent; }
                QRadioButton::indicator:checked { background: #a6e3a1; border: 2px solid #a6e3a1; }
                QGroupBox { border: 1px solid #45475a; border-radius: 8px; margin-top: 10px; padding-top: 10px; color: #cdd6f4; }
                QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #89b4fa; }
                QScrollBar:vertical { border: none; background: #181825; width: 10px; margin: 0px; }
                QScrollBar::handle:vertical { background: #45475a; min-height: 20px; border-radius: 5px; }
                QScrollBar::handle:vertical:hover { background: #585b70; }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; height: 0px; }
                QLabel { color: #cdd6f4; }
            """)
        else:
            self.app.setStyleSheet("""
                QMainWindow { background: #f4f7fb; }
                QTabWidget::pane { border: 1px solid #c9d6e8; border-radius: 6px; background: white; }
                QTabBar::tab { padding: 9px 18px; background: #dde6f2; border: 1px solid #c9d6e8; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; font-size: 13px; }
                QTabBar::tab:selected { background: white; font-weight: bold; }
                QPushButton { background-color: #4a90d9; color: white; border: none; border-radius: 6px; padding: 8px 14px; font-size: 13px; }
                QPushButton:hover { background-color: #3a7bc0; }
                QPushButton:disabled { background-color: #b8c4d0; }
                QLineEdit, QPlainTextEdit, QComboBox { border: 1px solid #c9d6e8; border-radius: 6px; padding: 6px 8px; font-size: 13px; background: white; }
                QLineEdit:focus, QPlainTextEdit:focus { border: 2px solid #4a90d9; }
                QTextBrowser { border: 1px solid #dbe4ef; border-radius: 6px; background: white; }
                QTableWidget { border: 1px solid #dbe4ef; border-radius: 6px; background: white; }
                QHeaderView::section { background: #e8eff8; padding: 6px; border: none; font-weight: bold; }
                QProgressBar { background: #e2e9f2; border: none; border-radius: 4px; }
                QProgressBar::chunk { background: #4caf50; border-radius: 4px; }
                QListWidget { border: 1px solid #dbe4ef; border-radius: 6px; background: white; font-size: 13px; }
                QListWidget::item:selected { background-color: #4a90d9; color: white; }
                QListWidget::item:hover { background-color: #e8eff8; }
                QTableWidget::item:selected { background-color: #4a90d9; color: white; }
                QRadioButton { spacing: 8px; padding: 4px; }
                QGroupBox { border: 1px solid #c9d6e8; border-radius: 8px; margin-top: 10px; padding-top: 10px; font-weight: bold; }
                QScrollBar:vertical { border: none; background: #f4f7fb; width: 10px; margin: 0px; }
                QScrollBar::handle:vertical { background: #c9d6e8; min-height: 20px; border-radius: 5px; }
                QScrollBar::handle:vertical:hover { background: #b8c4d0; }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; height: 0px; }
            """)

    def _on_tab_changed(self, index):
        widget = self.tabs.widget(index)
        if widget is self.madlib_tab: self.madlib_tab.refresh_stories()
        elif widget is self.stories_tab: self.stories_tab.refresh()
        elif widget is self.progress_tab: self.progress_tab.refresh()

# ============================== Entry Point ==============================
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()