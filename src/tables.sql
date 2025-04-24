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
    question TEXT NOT NULL
);

CREATE TABLE document (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_name VARCHAR(100) NOT NULL,
    file_name VARCHAR(300) NOT NULL,
    embedding_id VARCHAR(100),
    doc_type VARCHAR(50) NOT NULL,
    user_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    current_state INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE SET NULL
);

CREATE TABLE serviceResult (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT,
    service_name VARCHAR(100) NOT NULL,
    JSONFile_path VARCHAR(100),
    result_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    table_html_path VARCHAR(200),
    FOREIGN KEY (document_id) REFERENCES document(id) ON DELETE CASCADE
);


INSERT INTO team(name, department) VALUES ('컴플라이언스', '수탁사업부');
INSERT INTO team(name, department) VALUES ('계약팀', '수탁사업부');
INSERT INTO team(name, department) VALUES ('영업팀', '수탁사업부');