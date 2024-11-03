const collections = [
  "streams",
  "follows",
  "messages",
  "mutes",
  "bans",
  "reports",
];

collections.forEach((collection) => {
  if (!db.getCollectionNames().includes(collection)) {
    db.createCollection(collection);
    print(`Created collection: ${collection}`);
  }
});

print("Database initialization completed successfully.");
