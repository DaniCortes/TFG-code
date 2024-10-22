db = db.getSiblingDB("stream_db");

db.createCollection("streams");

db.createCollection("follows");

db.createCollection("messages");

db.createCollection("mutes");

db.createCollection("bans");

db.createCollection("reports");

db.createUser({
  user: "myuser",
  pwd: "mypassword",
  roles: [{ role: "readWrite", db: "stream_database" }],
});

print("Database initialization completed.");
