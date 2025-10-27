"""
SQL queries for the HealthCheck Dashboard
"""

# Store data query
STORE_DATA_QUERY = """
SELECT
    st.StoreLocationID,
    st.POSSystemCD,
    st.CompanyID,
    st.StoreName,
    st.ZIPCode,
    st.IsPCLess,
    mn.MNSPName AS MNSPID,
    psp.PaymentSystemsProductName,
    st.SiteIP,
    scan.Scandata,
    altria.RCN,
    mhx.LatestEndDateTime
FROM dbo.storelocation AS st
LEFT JOIN dbo.mnsp AS mn ON st.MNSPID = mn.MNSPID
LEFT JOIN dbo.PaymentSystemsProductCode AS psp 
    ON psp.PaymentSystemProductCodeID = st.PaymentSystemsProductCode
OUTER APPLY (
    SELECT MAX(mh.EndTime) AS LatestEndDateTime
    FROM dbo.movementheader AS mh
    WHERE mh.StoreLocationID = st.StoreLocationID
) AS mhx
OUTER APPLY (
    SELECT CASE
        WHEN EXISTS (
            SELECT 1 FROM dbo.SD_ScanDataSetup ss 
            WHERE ss.StoreLocationId = st.StoreLocationID
        ) THEN 'Yes(' + COALESCE(
            STRING_AGG(m.ManufacturerName, ', ') WITHIN GROUP (ORDER BY m.ManufacturerName), ''
        ) + ')'
        ELSE 'No'
    END AS Scandata
    FROM (
        SELECT DISTINCT ssds.ManufactureId
        FROM dbo.SD_ScanDataSetup ssds
        WHERE ssds.StoreLocationId = st.StoreLocationID
    ) d
    LEFT JOIN dbo.Manufacturer m ON m.ManufacturerID = d.ManufactureId
) AS scan
OUTER APPLY (
    SELECT TOP (1) ass.RCN
    FROM dbo.Altria_store_settings AS ass
    WHERE ass.StoreLocationId = st.StoreLocationID
    ORDER BY ass.is_active DESC
) AS altria;
"""

# User data query
USER_DATA_QUERY = """
SELECT
    c.CompanyID,
    c.CompanyName,
    sl.StoreLocationID AS StoreID,
    sl.StoreName,
    ulh.UserName,
    au.email as UserMail,
    anr.NormalizedName AS UserRole,
    CONVERT(VARCHAR, ulh.LogInTime, 120) AS LastLogon
FROM company c
INNER JOIN StoreLocation sl ON c.CompanyID = sl.CompanyID
INNER JOIN (
    SELECT USERID, MAX(LogInTime) AS LastLogon
    FROM UserLoginHistory
    GROUP BY USERID
) AS LatestLogins ON c.CompanyID = (
    SELECT TOP 1 CompanyID 
    FROM UserLoginHistory 
    WHERE USERID = LatestLogins.USERID AND LogInTime = LatestLogins.LastLogon
)
INNER JOIN UserLoginHistory ulh 
    ON ulh.USERID = LatestLogins.USERID AND ulh.LogInTime = LatestLogins.LastLogon
INNER JOIN AspNetUserRoles anur ON anur.UserId = ulh.USERID
INNER JOIN AspNetRoles anr ON anur.RoleId = anr.Id   
LEFT JOIN aspnetusers au ON au.ID = ulh.USERID;
"""

# Database health check query
HEALTH_CHECK_QUERY = "SELECT 1 as status"

# User count query
USER_COUNT_QUERY = "SELECT COUNT(DISTINCT UserName) as unique_users FROM UserLoginHistory"