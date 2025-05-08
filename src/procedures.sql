DELIMITER $$

CREATE PROCEDURE sp_create_instruction (
    IN in_type INT,
    IN in_performer_id INT,
    IN in_file_name VARCHAR(255),
    OUT out_inserted_id INT
)
BEGIN
    IF in_type = 1 THEN
        INSERT INTO instruction_pef (performer_id, file_name)
        VALUES (in_performer_id, in_file_name);
        SET out_inserted_id = LAST_INSERT_ID();
    ELSE
        INSERT INTO instruction_special (performer_id, file_name)
        VALUES (in_performer_id, in_file_name);
        SET out_inserted_id = LAST_INSERT_ID();
    END IF;
END$$

DELIMITER ;
