CREATE TABLE "users" (
  "id" SERIAL PRIMARY KEY,
  "username" VARCHAR(254) NOT NULL UNIQUE,
  "email" VARCHAR(254) NOT NULL UNIQUE,
  "password" bytea NOT NULL,
  "created" TIMESTAMP NOT NULL
);
CREATE INDEX ON "users" (username, password);

CREATE TABLE "task" (
  "id" SERIAL PRIMARY KEY,
  "text" VARCHAR(510) NOT NULL UNIQUE,
  "created" DATE NOT NULL,
  "user_id" INTEGER NOT NULL REFERENCES "users" ON DELETE CASCADE
);
