from flask import g, session


def get_valid_page_nums(entry_view_limit):
    """
    returns list of pages for view_entries pagination
     - determined by users total entry count +
       the # of entries shown in a view_entry page (entry_view_limit)
    """
    total_entries = g.storage.get_user_entry_count(session["user_id"])
    entry_range = list(range(1, total_entries[0] + 1, entry_view_limit))

    valid_page_nums = []
    page_num = 0
    for num in entry_range:
        valid_page_nums.append(page_num)
        page_num += 1
    return valid_page_nums


def validate_entry(entry_date, energy_level, mood_range, edit_entry_id=False):
    """
    return error_list: empty if valid input or string for each error
    errors:
        - missing input for entry_date, energy_level, mood_range
        - entry_date is not unique to user (already have an entry for that date)
    """
    error_list = []
    if not entry_date:
        error_list.append("Missing a date")
    if entry_date and validate_entry_date(entry_date, edit_entry_id):
        error_list.append(f"You already have an entry for this date: {entry_date}.")
    if not energy_level:
        error_list.append("Missing a value for energy level")
    if not mood_range:
        error_list.append("Missing a value for mood range")

    return error_list


def validate_entry_date(entry_date, entry_id):
    """
    check entry_date is unique:
    i.e belongs to current entry being edited / or is new unique date
    if entry_id -> entry is being edited and
        need to check if current entry_date matches input entry_date
    returns None if valid entry_date
    else a date (i.e date already exists for the users entries)
    """
    if entry_id:
        entry_date_is_same = g.storage.get_entry_date(entry_id, session["user_id"])[0]
        if str(entry_date_is_same) == entry_date:  # valid date
            return None

    return g.storage.check_unique_date(session["user_id"], entry_date)


def validate_unique_emotions(emotions_string, error_list):
    """
    check input emotions for duplicate emotion value
    returns list of error values if duplicate else empty list
    """
    count_emotions = {}
    for emotion in emotions_string.split():
        if emotion in count_emotions:
            count_emotions[emotion] += 1
            error_list.append(f'This emotion, "{emotion}", is already listed ')
        else:
            count_emotions[emotion] = 1
    return error_list


def current_emotions_match_emotions_string(emotions_string, entry_id):
    current_emotions_list = g.storage.get_entry_emotions(entry_id)
    input_emotions_list = emotions_string.split()
    # make list sorted alphabetically like current_emotions_list_is
    new_emotions_list = sorted(input_emotions_list)
    return current_emotions_list == new_emotions_list


def get_dict_of_attributes_and_values_to_edit(
    input_attribute_value_dict, entry_id, user_id
):
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
        if str(value) != input_value:
            attributes_with_values_to_edit[attribute] = input_value

    return attributes_with_values_to_edit
