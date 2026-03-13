from flask import (
    flash,
    g,
    redirect,
    render_template,
    session,
    url_for,
)

from services.entries_and_emotions.utils import (
    get_valid_page_nums,
    validate_entry,
    validate_unique_emotions,
)

ENTRY_VIEW_LIMIT = 5
ENTRY_ATTRIBUTES = [
    "entry_date",
    "mood_range",
    "energy_level",
    "reflection",
    "emotions",
]


def get_entries(page_num):
    # Validate page_num
    valid_page_nums_list = get_valid_page_nums(ENTRY_VIEW_LIMIT)
    if page_num != 0 and page_num not in valid_page_nums_list:
        flash(f"Page {page_num} out of Entry Views range", "error")
        return redirect(url_for("view_entries"))

    # Get all of users entries id's and entry_date's from db
    entries_info = g.storage.get_users_entries_ids_and_date(
        session["user_id"], page_num, ENTRY_VIEW_LIMIT
    )
    # Store current pagination view in session
    session["page_num"] = page_num
    return render_template(
        "view_entries.html",
        entries_info=entries_info,
        page_num=page_num,
        valid_page_nums_list=valid_page_nums_list,
    )


def entry_creation(entry_date, energy_level, mood_range, reflection, emotions_string):
    user_id = session["user_id"]
    # Validate input
    error_list = validate_entry(entry_date, energy_level, mood_range)
    if error_list:
        for error in error_list:
            flash(error, "error")
        return (
            render_template(
                "create_entry.html",
                entry_date=entry_date,
                energy_level=energy_level,
                mood_range=mood_range,
                reflection=reflection,
                emotions=emotions_string,
            ),
            422,
        )
    # Insert new entry in db
    entry_id = g.storage.create_new_entry(
        user_id, entry_date, energy_level, mood_range, reflection
    )
    # Validate / Insert emotions to db
    if emotions_string:
        g.storage.add_emotions(entry_id[0], emotions_string)
    return redirect(url_for("display_entry", entry_id=entry_id[0]))


def get_entry(entry_id):
    try:
        # Get entry data from db
        id, user_id, date, energy_level, mood_range, reflection = g.storage.get_entry(
            entry_id, session["user_id"]
        )
        # Get all emotions associated with entry from db
        emotions_list = g.storage.get_entry_emotions(entry_id)
        return render_template(
            "view_entry.html",
            entry_id=id,
            date=date,
            energy_level=energy_level,
            mood_range=mood_range,
            reflection=reflection,
            emotions=emotions_list,
        )
    except TypeError:
        flash(f"Unauthorized entry id: {entry_id}", "error")
        return redirect(url_for("view_entries"))


def get_edit_entry_view(entry_id):
    try:
        # Get entry data from db
        id, user_id, date, energy_level, mood_range, reflection = g.storage.get_entry(
            entry_id, session["user_id"]
        )

        # Get all emotions associated with entry from db
        emotions_list = g.storage.get_entry_emotions(entry_id)
        return render_template(
            "edit_entry.html",
            entry_id=entry_id,
            entry_date=date,
            energy_level=energy_level,
            mood_range=mood_range,
            reflection=reflection,
            emotions=" ".join(emotions_list),
        )
    except TypeError:
        flash(f"Unauthorized entry id: {entry_id}", "error")
        return redirect(url_for("view_entries"))


def get_dict_of_attributes_and_values_to_edit(
    input_attribute_value_dict, entry_id, user_id
):
    # accept dict of current input and its values
    # compare input with current values (dict of current attributes and their values)
    # get current values from g.storage.get_entry(entry_id, user_id)
    # returns id, user_id, date, energy_level, mood_range, reflection
    session
    id, user_id, date, energy_level, mood_range, reflection = g.storage.get_entry(
        entry_id, user_id
    )
    current_attributes_dict = {
        "entry_date": date,
        "energy_level": energy_level,
        "mood_range": mood_range,
        "reflection": reflection,
    }

    attributes_with_values_to_edit = {}
    for attribute, input_value in input_attribute_value_dict.items():
        value = current_attributes_dict.get(attribute)
        if value != input_value:
            attributes_with_values_to_edit[attribute] = input_value

    return attributes_with_values_to_edit


def update_entry_and_emotions(
    entry_date, energy_level, mood_range, entry_id, reflection, emotions_string
):
    # Validate input
    error_list = validate_entry(entry_date, energy_level, mood_range, entry_id)
    # TODO get dict of attributes to edit
    input_attribute_value_dict = {
        "entry_date": entry_date,
        "energy_level": energy_level,
        "mood_range": mood_range,
        "reflection": reflection,
    }

    if emotions_string:
        error_list = validate_unique_emotions(emotions_string, error_list)

    if error_list:
        for error in error_list:
            flash(error, "error")
        return (
            render_template(
                "edit_entry.html",
                entry_id=entry_id,
                entry_date=entry_date,
                energy_level=energy_level,
                mood_range=mood_range,
                reflection=reflection,
                emotions=emotions_string,
            ),
            422,
        )  # Redisplay page with current edits + alerts

    user_id = session["user_id"]

    # Identify which of the entries attributes need to be edited
    attributes_to_edit = get_dict_of_attributes_and_values_to_edit(
        input_attribute_value_dict, entry_id, user_id
    )
    # Update the attributes that have been edited
    for attribute, attribute_value in attributes_to_edit.items():
        if attribute == "entry_date":
            g.storage.update_entry_entry_date(attribute_value, entry_id, user_id)
        elif attribute == "mood_range":
            g.storage.update_entry_mood_range(attribute_value, entry_id, user_id)
        elif attribute == "energy_level":
            g.storage.update_entry_energy_level(attribute_value, entry_id, user_id)
        elif attribute == "reflection":
            g.storage.update_entry_reflection(attribute_value, entry_id, user_id)

    if emotions_string:
        # Update emotions
        """
        DESIGN CHOICE: Updating emotions -> Delete and re-add all emotions anew
        see README for more details
        """
        g.storage.delete_entries_emotions(entry_id)
        g.storage.add_emotions(entry_id, emotions_string)

    return redirect(url_for("display_entry", entry_id=entry_id))


def entry_deletion(entry_id):
    entry_date = g.storage.get_entry_date(entry_id, session["user_id"])
    # Delete entry (+ assocciated emotions) from db
    g.storage.delete_entry(entry_id, session["user_id"])
    flash(f"Successfully deleted entry from: {entry_date[0]}", "success")
    return redirect(url_for("view_entries", page_num=session["page_num"]))


def emotion_deletion(entry_id, emotion):
    # Get emotion's id from db
    emotion_id = g.storage.get_emotions_id(emotion, entry_id)
    if emotion_id is None:
        flash(f"Invalid emotion: {emotion}", "error")
        return redirect(url_for("display_edit_entry", entry_id=entry_id))

    # Delete emotion from db
    g.storage.delete_emotion(emotion_id, entry_id)
    return redirect(url_for("display_entry", entry_id=entry_id))
