-- seed.sql

-- Create tables
CREATE TABLE users (
    id serial PRIMARY KEY,
    username text UNIQUE NOT NULL CHECK (LENGTH(username) <= 30),
    password_hash text NOT NULL
);

CREATE TABLE entries (
    id serial PRIMARY KEY,
    user_id int NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entry_date DATE NOT NULL DEFAULT CURRENT_DATE,
    energy_level text NOT NULL,
    mood_range text NOT NULL,
    reflection text,
    UNIQUE (user_id, entry_date)
);

CREATE TABLE emotions (
    id serial PRIMARY KEY,
    entry_id int NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
    emotion text NOT NULL,
    UNIQUE (emotion, entry_id)
);

-- Seed user (password: "pw123")
INSERT INTO users (username, password_hash) VALUES
('testuser', '$2b$12$YHbQd8dGN58kvi7uUWQ7K.PDe5sXt/yieuL90ewblcCRiu9hjJLwS'); 

-- Seed 14 entries
INSERT INTO entries (user_id, entry_date, energy_level, mood_range, reflection) VALUES
(1, '2025-02-24', 'Very high energy',  'Very positive', 'Crushed my morning workout and felt unstoppable the rest of the day. Everything just clicked.'),
(1, '2025-02-25', 'High energy',       'Positive',      'Had a really productive work session. Knocked out tasks I had been putting off for days.'),
(1, '2025-02-26', 'Neutral',           'Calm',           NULL),
(1, '2025-02-27', 'High energy',       'Very positive', 'Caught up with an old friend over coffee. Left the conversation feeling recharged and grateful.'),
(1, '2025-02-28', 'Neutral',           'Positive',      'Steady day. Got through my to-do list without much friction and cooked a decent meal at home.'),
(1, '2025-03-01', 'Low energy',        'Negative',      'Work was overwhelming. Too many meetings and not enough time to actually focus on anything meaningful.'),
(1, '2025-03-02', 'Neutral',           'Calm',          'Took it slow today to recover. Went for a short walk outside and tried not to overthink things.'),
(1, '2025-03-03', 'Very high energy',  'Very positive', 'Spent the day with family. Laughed a lot and felt completely present. Exactly what I needed.'),
(1, '2025-03-04', 'Very low energy',   'Negative',      'Woke up feeling off and it never really improved. Hard to concentrate or find motivation for anything.'),
(1, '2025-03-05', 'Low energy',        'Calm',          'Still a bit drained but manageable. Kept things simple and gave myself permission to rest.'),
(1, '2025-03-06', 'High energy',       'Positive',      'Finally submitted a project I had been working on for weeks. Huge weight off my shoulders.'),
(1, '2025-03-07', 'Neutral',           'Very positive', 'Full day off with no obligations. Slept in, made a big breakfast, and just enjoyed the quiet.'),
(1, '2025-03-08', 'Low energy',        'Negative',      'Felt anxious most of the day without a clear reason. Hard to shake the restlessness even at night.'),
(1, '2025-03-09', 'High energy',       'Positive',       NULL);


-- Seed emotions
INSERT INTO emotions (entry_id, emotion) VALUES
(1,  'motivated'), (1,  'happy'),
(2,  'content'),
(3,  'tired'),     (3,  'calm'),
(4,  'energized'), (4,  'proud'),
(6,  'stressed'),  (6,  'overwhelmed'),
(7,  'hopeful'),
(8,  'joyful'),    (8,  'grateful'),
(9,  'fatigued'),  (9,  'sad'),
(10, 'neutral'),
(11, 'accomplished'), (11, 'relieved'),
(12, 'happy'),     (12, 'relaxed'),
(14, 'content'),   (14, 'satisfied');