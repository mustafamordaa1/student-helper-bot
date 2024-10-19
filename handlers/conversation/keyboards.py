from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def create_gender_keyboard() -> list:
    """Creates the gender selection keyboard."""
    return [
        [InlineKeyboardButton("ذكر 👦", callback_data="Male")],
        [InlineKeyboardButton("أنثى 👧", callback_data="Female")],
    ]


def create_class_keyboard() -> list:
    """Creates the class/grade selection keyboard."""
    return [
        [InlineKeyboardButton("الصف الأول متوسط 7️⃣", callback_data="7")],
        [InlineKeyboardButton("الصف الثاني متوسط 8️⃣", callback_data="8")],
        [InlineKeyboardButton("الصف الثالث متوسط 9️⃣", callback_data="9")],
        [InlineKeyboardButton("الصف الأول ثانوي 0️⃣1️⃣", callback_data="10")],
        [InlineKeyboardButton("الصف الثاني ثانوي 1️⃣1️⃣", callback_data="11")],
        [InlineKeyboardButton("الصف الثالث ثانوي 2️⃣1️⃣", callback_data="12")],
        [InlineKeyboardButton("أنهيت المرحلة الثانوية. 🎓", callback_data="Above")],
        [InlineKeyboardButton("لم أدخل المرحلة المتوسطة بعد. 👶", callback_data="Below")],
    ]


def create_voice_written_keyboard() -> list:
    """Creates the voice/written preference selection keyboard."""
    return [
        [InlineKeyboardButton("صوتي 🗣️", callback_data="voice")],
        [InlineKeyboardButton("مكتوب 📝", callback_data="written")],
    ]


def create_yes_no_keyboard() -> list:
    """Creates a simple Yes/No keyboard."""
    return [
        [InlineKeyboardButton("نعم ✅", callback_data="Yes")],
        [InlineKeyboardButton("لا ❌", callback_data="No")],
    ]


def create_preference_keyboard() -> list:
    """Creates the learning material preference selection keyboard."""
    return [
        [InlineKeyboardButton("نص 📄", callback_data="Text")],
        [InlineKeyboardButton("صوت 🎧", callback_data="Audio")],
        [InlineKeyboardButton("فيديو 🎬", callback_data="Video")],
    ]