CREATE TABLE team (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL
);

CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    contact VARCHAR(100) NOT NULL,
    team_id INT,
    refresh_token TEXT NULL,
    FOREIGN KEY (team_id) REFERENCES team(id) ON DELETE SET NULL
);

CREATE TABLE document (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(300) NOT NULL,
    embedding_id VARCHAR(100),
    doc_type VARCHAR(50) NOT NULL,
    user_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE SET NULL
);

CREATE TABLE serviceResult (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT,
    service_name VARCHAR(100) NOT NULL,
    JSONFile_path VARCHAR(100),
    result_text TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES document(id) ON DELETE CASCADE
);


INSERT INTO team(name, department) VALUES ('계약팀', '수탁사업부');