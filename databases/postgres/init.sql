-- Create the database
CREATE DATABASE stream_users;
-- Connect to the database
\ c stream_users;
-- Create a user for the application
CREATE USER myuser WITH ENCRYPTED PASSWORD 'mypassword';
-- Grant privileges to the user
GRANT ALL PRIVILEGES ON DATABASE stream_users TO myuser;
-- Create the users table
CREATE TABLE users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  biography TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  last_login_date TIMESTAMP WITH TIME ZONE,
  account_status VARCHAR(255) DEFAULT 'active',
  profile_picture TEXT DEFAULT 'default_profile_picture.jpg',
  stream_key VARCHAR(255) UNIQUE
);
-- Create admin user
INSERT INTO users (
    username,
    password,
    biography,
    account_status,
    stream_key
  )
VALUES (
    'admin',
    'admin',
    'Admin user',
    'active',
    'admin'
  );