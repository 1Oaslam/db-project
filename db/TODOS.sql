CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(250) NOT NULL UNIQUE,
    password VARCHAR(250) NOT NULL
);

CREATE TABLE todos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    content VARCHAR(100),
    due DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE spieler (
    spieler_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    geburtsdatum DATE,
    position VARCHAR(50)
);

CREATE TABLE spiel (
    spiel_id INT AUTO_INCREMENT PRIMARY KEY,
    datum DATE NOT NULL,
    gegner VARCHAR(100),
    tore_team INT DEFAULT 0,
    tore_gegner INT DEFAULT 0
);

CREATE TABLE training (
    training_id INT AUTO_INCREMENT PRIMARY KEY,
    datum DATE NOT NULL
);

CREATE TABLE ereignis (
    ereignis_id INT AUTO_INCREMENT PRIMARY KEY,
    typ VARCHAR(20) NOT NULL,
    spiel_id INT NOT NULL,
    spieler_id INT NOT NULL,
    FOREIGN KEY (spiel_id) REFERENCES spiel(spiel_id),
    FOREIGN KEY (spieler_id) REFERENCES spieler(spieler_id)
);

CREATE TABLE spieler_spiel (
    spieler_id INT NOT NULL,
    spiel_id INT NOT NULL,
    PRIMARY KEY (spieler_id, spiel_id),
    FOREIGN KEY (spieler_id) REFERENCES spieler(spieler_id),
    FOREIGN KEY (spiel_id) REFERENCES spiel(spiel_id)
);

CREATE TABLE spieler_training (
    spieler_id INT NOT NULL,
    training_id INT NOT NULL,
    PRIMARY KEY (spieler_id, training_id),
    FOREIGN KEY (spieler_id) REFERENCES spieler(spieler_id),
    FOREIGN KEY (training_id) REFERENCES training(training_id)
);

    
INSERT INTO spieler (name, geburtsdatum, position) VALUES
('Lionel Messi', '1987-06-24', 'Stürmer'),
('Luka Modric', '1985-09-09', 'Mittelfeld'),
('Manuel Neuer', '1986-03-27', 'Torwart');



INSERT INTO spiel (datum, gegner, tore_team, tore_gegner) VALUES
('2025-03-01', 'FC Basel', 3, 1),
('2025-03-08', 'FC Zürich', 2, 2);


INSERT INTO training (datum) VALUES
('2025-02-20'),
('2025-02-27');


INSERT INTO ereignis (typ, spiel_id, spieler_id) VALUES
('Tor', 1, 1),
('Assist', 1, 2),
('Gelbe Karte', 2, 3);


INSERT INTO spieler_spiel (spieler_id, spiel_id) VALUES
(1, 1),
(2, 1),
(3, 1),
(1, 2),
(2, 2);


INSERT INTO spieler_training (spieler_id, training_id) VALUES
(1, 1),
(2, 1),
(3, 2);



    

