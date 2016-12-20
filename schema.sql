CREATE TABLE food_recipe
(
  food_recipe_id INTEGER PRIMARY KEY AUTO_INCREMENT, username varchar(150) , dish_title varchar(50), cooking_time varchar(20), ingredients varchar(500), directions varchar(1000), dish_photo varchar(255)
);

CREATE TABLE friends (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id1 varchar(150),
    user_id2 varchar(150)
);


CREATE TABLE friend_requests (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id1 varchar(150),
    user_id2 varchar(150)
);


CREATE TABLE events(
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  creator_id varchar(150),
  restaurant_id varchar(150),
  date_of_event DATETIME
);


CREATE TABLE event_users(
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  user_id varchar(150),
  event_id varchar(150)
);

