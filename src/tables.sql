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

CREATE TABLE checklist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT,
    UNIQUE KEY unique_question (question(255))
);

CREATE TABLE contract(
    id INT AUTO_INCREMENT PRIMARY KEY,
    contract_name TEXT NOT NULL,
    file_name TEXT NOT NULL,
    embedding_id TEXT,
    uploader VARCHAR(50) NOT NULL,
    keypoint_processer VARCHAR(50),
    checklist_processer VARCHAR(50),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    keypoint_processed TIMESTAMP,
    checklist_processed TIMESTAMP,
    current_state INT DEFAULT 0
);

CREATE TABLE checklist_result(
    id INT AUTO_INCREMENT PRIMARY KEY,
    contract_id INT,
    json_file_path TEXT,
    printable_file_path TEXT,
    FOREIGN KEY (contract_id) REFERENCES contract(id) ON DELETE SET NULL
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