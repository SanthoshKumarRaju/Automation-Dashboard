
-- 1) Table to store the AuditFunctionalities
CREATE TABLE auditfunctionalities (
    functionalityid INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    functionalityname VARCHAR(250) NOT NULL UNIQUE
);

-- drop table auditfunctionalities;

INSERT INTO auditfunctionalities (functionalityname)
VALUES 
('Authenticate'),
('Price Management');
-- Select * from auditfunctionalities;

-- --------------------------------------------------------

-- 2) Table to store AuditEventTypes
CREATE TABLE auditeventtypes (
    eventtypeid INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    functionalityid INT NOT NULL REFERENCES auditfunctionalities(functionalityid),
    eventtypename VARCHAR(250) NOT NULL,
    CONSTRAINT uq_functionality_event UNIQUE (functionalityid, eventtypename)
);

-- drop table auditeventtypes;

INSERT INTO auditeventtypes (functionalityid, eventtypename)
VALUES
(1, 'Login'),
(1, 'Logout'),
(1, 'Sign up'),
(1, 'Reset Password'),
(2, 'Item updated'),
(2, 'Item updates picked up by publisher'),
(2, 'Item updates pushed to rabbit MQ'),
(2, 'Item updates acknowledgement received');
-- Select * from auditeventtypes;

-- --------------------------------------------------------

-- 3) Main table to store the AuditEvents
CREATE TABLE auditevents (
    Id BIGINT GENERATED ALWAYS AS IDENTITY,
    EventTimestamp TIMESTAMP NOT NULL,
    FunctionalityId INT NOT NULL REFERENCES auditfunctionalities(functionalityid),
    EventTypeId INT NOT NULL REFERENCES auditeventtypes(eventtypeid),
    StoreLocationID BIGINT NULL,
    CompanyId BIGINT NOT NULL,
    UserName VARCHAR(20) NOT NULL,
    Message TEXT NOT NULL,
    Status VARCHAR(20) NOT NULL,
    AdditionalData JSONB NULL,
    CONSTRAINT chk_auditevents_status CHECK (Status IN ('Success', 'Failed')),
    CONSTRAINT pk_auditevents PRIMARY KEY (Id, EventTimestamp)  -- include partition key
)
PARTITION BY RANGE (EventTimestamp);

-- Indexes
CREATE INDEX idx_auditevents_timestamp ON auditevents(EventTimestamp DESC);
CREATE INDEX idx_auditevents_functionalityid ON auditevents(FunctionalityId);
CREATE INDEX idx_auditevents_storelocationid ON auditevents(StoreLocationID);
CREATE INDEX idx_auditevents_user ON auditevents(UserName);
CREATE INDEX idx_auditevents_companyid ON auditevents(CompanyId);
CREATE INDEX idx_auditevents_eventtypeid ON auditevents(EventTypeId);

-- drop table auditevents;
-- select * from auditevents;
-- ------------------------------------------------------------------------


-- 4) Function to ensure partitions exist
CREATE OR REPLACE FUNCTION ensure_auditevents_partitions()
RETURNS void LANGUAGE plpgsql AS
$$
DECLARE
    i INT;                              
    start_month DATE;                   
    partition_start DATE;               
    partition_end DATE;                 
    partition_name TEXT;                
    partition_exists BOOLEAN;           
BEGIN
    start_month := date_trunc('month', CURRENT_DATE)::DATE;

    FOR i IN 0..5 LOOP
        partition_start := (start_month + (i * INTERVAL '1 month'))::DATE; 
        partition_end   := (partition_start + INTERVAL '1 month')::DATE;   
        partition_name  := format('auditevents_%s', to_char(partition_start, 'YYYYMM'));

        SELECT EXISTS (
            SELECT 1
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relkind = 'r'       
              AND c.relname = partition_name
        ) INTO partition_exists;

        IF NOT partition_exists THEN
            RAISE NOTICE 'Creating partition: % (from % to %)', partition_name, partition_start, partition_end;

            EXECUTE format(
                'CREATE TABLE %I PARTITION OF AuditEvents
                 FOR VALUES FROM (%L) TO (%L);',
                partition_name, partition_start, partition_end
            );

            EXECUTE format('CREATE INDEX ON %I (EventTimestamp DESC);', partition_name);
            EXECUTE format('CREATE INDEX ON %I (FunctionalityId);', partition_name); -- fixed
            EXECUTE format('CREATE INDEX ON %I (StoreLocationID);', partition_name);
            EXECUTE format('CREATE INDEX ON %I (UserName);', partition_name);
            EXECUTE format('CREATE INDEX ON %I (CompanyId);', partition_name);
        ELSE
            RAISE NOTICE 'Partition already exists: %', partition_name;
        END IF;
    END LOOP;
END;
$$;

-- need to run this function once to create the current and future partitions: 
-- select * from ensure_auditevents_partitions();


/*
INSERT INTO auditevents (EventTimestamp, FunctionalityID, EventTypeID, StoreLocationID, CompanyId, UserName, Message, Status, AdditionalData) 
VALUES 
('2025-09-01 10:15:00', 1, 1, 101, 1, 'jdoe', 'User logged in successfully', 'Success', '{"ip":"192.168.1.10"}'),
('2025-09-01 10:20:00', 2, 1, 101, 1, 'asmith', 'Invalid password attempt', 'Failed', '{"ip":"192.168.1.11"}'),
('2025-09-02 09:05:00', 1, 2, 102, 1, 'mjones', 'New item added to inventory', 'Success', '{"itemId":12345}'),
('2025-09-02 09:30:00', 2, 2, 102, 1, 'mjones', 'Item updated successfully', 'Success', '{"itemId":12345}'),
('2025-09-02 09:40:00', 1, 2, 102, 1, 'mjones', 'Item deletion failed', 'Failed', '{"itemId":54321}'),
('2025-09-03 14:00:00', 2, 3, 103, 2, 'akhan', 'Invoice generated', 'Success', '{"invoiceId":9001}'),
('2025-09-03 14:10:00', 1, 3, 103, 2, 'akhan', 'Invoice creation failed', 'Failed', '{"invoiceId":9002}'),
('2025-09-04 11:25:00', 2, 4, 104, 2, 'rpatel', 'Sale transaction processed', 'Success', '{"transactionId":45001}'),
('2025-09-04 11:30:00', 1, 4, 104, 2, 'rpatel', 'Card declined', 'Failed', '{"transactionId":45002}'),
('2025-09-05 16:45:00', 2, 1, 105, 3, 'jdoe', 'User logged out', 'Success', '{"ip":"192.168.1.10"}'),
('2025-09-06 08:00:00', 1, 4, 106, 3, 'asmith', 'Report generated successfully', 'Success', '{"reportId":"sales-2025"}'),
('2025-09-06 08:15:00', 2, 4, 106, 3, 'asmith', 'Report generation failed', 'Failed', '{"reportId":"stock-2025"}'),
('2025-09-07 12:05:00', 1, 1, 107, 4, 'admin', 'New user created', 'Success', '{"newUser":"twhite"}'),
('2025-09-07 12:20:00', 2, 1, 107, 4, 'admin', 'User creation failed', 'Failed', '{"newUser":"gblack"}'),
('2025-09-08 13:50:00', 1, 2, 108, 4, 'system', 'Token validation passed', 'Success', '{"token":"abc123"}'),
('2025-09-08 13:55:00', 2, 2, 108, 4, 'system', 'Token expired', 'Failed', '{"token":"xyz789"}'),
('2025-09-09 15:10:00', 1, 3, 109, 5, 'syncsvc', 'POS sync completed', 'Success', '{"records":150}'),
('2025-09-09 15:15:00', 2, 3, 109, 5, 'syncsvc', 'POS sync failed', 'Failed', '{"records":0}'),
('2025-09-10 17:40:00', 1, 4, 110, 5, 'mailer', 'Email sent successfully', 'Success', '{"to":"customer@example.com"}'),
('2025-09-10 17:50:00', 2, 4, 110, 5, 'mailer', 'Email delivery failed', 'Failed', '{"to":"customer2@example.com"}');

*/
-- Select * from AuditEvents;


-- -----------------------------------------------------------------------


--5) Procedure to insert the data into the AuditEvents Table
-- since we are using model to insert the data into the table, we don't need this procedure
/*DROP PROCEDURE IF EXISTS InsertAuditEvent;

CREATE OR REPLACE PROCEDURE InsertAuditEvent(
    IN p_EventTimestamp TIMESTAMP,
    IN p_FunctionalityId INT,
    IN p_EventTypeId INT,
    IN p_StoreLocationID BIGINT,
    IN p_CompanyId BIGINT,
    IN p_UserName VARCHAR(20),
    IN p_Message TEXT,
    IN p_Status VARCHAR(20),
    IN p_AdditionalData JSONB DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO AuditEvents (
        EventTimestamp,
        FunctionalityId,
        EventTypeId,
        StoreLocationID,
        CompanyId,
        UserName,
        Message,
        Status,
        AdditionalData
    )
    VALUES (
        p_EventTimestamp,
        p_FunctionalityId,
        p_EventTypeId,
        p_StoreLocationID,
        p_CompanyId,
        p_UserName,
        p_Message,
        p_Status,
        p_AdditionalData
    );
END;
$$;*/

/*
CALL InsertAuditEvent(
    NOW(),                -- EventTimestamp
    1,                    -- FunctionalityId
    2,                    -- EventTypeId
    101,                  -- StoreLocationID
    5001,                 -- CompanyId
    'jdoe',               -- UserName
    'User logged in',     -- Message
    'Success',            -- Status
    '{"ip":"192.168.1.10"}'::jsonb  -- AdditionalData
);

*/

-- -----------------------------------------------------------------------

--6) Procedure to display the data in the landing page which contains top recent 500 records
CREATE OR REPLACE FUNCTION GetLatestAuditEvents()
RETURNS TABLE (
    Id BIGINT,
    EventTimestamp TIMESTAMP,
    Functionality VARCHAR(100),
    EventType VARCHAR(250),
    StoreLocationID BIGINT,
    CompanyId BIGINT,
    UserName VARCHAR(20),
    Message TEXT,
    Status VARCHAR(20),
    AdditionalData JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        ae.Id,
        ae.EventTimestamp,
        af.functionalityname AS Functionality,
        aet.eventtypename AS EventType,   -- fixed here
        ae.StoreLocationID,
        ae.CompanyId,
        ae.UserName,
        ae.Message,
        ae.Status,
        ae.AdditionalData
    FROM AuditEvents ae
    INNER JOIN auditfunctionalities af ON ae.FunctionalityId = af.FunctionalityId
    INNER JOIN auditeventtypes aet ON ae.EventTypeId = aet.EventTypeId
    ORDER BY ae.EventTimestamp DESC
    LIMIT 500;
END;
$$;
-- SELECT * FROM GetLatestAuditEvents();
-- drop FUNCTION GetLatestAuditEvents();


-- -----------------------------------------------------------------------


--7) Procedure to display the data based on parameters which contains top recent 5000 records 
DROP FUNCTION IF EXISTS GetAuditEvents_Func;

/*
CREATE OR REPLACE FUNCTION GetAuditEvents_Func(
    p_FromDate TIMESTAMP,
    p_ToDate TIMESTAMP,
    p_Functionality VARCHAR(100) DEFAULT NULL,
    p_StoreLocationID BIGINT DEFAULT NULL,
    p_User VARCHAR(20) DEFAULT NULL,
    p_Message TEXT DEFAULT NULL,
    p_CompanyId BIGINT DEFAULT NULL
)
RETURNS TABLE (
    Id BIGINT,
    EventTimestamp TIMESTAMP,
    Functionality VARCHAR(100),
    EventType VARCHAR(250),
    StoreLocationID BIGINT,
    CompanyId BIGINT,
    UserName VARCHAR(20),
    Message TEXT,
    Status VARCHAR(20),
    AdditionalData JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ae.Id,
        ae.EventTimestamp,
        af.functionalityname AS Functionality,
        aet.eventtypename   AS EventType,
        ae.StoreLocationID,
        ae.CompanyId,
        ae.UserName,
        ae.Message,
        ae.Status,
        ae.AdditionalData
    FROM AuditEvents ae
    INNER JOIN auditfunctionalities af ON ae.FunctionalityId = af.FunctionalityId
    INNER JOIN auditeventtypes aet ON ae.EventTypeId = aet.EventTypeId
    WHERE ae.EventTimestamp BETWEEN p_FromDate AND p_ToDate
      AND (p_Functionality IS NULL OR af.functionalityname = p_Functionality)
      AND (p_StoreLocationID IS NULL OR ae.StoreLocationID = p_StoreLocationID)
      AND (p_User IS NULL OR ae.UserName = p_User)
      AND (p_Message IS NULL OR ae.Message ILIKE '%' || p_Message || '%')
      AND (p_CompanyId IS NULL OR ae.CompanyId = p_CompanyId)
    ORDER BY ae.EventTimestamp DESC
    LIMIT 5001;
END;
$$
*/;

CREATE OR REPLACE FUNCTION GetAuditEvents_Func(
    p_FromDate TEXT DEFAULT NULL,
    p_ToDate TEXT DEFAULT NULL,
    p_Functionality VARCHAR(100) DEFAULT NULL,
    p_EventType VARCHAR(250) DEFAULT NULL,
    p_StoreLocationID BIGINT DEFAULT NULL,
    p_User VARCHAR(20) DEFAULT NULL,
    p_Message TEXT DEFAULT NULL,
    p_CompanyId BIGINT DEFAULT NULL
)
RETURNS TABLE (
    Id BIGINT,
    EventTimestamp TIMESTAMP,
    Functionality VARCHAR(100),
    EventType VARCHAR(250),
    StoreLocationID BIGINT,
    CompanyId BIGINT,
    UserName VARCHAR(20),
    Message TEXT,
    Status VARCHAR(20),
    AdditionalData JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_FromDate TIMESTAMP;
    v_ToDate   TIMESTAMP;
BEGIN
    -- Convert text dates to timestamp if provided
    IF p_FromDate IS NOT NULL THEN
        BEGIN
            v_FromDate := to_timestamp(p_FromDate, 'MM-DD-YYYY HH24:MI:SS');
        EXCEPTION WHEN others THEN
            v_FromDate := NULL;
        END;
    END IF;

    IF p_ToDate IS NOT NULL THEN
        BEGIN
            v_ToDate := to_timestamp(p_ToDate, 'MM-DD-YYYY HH24:MI:SS');
        EXCEPTION WHEN others THEN
            v_ToDate := NULL;
        END;
    END IF;

    RETURN QUERY
    SELECT 
        ae.Id,
        ae.EventTimestamp,
        af.functionalityname AS Functionality,
        aet.eventtypename AS EventType,
        ae.StoreLocationID,
        ae.CompanyId,
        ae.UserName,
        ae.Message,
        ae.Status,
        ae.AdditionalData
    FROM AuditEvents ae
    INNER JOIN auditfunctionalities af ON ae.FunctionalityId = af.FunctionalityId
    INNER JOIN auditeventtypes aet ON ae.EventTypeId = aet.EventTypeId
    WHERE 
        -- Apply date range dynamically depending on what's provided
        (v_FromDate IS NULL OR ae.EventTimestamp >= v_FromDate)
        AND (v_ToDate IS NULL OR ae.EventTimestamp <= v_ToDate)

        -- Apply filters combinationally (AND logic)
        AND (p_Functionality IS NULL OR af.functionalityname = p_Functionality)
        AND (p_EventType IS NULL OR aet.eventtypename = p_EventType)
        AND (p_StoreLocationID IS NULL OR ae.StoreLocationID = p_StoreLocationID)
        AND (p_User IS NULL OR ae.UserName = p_User)
        AND (p_Message IS NULL OR ae.Message ILIKE '%' || p_Message || '%')
        AND (p_CompanyId IS NULL OR ae.CompanyId = p_CompanyId)

    ORDER BY ae.EventTimestamp DESC
    LIMIT 5001;
END;
$$;


/*
-- With Mandatory Feilds
SELECT * FROM GetAuditEvents_Func('2025-08-31 23:45:00', '2025-09-05 21:45:00');

-- With Optional Feilds
SELECT * 
FROM GetAuditEvents_Func(
    '2025-08-31 23:45:00',
    '2025-09-05 21:45:00'                   
);
*/

-- -----------------------------------------------------------------------


--8) Table to store the data which is older the 12 months from main table AuditEvents
DROP TABLE IF EXISTS AuditEvents_Archival;

CREATE TABLE AuditEvents_Archival (
    Id BIGINT PRIMARY KEY,
    EventTimestamp TIMESTAMP NOT NULL,
    FunctionalityId INT NOT NULL,   
    EventTypeId INT NOT NULL,       
    StoreLocationID BIGINT NULL,
    CompanyId BIGINT NOT NULL,
    UserName VARCHAR(20) NOT NULL,  
    Message TEXT NOT NULL,
    Status VARCHAR(20) NOT NULL,
    AdditionalData JSONB NULL,
    ArchivedAt TIMESTAMP NOT NULL DEFAULT NOW()
);
-- Select * from AuditEvents_Archival;

-- -----------------------------------------------------------------------

--9) procedure to maintain the Partitions, Archival data flow, and drop the old partitions and data older than 12 months from AuditEvents
CREATE OR REPLACE PROCEDURE sp_auditevents_maintain(p_months_to_keep integer DEFAULT 12)
LANGUAGE plpgsql
AS $$
DECLARE
    v_months_to_keep     integer := COALESCE(p_months_to_keep, 12);
   
    v_target_start       date := (date_trunc('month', CURRENT_DATE)
                                  - make_interval(months => v_months_to_keep + 1))::date;
    v_target_end         date := (v_target_start + interval '1 month')::date;
    v_part_name          text := format('auditevents_%s', to_char(v_target_start, 'YYYYMM'));
    v_part_exists        boolean;
    v_rows_copied        bigint := 0;
BEGIN
    -- (1) Runs the Function which Create the current and the future partitions 
	
    PERFORM ensure_auditevents_partitions();

    -- (2) Finds the Partitions which are need to be Archived to the archival table
	
    SELECT EXISTS (
        SELECT 1
        FROM pg_inherits i
        JOIN pg_class   c  ON c.oid = i.inhrelid
        JOIN pg_class   p  ON p.oid = i.inhparent
        WHERE p.oid = 'AuditEvents'::regclass
          AND c.relname = v_part_name
    ) INTO v_part_exists;

    IF NOT v_part_exists THEN
        RAISE NOTICE 'No partition % for %..%; nothing to archive this run.',
                     v_part_name, v_target_start, v_target_end;
        RETURN;
    END IF;

    RAISE NOTICE 'Archiving partition % (%..%) into AuditEvents_Archival...',
                 v_part_name, v_target_start, v_target_end;

    -- (3) Inserts the data from the Partition of the AuditEvents to the  AuditEvents_Archival
	
    EXECUTE format($ins$
        INSERT INTO AuditEvents_Archival
            (Id, EventTimestamp, FunctionalityId, EventTypeId, StoreLocationID,
             CompanyId, UserName, Message, Status, AdditionalData)
        SELECT Id, EventTimestamp, FunctionalityId, EventTypeId, StoreLocationID,
               CompanyId, UserName, Message, Status, AdditionalData
        FROM ONLY %I
        ON CONFLICT (Id) DO NOTHING
    $ins$, v_part_name);

    GET DIAGNOSTICS v_rows_copied = ROW_COUNT;
    RAISE NOTICE 'Copied % rows to archival.', v_rows_copied;

    -- (4) Drops the data or the partition for the 13 month from the 
	
    EXECUTE format('DROP TABLE IF EXISTS %I;', v_part_name);
    RAISE NOTICE 'Dropped partition %; main table now keeps the most recent % months.',
                 v_part_name, v_months_to_keep;
END;
$$;

-- (need to setup cron job for this 'sp_auditevents_maintain')need to run this procedure periodically (e.g. monthly) to maintain partitions and archive old data:
-- call sp_auditevents_maintain();


-- ----------------------------------------------------------
 --10) Get eventtypesname by functionality name
 --Drop function fun_get_eventtypes_by_functionality;
CREATE OR REPLACE FUNCTION fun_get_eventtypes_by_functionality(
    p_functionalityname VARCHAR
)
RETURNS TABLE (
	eventtypeid INT,
    eventtypename VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
	aet.eventtypeid,
	aet.eventtypename
    FROM auditeventtypes aet
    JOIN auditfunctionalities af
        ON af.functionalityid = aet.functionalityid
    WHERE af.functionalityname = p_functionalityname
    ORDER BY aet.eventtypename;
END;
$$;

-- SELECT * FROM fun_get_eventtypes_by_functionality('Authenticate');
-- select * from auditeventtypes;
