
CREATE TABLE IF NOT EXISTS members (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name  TEXT NOT NULL,
    email      TEXT UNIQUE NOT NULL,
    phone      TEXT,
    join_date  DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS plans (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    price           REAL NOT NULL CHECK (price > 0),
    duration_months INTEGER NOT NULL,
    duration_days   INTEGER,
    description     TEXT
);

CREATE TABLE IF NOT EXISTS memberships (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id  INTEGER NOT NULL,
    plan_id    INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date   DATE NOT NULL,
    status     TEXT DEFAULT 'active' CHECK (status IN ('active','expired','canceled','suspended','pending payment')),
    FOREIGN KEY (member_id) REFERENCES members(id),
    FOREIGN KEY (plan_id)   REFERENCES plans(id)
);

CREATE TABLE IF NOT EXISTS payments (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id     INTEGER,
    membership_id INTEGER NOT NULL,
    amount        REAL NOT NULL CHECK (amount > 0),
    payment_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date      DATE,
    status        TEXT DEFAULT 'pending' CHECK (status IN ('pending','completed','failed')),
    FOREIGN KEY (member_id)     REFERENCES members(id),
    FOREIGN KEY (membership_id) REFERENCES memberships(id)
);

CREATE TABLE IF NOT EXISTS access_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id   INTEGER NOT NULL,
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted     BOOLEAN NOT NULL,
    message     TEXT,
    FOREIGN KEY (member_id) REFERENCES members(id)
);

-- ── VIEWs ──────────────────────────────────────────────────────────────

-- Active members with CASE-based status classification
CREATE VIEW IF NOT EXISTS active_members_view AS
SELECT
    m.id,
    m.first_name || ' ' || m.last_name AS full_name,
    m.email,
    m.phone,
    ms.status AS membership_status,
    ms.start_date,
    ms.end_date,
    p.name  AS plan_name,
    p.price AS plan_price,
    CASE
        WHEN ms.end_date >= date('now') AND ms.status = 'active'           THEN 'Access Allowed'
        WHEN ms.status = 'suspended'                                        THEN 'Suspended'
        WHEN ms.status = 'pending payment'                                  THEN 'Payment Required'
        WHEN ms.end_date < date('now')  OR ms.status = 'expired'           THEN 'Expired'
        ELSE 'Access Denied'
    END AS access_status,
    CASE
        WHEN ms.end_date >= date('now') AND ms.status = 'active'           THEN 'active'
        WHEN ms.status IN ('suspended','pending payment')                   THEN ms.status
        ELSE 'expired'
    END AS computed_status
FROM members m
LEFT JOIN memberships ms ON m.id = ms.member_id
LEFT JOIN plans p        ON ms.plan_id = p.id;

-- Monthly payment totals
CREATE VIEW IF NOT EXISTS monthly_payments_summary AS
SELECT
    strftime('%Y-%m', payment_date)                                    AS month,
    COUNT(*)                                                           AS total_transactions,
    COALESCE(SUM(amount), 0)                                          AS total_amount,
    COALESCE(SUM(CASE WHEN status='completed' THEN amount ELSE 0 END),0) AS collected,
    SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END)                 AS pending_count
FROM payments
GROUP BY month
ORDER BY month DESC;

-- Denied access summary per member
CREATE VIEW IF NOT EXISTS denied_access_summary AS
SELECT
    m.first_name || ' ' || m.last_name AS full_name,
    COUNT(*)                           AS denied_count,
    MAX(al.access_time)                AS last_denied
FROM access_logs al
JOIN members m ON al.member_id = m.id
WHERE al.granted = 0
GROUP BY al.member_id
ORDER BY denied_count DESC;
