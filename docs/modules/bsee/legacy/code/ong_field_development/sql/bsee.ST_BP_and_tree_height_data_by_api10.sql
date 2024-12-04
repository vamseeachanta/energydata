DECLARE @API_WELL_NUMBER NVARCHAR(10) = {};

--DECLARE @API_WELL_NUMBER NVARCHAR(10) = '6081240095';

SELECT API12, WELL_NM_ST_SFIX, WELL_NM_BP_SFIX, SUBSEA_TREE_HEIGHT_AML, SN_EOR
FROM
(SELECT [API_WELL_NUMBER] as API12
FROM [dbo].[mv_api_list]
WHERE LEFT(API_WELL_NUMBER,10) = @API_WELL_NUMBER
)
AS APIListTable

JOIN
(SELECT API_WELL_NUMBER, SN_EOR, WELL_NM_ST_SFIX, WELL_NM_BP_SFIX, SUBSEA_TREE_HEIGHT_AML
FROM [dbo].[mv_eor_mainquery]
)
AS EOR_MAIN_QUERY
on APIListTable.API12 = EOR_MAIN_QUERY.API_WELL_NUMBER
ORDER BY API12, SN_EOR
