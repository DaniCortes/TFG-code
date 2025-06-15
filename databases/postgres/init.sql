CREATE TABLE users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  biography TEXT,
  followers_count INTEGER DEFAULT 0 NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
  last_login_date TIMESTAMP WITH TIME ZONE,
  account_status TEXT DEFAULT 'active' NOT NULL,
  stream_status TEXT DEFAULT 'offline' NOT NULL,
  profile_picture TEXT DEFAULT 'default_profile_picture.jpg',
  stream_key TEXT UNIQUE NOT NULL,
  is_admin BOOLEAN DEFAULT FALSE
);
-- Create admin user
INSERT INTO users (
    username,
    password,
    biography,
    account_status,
    stream_key,
    is_admin
  )
VALUES (
    'admin',
    '$2a$12$Ph3Xr.xnecI2Jbpr9jAIfO0ahrMbtN8yzHsz8MSNrcy59DrUPAY3a',
    'Admin user',
    'active',
    'admin_replace_this_key',
    TRUE
  );