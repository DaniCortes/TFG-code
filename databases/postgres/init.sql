CREATE TABLE users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username VARCHAR(255) UNIQUE NOT NULL,
  password TEXT NOT NULL,
  biography TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
  last_login_date TIMESTAMP WITH TIME ZONE,
  account_status VARCHAR(255) DEFAULT 'active' NOT NULL,
  profile_picture TEXT DEFAULT 'default_profile_picture.jpg',
  stream_key VARCHAR(255) UNIQUE NOT NULL,
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