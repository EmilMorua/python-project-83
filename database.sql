CREATE TABLE urls (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  created_at TIMESTAMP
);

CREATE TABLE url_checks (
  id SERIAL PRIMARY KEY,
  url_id INT REFERENCES urls(id),
  status_code INT,
  h1 VARCHAR(255),
  title VARCHAR(255),
  description VARCHAR(255),
  created_at TIMESTAMP
);
