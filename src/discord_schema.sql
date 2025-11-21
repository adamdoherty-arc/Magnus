-- Discord Messages Schema
-- Stores messages extracted from Discord channels

CREATE TABLE IF NOT EXISTS discord_channels (
    channel_id BIGINT PRIMARY KEY,
    channel_name TEXT,
    server_name TEXT,
    server_id BIGINT,
    description TEXT,
    last_sync TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS discord_messages (
    message_id BIGINT PRIMARY KEY,
    channel_id BIGINT REFERENCES discord_channels(channel_id),
    author_id BIGINT,
    author_name TEXT,
    content TEXT,
    timestamp TIMESTAMP,
    edited_timestamp TIMESTAMP,
    attachments JSONB,
    embeds JSONB,
    reactions JSONB,
    mentions JSONB,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_discord_messages_channel ON discord_messages(channel_id);
CREATE INDEX IF NOT EXISTS idx_discord_messages_timestamp ON discord_messages(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_discord_messages_author ON discord_messages(author_id);
CREATE INDEX IF NOT EXISTS idx_discord_messages_content ON discord_messages USING gin(to_tsvector('english', content));

-- View for recent messages
CREATE OR REPLACE VIEW discord_recent_messages AS
SELECT
    m.message_id,
    m.content,
    m.author_name,
    m.timestamp,
    c.channel_name,
    c.server_name,
    m.reactions,
    m.attachments
FROM discord_messages m
JOIN discord_channels c ON m.channel_id = c.channel_id
ORDER BY m.timestamp DESC
LIMIT 1000;

-- Betting signals extraction
CREATE TABLE IF NOT EXISTS discord_betting_signals (
    signal_id SERIAL PRIMARY KEY,
    message_id BIGINT REFERENCES discord_messages(message_id),
    sport TEXT,
    team TEXT,
    bet_type TEXT,
    odds NUMERIC,
    stake NUMERIC,
    confidence TEXT,
    reasoning TEXT,
    posted_at TIMESTAMP,
    result TEXT,  -- 'pending', 'won', 'lost'
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_signals_sport ON discord_betting_signals(sport);
CREATE INDEX IF NOT EXISTS idx_signals_result ON discord_betting_signals(result);
CREATE INDEX IF NOT EXISTS idx_signals_posted ON discord_betting_signals(posted_at DESC);

COMMENT ON TABLE discord_messages IS 'Stores Discord messages from monitored channels';
COMMENT ON TABLE discord_betting_signals IS 'Parsed betting signals from Discord messages';
