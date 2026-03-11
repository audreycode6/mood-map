# MOOD MAP - PY 189

### A Python/Flask/Jinja application backed by PostgreSQL that allows users to create and manage emotional check-ins over time, creating a personal record of mood range, energy levels, reflections, and emotions.

## Set Up & Installation

### Prequisites (must be installed before proceeding):

- Python 3.12+
- Poetry 2.x
- PostgreSQL 14+

> [!NOTE] versions I used:
>
> - Python: 3.12.0
> - Poetry: 2.1.2
> - Postgresql: 14.19 (Homebrew)
> - Browser: Arc 1.135.0 (Chromium 145.0.7632.110)

### Steps:

> [!NOTE]
>
> Commands should be run on command line at root of project folder

1. **Unzip** the project archive and navigate into the project folder:

   ```bash
   cd mood_map
   ```

2. **Install dependencies** via Poetry:

   The following command installs all project dependencies defined in `pyproject.toml`

   ```bash
   poetry install
   ```

3. **Create the PostgreSQL database:**

   ```bash
   createdb mood_map
   ```

4. **Load the schema and seed data:**

   ```bash
   psql -d mood_map < seed.sql
   ```

5. **Run the application:**

   ```bash
   poetry run python app.py
   ```

6. Open your browser and go to `http://localhost:5003/`

7. **Test credentials:**
   - Username: `testuser` - Password: `pw123`
   - data should match what is in `seed.sql`

## Features

- **CRUD entries and** their associated **emotions**
- **chronological order** view of entries
- **pagination**: view entries 5 at a time in order of most recent to oldest entry
- **input validation with error handling**: alert when missing or invalid data submit for entry and emotion creation/update
- **redirect to protected path after login** if attempting to access protected (login_required) path before authenticated

## Additional Info

### Problem Domain:

- **Many people experience changes in mood and energy throughout the day but do not have a structured way to record or reflect on those changes. Without a record, it can be difficult to notice patterns or understand how emotions relate to daily experiences**.

### Target Audience:

- People interested in self-reflection or emotional awareness who want to track how their mood changes over time.
- People who journal or document daily experiences but prefer a more structured format than traditional journaling.
- Individuals trying to notice patterns in behavior, such as how sleep, work, or social interactions might affect their mood.

### How Mood Map Addresses Problem Domain:

- A personal **journaling tool** where users log daily check-ins to track their emotional and physical state over time.

- Each **Entry** captures:
  - **Date of Entry** — 'yyyy-mm-dd'
  - **Mood Range** — 1 of the following descriptions: [Very positive, Positive, Calm, Negative, Very Negative]
  - **Energy Level** — 1 of the following descriptions: [Very high energy, High energy, Neutral, Low energy, Very low energy]
  - **Reflection** _Optional_ — a free-text note about the day
  - **Emotions** _Optional_ — 0 or more labeled feelings (e.g. "anxious", "grateful")

- Entries are saved and displayed from most recent to oldest, creating a **timeline of records** that users can review/analyze later.

- Users can also **view, update, or delete entries and emotions**, allowing the record to stay accurate and detailed over time.

### Schema:

- 3 tables: `users`, `entries`, and `emotions`
- **`entries` have a 1 to many relationship with `emotions`.**
  - an entry can have 0 to many instances emotions
  - an emotion has 1 and only 1 instance of an entry
    **Key Details**
- `users`:
  - limit on length of username (<=30)
  - stores only hashed pw, not plain text; hashing pw with bcrypt
- `entries` :
  - 1 entry per day constraint: `UNIQUE(entry_date, user_id)`
  - `entries(user_id)` references `users(id)` on delete cascade
  - `entries(reflection)` is optional
- `emotions`:
  - `emotions(entry_id)` references `entries(id)` on delete cascade
  - emotions must have unique emotion and entry_id -- no duplicate emotions in an entry: `UNIQUE(entry_id, emotion)`
  - an entry can have 0 to many emotions
