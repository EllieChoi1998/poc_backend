CREATE TABLE team (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL
);

CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    login_id VARCHAR(100) UNIQUE NOT NULL,
    ibk_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    password TEXT NOT NULL,
    hiearchy VARCHAR(100) NOT NULL,
    system_role VARCHAR(10) NOT NULL,
    activate VARCHAR(1) DEFAULT 'T',
    team_id INT,
    refresh_token TEXT NULL,
    FOREIGN KEY (team_id) REFERENCES team(id) ON DELETE SET NULL
);

CREATE TABLE termsNconditions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code TEXT,
    query TEXT,

    UNIQUE KEY unique_query (query(255)),
    UNIQUE KEY unique_code (code(255))
);

CREATE TABLE checklist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT,
    UNIQUE KEY unique_question (question(255))
);

CREATE TABLE contract(
    id INT AUTO_INCREMENT PRIMARY KEY,
    contract_name TEXT NOT NULL,
    file_name TEXT NOT NULL,
    embedding_id TEXT DEFAULT NULL,
    uploader_id INT NOT NULL,
    keypoint_processer_id INT DEFAULT NULL,
    checklist_processer_id INT DEFAULT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    keypoint_processed TIMESTAMP DEFAULT NULL,
    checklist_processed TIMESTAMP DEFAULT NULL,
    checklist_printable_file_path TEXT DEFAULT NULL,
    current_state INT DEFAULT 0,

    FOREIGN KEY (uploader_id) REFERENCES user(id) ON DELETE SET NULL,
    FOREIGN KEY (keypoint_processer_id) REFERENCES user(id) ON DELETE SET NULL,
    FOREIGN KEY (checklist_processer_id) REFERENCES user(id) ON DELETE SET NULL,E
);

CREATE TABLE checklist_results(
    id INT AUTO_INCREMENT PRIMARY KEY,
    contract_id INT,
    checklist_id INT,
    memo TEXT DEFAULT NULL,
    FOREIGN KEY (contract_id) REFERENCES contract(id) ON DELETE CASCADE,
    FOREIGN KEY (checklist_id) REFERENCES checklist(id) ON DELETE CASCADE,
);

CREATE TABLE checklist_results_values(
    id INT AUTO_INCREMENT PRIMARY KEY,
    checklist_results_id INT,
    clause_num TEXT,
    located_page INT,
    FOREIGN KEY (checklist_results_id) REFERENCES checklist_results(id) ON DELETE CASCADE,
);

CREATE TABLE keypoint_result(
    id INT AUTO_INCREMENT PRIMARY KEY,
    contract_id INT,
    json_file_path TEXT,
    FOREIGN KEY (contract_id) REFERENCES contract(id) ON DELETE SET NULL
);


INSERT INTO team(name, department) VALUES ('컴플라이언스', '수탁사업부');
INSERT INTO team(name, department) VALUES ('계약팀', '수탁사업부');
INSERT INTO team(name, department) VALUES ('영업팀', '수탁사업부');