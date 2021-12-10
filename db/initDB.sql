CREATE DATABASE IF NOT EXISTS food;
USE food;

CREATE TABLE users (
  id INT NOT NULL AUTO_INCREMENT,
  username VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL,
  email VARCHAR(100) NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE food_items (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  calories INT NOT NULL,
  protein FLOAT NOT NULL,
  carbs FLOAT NOT NULL,
  fat FLOAT NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE food_log (
  id INT NOT NULL AUTO_INCREMENT,
  food_id INT NOT NULL,
  user_id INT NOT NULL,
  date DATE NOT NULL,
  quantity INT NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (food_id) REFERENCES food_items(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);






