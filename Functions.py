from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap


def calculate_wpm(start_time, end_time, num_words):
    elapsed_time = end_time - start_time
    minutes = elapsed_time / 60
    wpm = num_words / minutes
    return round(wpm, 2)


def calculate_correctness(user_input, correct_sentence):
    user_words = user_input.split()
    correct_words = correct_sentence.split()
    correct_count = sum(u == c for u, c in zip(user_words, correct_words))
    return correct_count / len(correct_words) * 100


def underline_errors(user_input, correct_sentence):
    user_words = user_input.split()
    correct_words = correct_sentence.split()
    underlined_sentence = []
    for u, c in zip(user_words, correct_words):
        if u == c:
            underlined_sentence.append(u)
        else:
            underlined_sentence.append(f"__{u}__")
    return ' '.join(underlined_sentence)


def update_user_progress(userdata, uid, wpm, accuracy, language):
    user_record = userdata.find_one({"_id": uid})
    if user_record is None:
        userdata.insert_one(
            {"_id": uid, "progress": [], "record": {"wpm": 0, "accuracy": 0, "language": ""}, "xp": 0, "level": 1})

    user_record = userdata.find_one({"_id": uid})
    if 'xp' not in user_record:
        user_record['xp'] = 0
    if 'level' not in user_record:
        user_record['level'] = 1

    xp_gain = calculate_xp_gain(wpm, accuracy)  # Calculate XP gain
    user_record["xp"] += xp_gain  # Update XP
    user_record["level"] = calculate_level(user_record["xp"])  # Update level
    user_record["progress"].append(
        {'userId': uid, 'wpm': wpm, 'accuracy': accuracy, 'date': datetime.now().isoformat(), 'language': language})
    userdata.update_one({"_id": uid}, {
        "$set": {"progress": user_record["progress"], "xp": user_record["xp"], "level": user_record["level"]}})


def get_text_dimensions(text_string, font):
    ascent, descent = font.getmetrics()
    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent
    return (text_width, text_height)


def text_to_image(text):
    fnt = ImageFont.truetype('FilesNeeded/GG Sans.ttf', 30)

    wrapped_text = textwrap.wrap(text, width=80)

    text_sizes = [get_text_dimensions(line, fnt) for line in wrapped_text]

    max_width = max(width for width, height in text_sizes)
    total_height = sum(height for width, height in text_sizes)
    img = Image.new('RGB', (max_width + 25, total_height + 25), color=(54, 57, 63))

    d = ImageDraw.Draw(img)

    current_height = 10
    for i, line in enumerate(wrapped_text):
        d.text((10, current_height), line, font=fnt, fill=(255, 255, 255))
        current_height += text_sizes[i][1]

    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return img_io


# Function to calculate XP gain
def calculate_xp_gain(wpm, accuracy):
    # This is a simple formula, you can adjust it as needed
    return round((wpm * accuracy) / 100)


# Function to calculate level based on XP
def calculate_level(xp):
    # This is a simple formula, you can adjust it as needed
    return xp // 100 + 1
