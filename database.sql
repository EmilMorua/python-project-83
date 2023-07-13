CREATE TABLE urls (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  created_at TIMESTAMP
);

CREATE TABLE url_checks (
  id SERIAL PRIMARY KEY,
  url_id INT REFERENCES urls(id),
  status_code INT,
  h1_content VARCHAR(255),
  title_content VARCHAR(255),
  description_content VARCHAR(255),
  created_at TIMESTAMP
);
