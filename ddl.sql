CREATE TABLE version (
  version SERIAL PRIMARY KEY
);

CREATE TABLE project (
  id SERIAL PRIMARY KEY,
  version INT REFERENCES version(version),
  parent_id INT REFERENCES project(id),
  name TEXT,
  CHECK (version IS NULL or parent_id IS NULL)
);

CREATE TABLE price (
  id SERIAL PRIMARY KEY,
  project_id INT REFERENCES project(id),
  price DOUBLE PRECISION,
  year SMALLINT,
  name TEXT,
  UNIQUE (project_id, name, year)
);