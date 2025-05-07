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
    code VARCHAR(255),
    query VARCHAR(255),
    UNIQUE KEY unique_query (query),
    UNIQUE KEY unique_code (code)
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
    uploader_id INT,
    keypoint_processer_id INT DEFAULT NULL,
    checklist_processer_id INT DEFAULT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    keypoint_processed TIMESTAMP DEFAULT NULL,
    checklist_processed TIMESTAMP DEFAULT NULL,
    checklist_printable_file_path TEXT DEFAULT NULL,
    current_state INT DEFAULT 0,

    FOREIGN KEY (uploader_id) REFERENCES user(id) ON DELETE SET NULL,
    FOREIGN KEY (keypoint_processer_id) REFERENCES user(id) ON DELETE SET NULL,
    FOREIGN KEY (checklist_processer_id) REFERENCES user(id) ON DELETE SET NULL
);

CREATE TABLE checklist_result(
    id INT AUTO_INCREMENT PRIMARY KEY,
    contract_id INT,
    checklist_id INT,
    memo TEXT DEFAULT NULL,
    FOREIGN KEY (contract_id) REFERENCES contract(id) ON DELETE CASCADE,
    FOREIGN KEY (checklist_id) REFERENCES checklist(id) ON DELETE CASCADE,
    UNIQUE KEY unique_contract_checklist (contract_id, checklist_id)
);

CREATE TABLE checklist_result_value(
    id INT AUTO_INCREMENT PRIMARY KEY,
    checklist_result_id INT,
    clause_num TEXT,
    located_page INT,
    FOREIGN KEY (checklist_result_id) REFERENCES checklist_result(id) ON DELETE CASCADE
);

CREATE TABLE keypoint_result(
    id INT AUTO_INCREMENT PRIMARY KEY,
    contract_id INT,
    termsNconditions_id INT,
    match_rate FLOAT,
    FOREIGN KEY (contract_id) REFERENCES contract(id) ON DELETE SET NULL,
    FOREIGN KEY (termsNconditions_id) REFERENCES termsNconditions(id) ON DELETE CASCADE,
    UNIQUE KEY unique_contract_terms (contract_id, termsNconditions_id)
);

INSERT INTO team(name, department) VALUES ('컴플라이언스', '수탁사업부');
INSERT INTO team(name, department) VALUES ('계약팀', '수탁사업부');
INSERT INTO team(name, department) VALUES ('영업팀', '수탁사업부');

INSERT INTO checklist(question) VALUES ('집합투자업자와 기본계약은 체결되어 있는가');
INSERT INTO checklist(question) VALUES ('집합투자업자 및 신탁업자의 상호가 적정하게 기재되어 있는가');
INSERT INTO checklist(question) VALUES ('집합투자업자의 업무와 신탁업자의 업무가 적정하게 기재되어 있는가');
INSERT INTO checklist(question) VALUES ('집합투자기구의 종류와 추가신탁 허용 여부, 환매금지여부 등이 적정하게 매칭되어 있는가');
INSERT INTO checklist(question) VALUES ('신탁계약기간의 효력발생시기와 신탁계약기간이 적정하게 기재되어 있는가');
INSERT INTO checklist(question) VALUES ('신탁원본의 가액 및 수익증권의 총좌수에 관한 사항이 기재되어 있는가');
INSERT INTO checklist(question) VALUES ('집합투자업자와 신탁업자의 투자대상자산의 취득/처분 등에 대하여 신탁 재산 한도 내에서 이행책임을 부담한다는 문구가 기재되어 있는가');
INSERT INTO checklist(question) VALUES ('투자신탁재산의 투자대상자산, 운용 및 투자제한 사항, 한도 및 제한의 예외사항이 기재되어 있는가');
INSERT INTO checklist(question) VALUES ('투자목적과 투자전략에 타당한 투자대상 가능자산이 기재되어 있는가');
INSERT INTO checklist(question) VALUES ('투자목적 및 투자전략, 투자대상자산 및 취득한도 등의 상충이 발생하지 않는가');
INSERT INTO checklist(question) VALUES ('레버리지 비율이 적격투자자의 조건에 부합하게 기재되어 있는가');
INSERT INTO checklist(question) VALUES ('신탁업자의 투자신탁재산 보관 및 관리사항이 기재되어 있는가');
INSERT INTO checklist(question) VALUES ('운용행위의 감시 의무 등에 대한 사항이 공사모펀드 유형에 맞게 기재되어 있는가');
INSERT INTO checklist(question) VALUES ('이익분배 및 환매에 관한 사항이 적정하게 기재되어 있는가');
INSERT INTO checklist(question) VALUES ('집합투자재산 평가와 관련하여 집합투자재산평가 위원회의 구성/운영을 포함한 집합투자재산평가기준 및 평가명세 제출을 명시하고 있는가');
INSERT INTO checklist(question) VALUES ('기준가격의 산정 및 제시에 관한 사항이 적정하게 기재되어 있는가');
INSERT INTO checklist(question) VALUES ('집합투자, 신탁업자, 판매회사 등이 받는 보수와 그 외 수수료의 계산 방법 및 지급시기, 방법에 관한 사항이 기재되어 있는가(다만, 집합투자업자가 기준가격 산정업무를 위탁하는 경우에는 향후 발생될 수수료를 해당 집합투자재산에서 부담한다는 내용을 포함하여야 한다)');
INSERT INTO checklist(question) VALUES ('투자설명자료(투자설명서, 핵심투자설명서, 펀드IM)와 법령 및 신탁계약서 상의 주된 투자자산 등 주요내용은 일치하는가(투자설명서의 법령 및 집합투자규약 부합여부)');
INSERT INTO checklist(question) VALUES ('수익자 총회 및 공시(보고서)에 관한 사항이 적정하게 기재되어 있는가');
INSERT INTO checklist(question) VALUES ('손해배상 관련 규정은 적절하게 기재되어 있는가');
INSERT INTO checklist(question) VALUES ('분쟁 발생시 재판관할규정은 기재되어 있는가');
INSERT INTO checklist(question) VALUES ('그 밖에 수익자 및 신탁업자의 이익에 반하는 내용이 기재되어 있지 않은 가');
INSERT INTO checklist(question) VALUES ('장외파생상품 매매에 따른 위험평가액이 자산총액의 100분의 10을 초과하는 펀드인 경우, 집합투자업자의 장외파생상품 위험관리방법을 확인하였는가');
INSERT INTO checklist(question) VALUES ('ESG 관련 펀드 여부');
INSERT INTO checklist(question) VALUES ('본 계약과 관련하여 수탁재산 보관/관리 업무 세칙 제 48조(수탁계약의사결정 참여금지) 이해상충행위 방지조항을 점검하였는가?');