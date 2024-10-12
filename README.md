```tsql
DROP FUNCTION IF EXISTS get_group_schedule_for_current_month;
CREATE OR ALTER FUNCTION get_group_schedule_for_current_month (@group_id BIGINT) RETURNS @ret TABLE (
    schedule_item_id BIGINT NOT NULL,
    teacher_id BIGINT NOT NULL,
    teacher_first_name VARCHAR(256) NOT NULL,
    teacher_last_name VARCHAR(256) NOT NULL,
    subject_id BIGINT NOT NULL,
    subject_name VARCHAR(128) NOT NULL,
    subject_short_name VARCHAR(64) NOT NULL,
    [date] DATE NOT NULL,
    [position] TINYINT NOT NULL,
    [type] VARCHAR(32) NOT NULL
) AS 
BEGIN 
    DECLARE @current_date DATETIME;
    SET @current_date = GETDATE();

    INSERT INTO @ret(schedule_item_id, teacher_id, teacher_first_name, teacher_last_name, subject_id, subject_name, subject_short_name, [date], [position], [type])
    SELECT si.id, si.teacher_id, t.first_name, t.last_name, si.subject_id, sj.name, sj.short_name, si.[date], si.[position], si.[type]
    FROM schedule_item si
    INNER JOIN teacher t ON t.id = si.teacher_id
    INNER JOIN subject sj ON sj.id = si.subject_id
    WHERE si.group_id = @group_id AND [date] >= DATEFROMPARTS(YEAR(@current_date), MONTH(@current_date), 1) AND [date] <= EOMONTH(@current_date) ORDER BY [date];

    RETURN;
END
```