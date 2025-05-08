DELIMITER $$

CREATE PROCEDURE sp_create_instruction (
    IN in_type INT,
    IN in_performer_id INT,
    IN in_file_name VARCHAR(255),
    IN in_is_fund_item VARCHAR(1),
    IN in_company_detail TEXT,
    IN in_deal_type VARCHAR(255),
    IN in_deal_object VARCHAR(255),
    IN in_bank_name VARCHAR(255),
    IN in_account_number VARCHAR(255),
    IN in_holder_name VARCHAR(255),
    IN in_amount VARCHAR(255),
    IN in_process_date TIMESTAMP,
    IN in_other_specs_text TEXT,
    IN in_other_specs_detail TEXT,
    OUT out_inserted_id INT
)
BEGIN
    DECLARE inserted_pef_id INT;
    DECLARE inserted_result_id INT;
    
    -- Start transaction to ensure data consistency
    START TRANSACTION;
    
    IF in_type = 1 THEN
        -- Insert into instruction_pef
        INSERT INTO instruction_pef (performer_id, file_name)
        VALUES (in_performer_id, in_file_name);
        
        SET inserted_pef_id = LAST_INSERT_ID();
        SET out_inserted_id = inserted_pef_id;
        
        -- Insert into instruction_pef_result
        INSERT INTO instruction_pef_result (instruction_pef_id, is_fund_item, company_detail)
        VALUES (inserted_pef_id, in_is_fund_item, in_company_detail);
        
        SET inserted_result_id = LAST_INSERT_ID();
        
        -- Insert into transaction_history
        IF in_deal_type IS NOT NULL THEN
            INSERT INTO transaction_history (
                instruction_pef_result_id, 
                deal_type, 
                deal_object, 
                bank_name, 
                account_number, 
                holder_name, 
                amount, 
                process_date
            )
            VALUES (
                inserted_result_id,
                in_deal_type,
                in_deal_object,
                in_bank_name,
                in_account_number,
                in_holder_name,
                in_amount,
                in_process_date
            );
        END IF;
        
        -- Insert into other_specifications
        IF in_other_specs_text IS NOT NULL THEN
            INSERT INTO other_specifications (
                instruction_pef_result_id,
                other_specs_text,
                other_specs_detail
            )
            VALUES (
                inserted_result_id,
                in_other_specs_text,
                in_other_specs_detail
            );
        END IF;
    ELSE
        -- The original code for instruction_special
        INSERT INTO instruction_special (performer_id, file_name)
        VALUES (in_performer_id, in_file_name);
        SET out_inserted_id = LAST_INSERT_ID();
    END IF;
    
    -- Commit the transaction
    COMMIT;
    
END$$

DELIMITER ;