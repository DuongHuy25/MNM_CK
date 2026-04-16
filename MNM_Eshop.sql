/* =========================================================
   DATABASE: ConvenienceStoreDB
   PLATFORM: SQL Server
   PURPOSE : Full schema for convenience store web system
   NOTE    : Create tables only, no seed data
   ========================================================= */

-- =========================================================
-- 1) CREATE DATABASE
-- =========================================================
IF DB_ID('ConvenienceStoreDB') IS NULL
BEGIN
    CREATE DATABASE ConvenienceStoreDB;
END
GO

USE ConvenienceStoreDB;
GO

-- =========================================================
-- 2) CREATE SCHEMAS
-- =========================================================
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'core') EXEC('CREATE SCHEMA core');
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'catalog') EXEC('CREATE SCHEMA catalog');
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'sales') EXEC('CREATE SCHEMA sales');
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'inventory') EXEC('CREATE SCHEMA inventory');
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'crm') EXEC('CREATE SCHEMA crm');
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'purchasing') EXEC('CREATE SCHEMA purchasing');
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'hr') EXEC('CREATE SCHEMA hr');
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'audit') EXEC('CREATE SCHEMA audit');
GO

-- =========================================================
-- 3) CORE TABLES
-- =========================================================
CREATE TABLE core.Stores (
    StoreID              INT IDENTITY(1,1) PRIMARY KEY,
    StoreCode            NVARCHAR(30) NOT NULL UNIQUE,
    StoreName            NVARCHAR(200) NOT NULL,
    Phone                NVARCHAR(20) NULL,
    Email                NVARCHAR(150) NULL,
    AddressLine          NVARCHAR(300) NULL,
    Ward                 NVARCHAR(100) NULL,
    District             NVARCHAR(100) NULL,
    City                 NVARCHAR(100) NULL,
    Province             NVARCHAR(100) NULL,
    ZipCode              NVARCHAR(20) NULL,
    OpenTime             TIME NULL,
    CloseTime            TIME NULL,
    IsActive             BIT NOT NULL CONSTRAINT DF_Stores_IsActive DEFAULT(1),
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_Stores_CreatedAt DEFAULT(SYSDATETIME()),
    UpdatedAt            DATETIME2 NULL
);
GO

CREATE TABLE core.Roles (
    RoleID               INT IDENTITY(1,1) PRIMARY KEY,
    RoleCode             NVARCHAR(50) NOT NULL UNIQUE,
    RoleName             NVARCHAR(100) NOT NULL,
    Description          NVARCHAR(500) NULL,
    IsSystem             BIT NOT NULL CONSTRAINT DF_Roles_IsSystem DEFAULT(0),
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_Roles_CreatedAt DEFAULT(SYSDATETIME())
);
GO

CREATE TABLE core.Users (
    UserID               INT IDENTITY(1,1) PRIMARY KEY,
    Username             NVARCHAR(50) NOT NULL UNIQUE,
    PasswordHash         NVARCHAR(500) NOT NULL,
    FullName             NVARCHAR(150) NOT NULL,
    Email                NVARCHAR(150) NULL UNIQUE,
    Phone                NVARCHAR(20) NULL,
    AvatarUrl            NVARCHAR(500) NULL,
    DefaultStoreID       INT NULL,
    IsActive             BIT NOT NULL CONSTRAINT DF_Users_IsActive DEFAULT(1),
    LastLoginAt          DATETIME2 NULL,
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_Users_CreatedAt DEFAULT(SYSDATETIME()),
    UpdatedAt            DATETIME2 NULL,
    CONSTRAINT FK_Users_Stores FOREIGN KEY (DefaultStoreID) REFERENCES core.Stores(StoreID)
);
GO

CREATE TABLE core.UserRoles (
    UserRoleID           INT IDENTITY(1,1) PRIMARY KEY,
    UserID               INT NOT NULL,
    RoleID               INT NOT NULL,
    AssignedAt           DATETIME2 NOT NULL CONSTRAINT DF_UserRoles_AssignedAt DEFAULT(SYSDATETIME()),
    AssignedByUserID     INT NULL,
    CONSTRAINT UQ_UserRoles UNIQUE(UserID, RoleID),
    CONSTRAINT FK_UserRoles_Users FOREIGN KEY (UserID) REFERENCES core.Users(UserID),
    CONSTRAINT FK_UserRoles_Roles FOREIGN KEY (RoleID) REFERENCES core.Roles(RoleID),
    CONSTRAINT FK_UserRoles_AssignedBy FOREIGN KEY (AssignedByUserID) REFERENCES core.Users(UserID)
);
GO

CREATE TABLE core.Settings (
    SettingID            INT IDENTITY(1,1) PRIMARY KEY,
    SettingGroup         NVARCHAR(100) NOT NULL,
    SettingKey           NVARCHAR(100) NOT NULL,
    SettingValue         NVARCHAR(MAX) NULL,
    ValueType            NVARCHAR(50) NOT NULL CONSTRAINT DF_Settings_ValueType DEFAULT('string'),
    Description          NVARCHAR(500) NULL,
    IsPublic             BIT NOT NULL CONSTRAINT DF_Settings_IsPublic DEFAULT(0),
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_Settings_CreatedAt DEFAULT(SYSDATETIME()),
    UpdatedAt            DATETIME2 NULL,
    CONSTRAINT UQ_Settings UNIQUE(SettingGroup, SettingKey)
);
GO

-- =========================================================
-- 4) HR TABLES
-- =========================================================
CREATE TABLE hr.Departments (
    DepartmentID         INT IDENTITY(1,1) PRIMARY KEY,
    DepartmentCode       NVARCHAR(30) NOT NULL UNIQUE,
    DepartmentName       NVARCHAR(150) NOT NULL,
    Description          NVARCHAR(500) NULL,
    IsActive             BIT NOT NULL CONSTRAINT DF_Departments_IsActive DEFAULT(1)
);
GO

CREATE TABLE hr.Employees (
    EmployeeID           INT IDENTITY(1,1) PRIMARY KEY,
    EmployeeCode         NVARCHAR(30) NOT NULL UNIQUE,
    UserID               INT NULL UNIQUE,
    StoreID              INT NOT NULL,
    DepartmentID         INT NULL,
    FullName             NVARCHAR(150) NOT NULL,
    Gender               NVARCHAR(20) NULL,
    DateOfBirth          DATE NULL,
    Phone                NVARCHAR(20) NULL,
    Email                NVARCHAR(150) NULL,
    AddressLine          NVARCHAR(300) NULL,
    HireDate             DATE NOT NULL,
    TerminationDate      DATE NULL,
    PositionTitle        NVARCHAR(100) NULL,
    Salary               DECIMAL(18,2) NULL,
    EmploymentStatus     NVARCHAR(30) NOT NULL CONSTRAINT DF_Employees_EmploymentStatus DEFAULT('ACTIVE'),
    ManagerEmployeeID    INT NULL,
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_Employees_CreatedAt DEFAULT(SYSDATETIME()),
    UpdatedAt            DATETIME2 NULL,
    CONSTRAINT FK_Employees_User FOREIGN KEY (UserID) REFERENCES core.Users(UserID),
    CONSTRAINT FK_Employees_Store FOREIGN KEY (StoreID) REFERENCES core.Stores(StoreID),
    CONSTRAINT FK_Employees_Department FOREIGN KEY (DepartmentID) REFERENCES hr.Departments(DepartmentID),
    CONSTRAINT FK_Employees_Manager FOREIGN KEY (ManagerEmployeeID) REFERENCES hr.Employees(EmployeeID)
);
GO

CREATE TABLE hr.Shifts (
    ShiftID              INT IDENTITY(1,1) PRIMARY KEY,
    ShiftCode            NVARCHAR(30) NOT NULL UNIQUE,
    ShiftName            NVARCHAR(100) NOT NULL,
    StartTime            TIME NOT NULL,
    EndTime              TIME NOT NULL,
    BreakMinutes         INT NOT NULL CONSTRAINT DF_Shifts_BreakMinutes DEFAULT(0),
    IsOvernight          BIT NOT NULL CONSTRAINT DF_Shifts_IsOvernight DEFAULT(0),
    IsActive             BIT NOT NULL CONSTRAINT DF_Shifts_IsActive DEFAULT(1)
);
GO

CREATE TABLE hr.EmployeeShifts (
    EmployeeShiftID      INT IDENTITY(1,1) PRIMARY KEY,
    EmployeeID           INT NOT NULL,
    StoreID              INT NOT NULL,
    ShiftID              INT NOT NULL,
    WorkDate             DATE NOT NULL,
    CheckInAt            DATETIME2 NULL,
    CheckOutAt           DATETIME2 NULL,
    Status               NVARCHAR(30) NOT NULL CONSTRAINT DF_EmployeeShifts_Status DEFAULT('SCHEDULED'),
    Notes                NVARCHAR(500) NULL,
    CONSTRAINT UQ_EmployeeShifts UNIQUE(EmployeeID, WorkDate, ShiftID),
    CONSTRAINT FK_EmployeeShifts_Employee FOREIGN KEY (EmployeeID) REFERENCES hr.Employees(EmployeeID),
    CONSTRAINT FK_EmployeeShifts_Store FOREIGN KEY (StoreID) REFERENCES core.Stores(StoreID),
    CONSTRAINT FK_EmployeeShifts_Shift FOREIGN KEY (ShiftID) REFERENCES hr.Shifts(ShiftID)
);
GO

-- =========================================================
-- 5) CATALOG TABLES
-- =========================================================
CREATE TABLE catalog.Units (
    UnitID               INT IDENTITY(1,1) PRIMARY KEY,
    UnitCode             NVARCHAR(20) NOT NULL UNIQUE,
    UnitName             NVARCHAR(50) NOT NULL,
    Description          NVARCHAR(200) NULL,
    IsActive             BIT NOT NULL CONSTRAINT DF_Units_IsActive DEFAULT(1)
);
GO

CREATE TABLE catalog.Brands (
    BrandID              INT IDENTITY(1,1) PRIMARY KEY,
    BrandCode            NVARCHAR(30) NOT NULL UNIQUE,
    BrandName            NVARCHAR(100) NOT NULL,
    Description          NVARCHAR(500) NULL,
    CountryOfOrigin      NVARCHAR(100) NULL,
    IsActive             BIT NOT NULL CONSTRAINT DF_Brands_IsActive DEFAULT(1),
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_Brands_CreatedAt DEFAULT(SYSDATETIME())
);
GO

CREATE TABLE catalog.Categories (
    CategoryID           INT IDENTITY(1,1) PRIMARY KEY,
    ParentCategoryID     INT NULL,
    CategoryCode         NVARCHAR(30) NOT NULL UNIQUE,
    CategoryName         NVARCHAR(150) NOT NULL,
    Description          NVARCHAR(500) NULL,
    SortOrder            INT NOT NULL CONSTRAINT DF_Categories_SortOrder DEFAULT(0),
    IsActive             BIT NOT NULL CONSTRAINT DF_Categories_IsActive DEFAULT(1),
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_Categories_CreatedAt DEFAULT(SYSDATETIME()),
    CONSTRAINT FK_Categories_Parent FOREIGN KEY (ParentCategoryID) REFERENCES catalog.Categories(CategoryID)
);
GO

CREATE TABLE catalog.TaxRates (
    TaxRateID            INT IDENTITY(1,1) PRIMARY KEY,
    TaxCode              NVARCHAR(30) NOT NULL UNIQUE,
    TaxName              NVARCHAR(100) NOT NULL,
    TaxPercent           DECIMAL(5,2) NOT NULL,
    IsActive             BIT NOT NULL CONSTRAINT DF_TaxRates_IsActive DEFAULT(1),
    EffectiveFrom        DATE NULL,
    EffectiveTo          DATE NULL
);
GO

CREATE TABLE catalog.Products (
    ProductID            INT IDENTITY(1,1) PRIMARY KEY,
    ProductCode          NVARCHAR(50) NOT NULL UNIQUE,
    SKU                  NVARCHAR(50) NOT NULL UNIQUE,
    ProductName          NVARCHAR(200) NOT NULL,
    ShortName            NVARCHAR(100) NULL,
    CategoryID           INT NOT NULL,
    BrandID              INT NULL,
    BaseUnitID           INT NOT NULL,
    TaxRateID            INT NULL,
    ProductType          NVARCHAR(30) NOT NULL CONSTRAINT DF_Products_ProductType DEFAULT('NORMAL'),
    CostPrice            DECIMAL(18,2) NOT NULL CONSTRAINT DF_Products_CostPrice DEFAULT(0),
    SalePrice            DECIMAL(18,2) NOT NULL CONSTRAINT DF_Products_SalePrice DEFAULT(0),
    MinStock             DECIMAL(18,3) NOT NULL CONSTRAINT DF_Products_MinStock DEFAULT(0),
    MaxStock             DECIMAL(18,3) NULL,
    ReorderPoint         DECIMAL(18,3) NULL,
    Weight               DECIMAL(18,3) NULL,
    Volume               DECIMAL(18,3) NULL,
    IsBatchTracked       BIT NOT NULL CONSTRAINT DF_Products_IsBatchTracked DEFAULT(0),
    IsExpiryTracked      BIT NOT NULL CONSTRAINT DF_Products_IsExpiryTracked DEFAULT(0),
    ShelfLifeDays        INT NULL,
    IsActive             BIT NOT NULL CONSTRAINT DF_Products_IsActive DEFAULT(1),
    ImageUrl             NVARCHAR(500) NULL,
    Description          NVARCHAR(1000) NULL,
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_Products_CreatedAt DEFAULT(SYSDATETIME()),
    UpdatedAt            DATETIME2 NULL,
    CONSTRAINT FK_Products_Category FOREIGN KEY (CategoryID) REFERENCES catalog.Categories(CategoryID),
    CONSTRAINT FK_Products_Brand FOREIGN KEY (BrandID) REFERENCES catalog.Brands(BrandID),
    CONSTRAINT FK_Products_Unit FOREIGN KEY (BaseUnitID) REFERENCES catalog.Units(UnitID),
    CONSTRAINT FK_Products_TaxRate FOREIGN KEY (TaxRateID) REFERENCES catalog.TaxRates(TaxRateID)
);
GO

CREATE TABLE catalog.ProductBarcodes (
    ProductBarcodeID     INT IDENTITY(1,1) PRIMARY KEY,
    ProductID            INT NOT NULL,
    Barcode              NVARCHAR(50) NOT NULL,
    BarcodeType          NVARCHAR(30) NOT NULL CONSTRAINT DF_ProductBarcodes_BarcodeType DEFAULT('EAN'),
    IsPrimary            BIT NOT NULL CONSTRAINT DF_ProductBarcodes_IsPrimary DEFAULT(0),
    IsActive             BIT NOT NULL CONSTRAINT DF_ProductBarcodes_IsActive DEFAULT(1),
    CONSTRAINT UQ_ProductBarcodes_Barcode UNIQUE(Barcode),
    CONSTRAINT FK_ProductBarcodes_Product FOREIGN KEY (ProductID) REFERENCES catalog.Products(ProductID)
);
GO

CREATE TABLE catalog.ProductPrices (
    ProductPriceID       INT IDENTITY(1,1) PRIMARY KEY,
    ProductID            INT NOT NULL,
    StoreID              INT NULL,
    PriceType            NVARCHAR(30) NOT NULL CONSTRAINT DF_ProductPrices_PriceType DEFAULT('RETAIL'),
    Price                DECIMAL(18,2) NOT NULL,
    EffectiveFrom        DATETIME2 NOT NULL,
    EffectiveTo          DATETIME2 NULL,
    IsActive             BIT NOT NULL CONSTRAINT DF_ProductPrices_IsActive DEFAULT(1),
    CreatedByUserID      INT NULL,
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_ProductPrices_CreatedAt DEFAULT(SYSDATETIME()),
    CONSTRAINT FK_ProductPrices_Product FOREIGN KEY (ProductID) REFERENCES catalog.Products(ProductID),
    CONSTRAINT FK_ProductPrices_Store FOREIGN KEY (StoreID) REFERENCES core.Stores(StoreID),
    CONSTRAINT FK_ProductPrices_CreatedBy FOREIGN KEY (CreatedByUserID) REFERENCES core.Users(UserID)
);
GO

CREATE TABLE catalog.ProductSuppliers (
    ProductSupplierID    INT IDENTITY(1,1) PRIMARY KEY,
    ProductID            INT NOT NULL,
    SupplierID           INT NOT NULL,
    SupplierProductCode  NVARCHAR(50) NULL,
    LastPurchasePrice    DECIMAL(18,2) NULL,
    IsPreferred          BIT NOT NULL CONSTRAINT DF_ProductSuppliers_IsPreferred DEFAULT(0),
    LeadTimeDays         INT NULL,
    MinOrderQty          DECIMAL(18,3) NULL,
    IsActive             BIT NOT NULL CONSTRAINT DF_ProductSuppliers_IsActive DEFAULT(1)
);
GO

-- =========================================================
-- 6) PURCHASING TABLES
-- =========================================================
CREATE TABLE purchasing.Suppliers (
    SupplierID           INT IDENTITY(1,1) PRIMARY KEY,
    SupplierCode         NVARCHAR(30) NOT NULL UNIQUE,
    SupplierName         NVARCHAR(200) NOT NULL,
    ContactPerson        NVARCHAR(150) NULL,
    Phone                NVARCHAR(20) NULL,
    Email                NVARCHAR(150) NULL,
    TaxCode              NVARCHAR(50) NULL,
    AddressLine          NVARCHAR(300) NULL,
    Ward                 NVARCHAR(100) NULL,
    District             NVARCHAR(100) NULL,
    City                 NVARCHAR(100) NULL,
    Province             NVARCHAR(100) NULL,
    PaymentTerms         NVARCHAR(200) NULL,
    IsActive             BIT NOT NULL CONSTRAINT DF_Suppliers_IsActive DEFAULT(1),
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_Suppliers_CreatedAt DEFAULT(SYSDATETIME())
);
GO

ALTER TABLE catalog.ProductSuppliers
ADD CONSTRAINT FK_ProductSuppliers_Product FOREIGN KEY (ProductID) REFERENCES catalog.Products(ProductID),
    CONSTRAINT FK_ProductSuppliers_Supplier FOREIGN KEY (SupplierID) REFERENCES purchasing.Suppliers(SupplierID),
    CONSTRAINT UQ_ProductSuppliers UNIQUE(ProductID, SupplierID);
GO

CREATE TABLE purchasing.PurchaseOrders (
    PurchaseOrderID      INT IDENTITY(1,1) PRIMARY KEY,
    PONumber             NVARCHAR(30) NOT NULL UNIQUE,
    StoreID              INT NOT NULL,
    SupplierID           INT NOT NULL,
    OrderDate            DATE NOT NULL,
    ExpectedDate         DATE NULL,
    Status               NVARCHAR(30) NOT NULL CONSTRAINT DF_PurchaseOrders_Status DEFAULT('DRAFT'),
    SubTotal             DECIMAL(18,2) NOT NULL CONSTRAINT DF_PurchaseOrders_SubTotal DEFAULT(0),
    DiscountAmount       DECIMAL(18,2) NOT NULL CONSTRAINT DF_PurchaseOrders_DiscountAmount DEFAULT(0),
    TaxAmount            DECIMAL(18,2) NOT NULL CONSTRAINT DF_PurchaseOrders_TaxAmount DEFAULT(0),
    TotalAmount          DECIMAL(18,2) NOT NULL CONSTRAINT DF_PurchaseOrders_TotalAmount DEFAULT(0),
    Notes                NVARCHAR(1000) NULL,
    CreatedByUserID      INT NULL,
    ApprovedByUserID     INT NULL,
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_PurchaseOrders_CreatedAt DEFAULT(SYSDATETIME()),
    UpdatedAt            DATETIME2 NULL,
    CONSTRAINT FK_PurchaseOrders_Store FOREIGN KEY (StoreID) REFERENCES core.Stores(StoreID),
    CONSTRAINT FK_PurchaseOrders_Supplier FOREIGN KEY (SupplierID) REFERENCES purchasing.Suppliers(SupplierID),
    CONSTRAINT FK_PurchaseOrders_CreatedBy FOREIGN KEY (CreatedByUserID) REFERENCES core.Users(UserID),
    CONSTRAINT FK_PurchaseOrders_ApprovedBy FOREIGN KEY (ApprovedByUserID) REFERENCES core.Users(UserID)
);
GO

CREATE TABLE purchasing.PurchaseOrderItems (
    PurchaseOrderItemID  INT IDENTITY(1,1) PRIMARY KEY,
    PurchaseOrderID      INT NOT NULL,
    ProductID            INT NOT NULL,
    UnitID               INT NOT NULL,
    OrderedQty           DECIMAL(18,3) NOT NULL,
    ReceivedQty          DECIMAL(18,3) NOT NULL CONSTRAINT DF_POItems_ReceivedQty DEFAULT(0),
    UnitPrice            DECIMAL(18,2) NOT NULL,
    DiscountPercent      DECIMAL(5,2) NOT NULL CONSTRAINT DF_POItems_DiscountPercent DEFAULT(0),
    TaxPercent           DECIMAL(5,2) NOT NULL CONSTRAINT DF_POItems_TaxPercent DEFAULT(0),
    LineTotal            DECIMAL(18,2) NOT NULL CONSTRAINT DF_POItems_LineTotal DEFAULT(0),
    Notes                NVARCHAR(500) NULL,
    CONSTRAINT FK_POItems_PO FOREIGN KEY (PurchaseOrderID) REFERENCES purchasing.PurchaseOrders(PurchaseOrderID),
    CONSTRAINT FK_POItems_Product FOREIGN KEY (ProductID) REFERENCES catalog.Products(ProductID),
    CONSTRAINT FK_POItems_Unit FOREIGN KEY (UnitID) REFERENCES catalog.Units(UnitID),
    CONSTRAINT UQ_POItems UNIQUE(PurchaseOrderID, ProductID)
);
GO

CREATE TABLE purchasing.GoodsReceipts (
    GoodsReceiptID       INT IDENTITY(1,1) PRIMARY KEY,
    GRNNumber            NVARCHAR(30) NOT NULL UNIQUE,
    PurchaseOrderID      INT NULL,
    StoreID              INT NOT NULL,
    SupplierID           INT NOT NULL,
    ReceiptDate          DATETIME2 NOT NULL,
    Status               NVARCHAR(30) NOT NULL CONSTRAINT DF_GoodsReceipts_Status DEFAULT('POSTED'),
    Notes                NVARCHAR(1000) NULL,
    CreatedByUserID      INT NULL,
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_GoodsReceipts_CreatedAt DEFAULT(SYSDATETIME()),
    CONSTRAINT FK_GoodsReceipts_PO FOREIGN KEY (PurchaseOrderID) REFERENCES purchasing.PurchaseOrders(PurchaseOrderID),
    CONSTRAINT FK_GoodsReceipts_Store FOREIGN KEY (StoreID) REFERENCES core.Stores(StoreID),
    CONSTRAINT FK_GoodsReceipts_Supplier FOREIGN KEY (SupplierID) REFERENCES purchasing.Suppliers(SupplierID),
    CONSTRAINT FK_GoodsReceipts_CreatedBy FOREIGN KEY (CreatedByUserID) REFERENCES core.Users(UserID)
);
GO

CREATE TABLE purchasing.GoodsReceiptItems (
    GoodsReceiptItemID   INT IDENTITY(1,1) PRIMARY KEY,
    GoodsReceiptID       INT NOT NULL,
    ProductID            INT NOT NULL,
    UnitID               INT NOT NULL,
    Quantity             DECIMAL(18,3) NOT NULL,
    UnitCost             DECIMAL(18,2) NOT NULL,
    BatchNumber          NVARCHAR(50) NULL,
    ManufactureDate      DATE NULL,
    ExpiryDate           DATE NULL,
    LineTotal            DECIMAL(18,2) NOT NULL CONSTRAINT DF_GRItems_LineTotal DEFAULT(0),
    CONSTRAINT FK_GRItems_GR FOREIGN KEY (GoodsReceiptID) REFERENCES purchasing.GoodsReceipts(GoodsReceiptID),
    CONSTRAINT FK_GRItems_Product FOREIGN KEY (ProductID) REFERENCES catalog.Products(ProductID),
    CONSTRAINT FK_GRItems_Unit FOREIGN KEY (UnitID) REFERENCES catalog.Units(UnitID)
);
GO

-- =========================================================
-- 7) INVENTORY TABLES
-- =========================================================
CREATE TABLE inventory.Warehouses (
    WarehouseID          INT IDENTITY(1,1) PRIMARY KEY,
    StoreID              INT NOT NULL,
    WarehouseCode        NVARCHAR(30) NOT NULL,
    WarehouseName        NVARCHAR(150) NOT NULL,
    WarehouseType        NVARCHAR(30) NOT NULL CONSTRAINT DF_Warehouses_WarehouseType DEFAULT('MAIN'),
    AddressLine          NVARCHAR(300) NULL,
    IsDefault            BIT NOT NULL CONSTRAINT DF_Warehouses_IsDefault DEFAULT(0),
    IsActive             BIT NOT NULL CONSTRAINT DF_Warehouses_IsActive DEFAULT(1),
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_Warehouses_CreatedAt DEFAULT(SYSDATETIME()),
    CONSTRAINT UQ_Warehouses UNIQUE(StoreID, WarehouseCode),
    CONSTRAINT FK_Warehouses_Store FOREIGN KEY (StoreID) REFERENCES core.Stores(StoreID)
);
GO

CREATE TABLE inventory.StockBalances (
    StockBalanceID       INT IDENTITY(1,1) PRIMARY KEY,
    StoreID              INT NOT NULL,
    WarehouseID          INT NOT NULL,
    ProductID            INT NOT NULL,
    BatchNumber          NVARCHAR(50) NULL,
    ExpiryDate           DATE NULL,
    QuantityOnHand       DECIMAL(18,3) NOT NULL CONSTRAINT DF_StockBalances_QtyOnHand DEFAULT(0),
    QuantityReserved     DECIMAL(18,3) NOT NULL CONSTRAINT DF_StockBalances_QtyReserved DEFAULT(0),
    AverageCost          DECIMAL(18,2) NOT NULL CONSTRAINT DF_StockBalances_AvgCost DEFAULT(0),
    LastUpdatedAt        DATETIME2 NOT NULL CONSTRAINT DF_StockBalances_LastUpdatedAt DEFAULT(SYSDATETIME()),
    CONSTRAINT FK_StockBalances_Store FOREIGN KEY (StoreID) REFERENCES core.Stores(StoreID),
    CONSTRAINT FK_StockBalances_Warehouse FOREIGN KEY (WarehouseID) REFERENCES inventory.Warehouses(WarehouseID),
    CONSTRAINT FK_StockBalances_Product FOREIGN KEY (ProductID) REFERENCES catalog.Products(ProductID)
);
GO

CREATE TABLE inventory.StockMovements (
    StockMovementID      BIGINT IDENTITY(1,1) PRIMARY KEY,
    StoreID              INT NOT NULL,
    WarehouseID          INT NOT NULL,
    ProductID            INT NOT NULL,
    MovementType         NVARCHAR(30) NOT NULL, -- IN / OUT / ADJUST / TRANSFER
    ReferenceType        NVARCHAR(30) NULL,     -- SALE / PURCHASE / RETURN / COUNT / TRANSFER
    ReferenceID          BIGINT NULL,
    BatchNumber          NVARCHAR(50) NULL,
    ExpiryDate           DATE NULL,
    Quantity             DECIMAL(18,3) NOT NULL,
    UnitCost             DECIMAL(18,2) NULL,
    BeforeQty            DECIMAL(18,3) NULL,
    AfterQty             DECIMAL(18,3) NULL,
    Notes                NVARCHAR(500) NULL,
    CreatedByUserID      INT NULL,
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_StockMovements_CreatedAt DEFAULT(SYSDATETIME()),
    CONSTRAINT FK_StockMovements_Store FOREIGN KEY (StoreID) REFERENCES core.Stores(StoreID),
    CONSTRAINT FK_StockMovements_Warehouse FOREIGN KEY (WarehouseID) REFERENCES inventory.Warehouses(WarehouseID),
    CONSTRAINT FK_StockMovements_Product FOREIGN KEY (ProductID) REFERENCES catalog.Products(ProductID),
    CONSTRAINT FK_StockMovements_User FOREIGN KEY (CreatedByUserID) REFERENCES core.Users(UserID)
);
GO

CREATE TABLE inventory.StockTransfers (
    StockTransferID      INT IDENTITY(1,1) PRIMARY KEY,
    TransferNumber       NVARCHAR(30) NOT NULL UNIQUE,
    FromStoreID          INT NOT NULL,
    FromWarehouseID      INT NOT NULL,
    ToStoreID            INT NOT NULL,
    ToWarehouseID        INT NOT NULL,
    TransferDate         DATETIME2 NOT NULL,
    Status               NVARCHAR(30) NOT NULL CONSTRAINT DF_StockTransfers_Status DEFAULT('DRAFT'),
    Notes                NVARCHAR(1000) NULL,
    CreatedByUserID      INT NULL,
    ApprovedByUserID     INT NULL,
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_StockTransfers_CreatedAt DEFAULT(SYSDATETIME()),
    CONSTRAINT FK_StockTransfers_FromStore FOREIGN KEY (FromStoreID) REFERENCES core.Stores(StoreID),
    CONSTRAINT FK_StockTransfers_FromWarehouse FOREIGN KEY (FromWarehouseID) REFERENCES inventory.Warehouses(WarehouseID),
    CONSTRAINT FK_StockTransfers_ToStore FOREIGN KEY (ToStoreID) REFERENCES core.Stores(StoreID),
    CONSTRAINT FK_StockTransfers_ToWarehouse FOREIGN KEY (ToWarehouseID) REFERENCES inventory.Warehouses(WarehouseID),
    CONSTRAINT FK_StockTransfers_CreatedBy FOREIGN KEY (CreatedByUserID) REFERENCES core.Users(UserID),
    CONSTRAINT FK_StockTransfers_ApprovedBy FOREIGN KEY (ApprovedByUserID) REFERENCES core.Users(UserID)
);
GO

CREATE TABLE inventory.StockTransferItems (
    StockTransferItemID  INT IDENTITY(1,1) PRIMARY KEY,
    StockTransferID      INT NOT NULL,
    ProductID            INT NOT NULL,
    Quantity             DECIMAL(18,3) NOT NULL,
    UnitCost             DECIMAL(18,2) NULL,
    BatchNumber          NVARCHAR(50) NULL,
    ExpiryDate           DATE NULL,
    Notes                NVARCHAR(500) NULL,
    CONSTRAINT FK_StockTransferItems_Transfer FOREIGN KEY (StockTransferID) REFERENCES inventory.StockTransfers(StockTransferID),
    CONSTRAINT FK_StockTransferItems_Product FOREIGN KEY (ProductID) REFERENCES catalog.Products(ProductID)
);
GO

CREATE TABLE inventory.StockCounts (
    StockCountID         INT IDENTITY(1,1) PRIMARY KEY,
    CountNumber          NVARCHAR(30) NOT NULL UNIQUE,
    StoreID              INT NOT NULL,
    WarehouseID          INT NOT NULL,
    CountDate            DATETIME2 NOT NULL,
    Status               NVARCHAR(30) NOT NULL CONSTRAINT DF_StockCounts_Status DEFAULT('DRAFT'),
    Notes                NVARCHAR(1000) NULL,
    CreatedByUserID      INT NULL,
    ApprovedByUserID     INT NULL,
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_StockCounts_CreatedAt DEFAULT(SYSDATETIME()),
    CONSTRAINT FK_StockCounts_Store FOREIGN KEY (StoreID) REFERENCES core.Stores(StoreID),
    CONSTRAINT FK_StockCounts_Warehouse FOREIGN KEY (WarehouseID) REFERENCES inventory.Warehouses(WarehouseID),
    CONSTRAINT FK_StockCounts_CreatedBy FOREIGN KEY (CreatedByUserID) REFERENCES core.Users(UserID),
    CONSTRAINT FK_StockCounts_ApprovedBy FOREIGN KEY (ApprovedByUserID) REFERENCES core.Users(UserID)
);
GO

CREATE TABLE inventory.StockCountItems (
    StockCountItemID     INT IDENTITY(1,1) PRIMARY KEY,
    StockCountID         INT NOT NULL,
    ProductID            INT NOT NULL,
    SystemQty            DECIMAL(18,3) NOT NULL,
    CountedQty           DECIMAL(18,3) NOT NULL,
    DifferenceQty        DECIMAL(18,3) NOT NULL,
    BatchNumber          NVARCHAR(50) NULL,
    ExpiryDate           DATE NULL,
    Notes                NVARCHAR(500) NULL,
    CONSTRAINT FK_StockCountItems_Count FOREIGN KEY (StockCountID) REFERENCES inventory.StockCounts(StockCountID),
    CONSTRAINT FK_StockCountItems_Product FOREIGN KEY (ProductID) REFERENCES catalog.Products(ProductID)
);
GO

-- =========================================================
-- 8) CRM TABLES
-- =========================================================
CREATE TABLE crm.CustomerGroups (
    CustomerGroupID      INT IDENTITY(1,1) PRIMARY KEY,
    GroupCode            NVARCHAR(30) NOT NULL UNIQUE,
    GroupName            NVARCHAR(100) NOT NULL,
    DiscountPercent      DECIMAL(5,2) NOT NULL CONSTRAINT DF_CustomerGroups_Discount DEFAULT(0),
    Description          NVARCHAR(500) NULL,
    IsActive             BIT NOT NULL CONSTRAINT DF_CustomerGroups_IsActive DEFAULT(1)
);
GO

CREATE TABLE crm.Customers (
    CustomerID           INT IDENTITY(1,1) PRIMARY KEY,
    CustomerCode         NVARCHAR(30) NOT NULL UNIQUE,
    FullName             NVARCHAR(150) NOT NULL,
    Phone                NVARCHAR(20) NULL UNIQUE,
    Email                NVARCHAR(150) NULL,
    Gender               NVARCHAR(20) NULL,
    DateOfBirth          DATE NULL,
    AddressLine          NVARCHAR(300) NULL,
    Ward                 NVARCHAR(100) NULL,
    District             NVARCHAR(100) NULL,
    City                 NVARCHAR(100) NULL,
    Province             NVARCHAR(100) NULL,
    CustomerGroupID      INT NULL,
    LoyaltyPoints        INT NOT NULL CONSTRAINT DF_Customers_LoyaltyPoints DEFAULT(0),
    TotalSpent           DECIMAL(18,2) NOT NULL CONSTRAINT DF_Customers_TotalSpent DEFAULT(0),
    IsActive             BIT NOT NULL CONSTRAINT DF_Customers_IsActive DEFAULT(1),
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_Customers_CreatedAt DEFAULT(SYSDATETIME()),
    UpdatedAt            DATETIME2 NULL,
    CONSTRAINT FK_Customers_Group FOREIGN KEY (CustomerGroupID) REFERENCES crm.CustomerGroups(CustomerGroupID)
);
GO

CREATE TABLE crm.LoyaltyTransactions (
    LoyaltyTransactionID BIGINT IDENTITY(1,1) PRIMARY KEY,
    CustomerID           INT NOT NULL,
    TransactionType      NVARCHAR(30) NOT NULL, -- EARN / REDEEM / ADJUST
    Points               INT NOT NULL,
    ReferenceType        NVARCHAR(30) NULL,
    ReferenceID          BIGINT NULL,
    Notes                NVARCHAR(500) NULL,
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_LoyaltyTransactions_CreatedAt DEFAULT(SYSDATETIME()),
    CONSTRAINT FK_LoyaltyTransactions_Customer FOREIGN KEY (CustomerID) REFERENCES crm.Customers(CustomerID)
);
GO

CREATE TABLE crm.Promotions (
    PromotionID          INT IDENTITY(1,1) PRIMARY KEY,
    PromotionCode        NVARCHAR(30) NOT NULL UNIQUE,
    PromotionName        NVARCHAR(200) NOT NULL,
    PromotionType        NVARCHAR(30) NOT NULL, -- ORDER / PRODUCT / BUY_X_GET_Y / PERCENT / AMOUNT
    StartAt              DATETIME2 NOT NULL,
    EndAt                DATETIME2 NOT NULL,
    DiscountPercent      DECIMAL(5,2) NULL,
    DiscountAmount       DECIMAL(18,2) NULL,
    MinOrderAmount       DECIMAL(18,2) NULL,
    MaxDiscountAmount    DECIMAL(18,2) NULL,
    IsActive             BIT NOT NULL CONSTRAINT DF_Promotions_IsActive DEFAULT(1),
    Description          NVARCHAR(1000) NULL,
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_Promotions_CreatedAt DEFAULT(SYSDATETIME())
);
GO

CREATE TABLE crm.PromotionProducts (
    PromotionProductID   INT IDENTITY(1,1) PRIMARY KEY,
    PromotionID          INT NOT NULL,
    ProductID            INT NOT NULL,
    CONSTRAINT UQ_PromotionProducts UNIQUE(PromotionID, ProductID),
    CONSTRAINT FK_PromotionProducts_Promotion FOREIGN KEY (PromotionID) REFERENCES crm.Promotions(PromotionID),
    CONSTRAINT FK_PromotionProducts_Product FOREIGN KEY (ProductID) REFERENCES catalog.Products(ProductID)
);
GO

CREATE TABLE crm.Coupons (
    CouponID             INT IDENTITY(1,1) PRIMARY KEY,
    CouponCode           NVARCHAR(50) NOT NULL UNIQUE,
    PromotionID          INT NULL,
    CustomerID           INT NULL,
    DiscountType         NVARCHAR(20) NOT NULL CONSTRAINT DF_Coupons_DiscountType DEFAULT('AMOUNT'),
    DiscountValue        DECIMAL(18,2) NOT NULL,
    MinOrderAmount       DECIMAL(18,2) NULL,
    StartAt              DATETIME2 NULL,
    EndAt                DATETIME2 NULL,
    UsageLimit           INT NOT NULL CONSTRAINT DF_Coupons_UsageLimit DEFAULT(1),
    UsedCount            INT NOT NULL CONSTRAINT DF_Coupons_UsedCount DEFAULT(0),
    IsActive             BIT NOT NULL CONSTRAINT DF_Coupons_IsActive DEFAULT(1),
    CONSTRAINT FK_Coupons_Promotion FOREIGN KEY (PromotionID) REFERENCES crm.Promotions(PromotionID),
    CONSTRAINT FK_Coupons_Customer FOREIGN KEY (CustomerID) REFERENCES crm.Customers(CustomerID)
);
GO

-- =========================================================
-- 9) SALES TABLES
-- =========================================================
CREATE TABLE sales.PaymentMethods (
    PaymentMethodID      INT IDENTITY(1,1) PRIMARY KEY,
    MethodCode           NVARCHAR(30) NOT NULL UNIQUE,
    MethodName           NVARCHAR(100) NOT NULL,
    RequiresReference    BIT NOT NULL CONSTRAINT DF_PaymentMethods_RequiresReference DEFAULT(0),
    IsActive             BIT NOT NULL CONSTRAINT DF_PaymentMethods_IsActive DEFAULT(1)
);
GO

CREATE TABLE sales.CashRegisters (
    CashRegisterID       INT IDENTITY(1,1) PRIMARY KEY,
    StoreID              INT NOT NULL,
    RegisterCode         NVARCHAR(30) NOT NULL,
    RegisterName         NVARCHAR(100) NOT NULL,
    LocationDescription  NVARCHAR(200) NULL,
    IsActive             BIT NOT NULL CONSTRAINT DF_CashRegisters_IsActive DEFAULT(1),
    CONSTRAINT UQ_CashRegisters UNIQUE(StoreID, RegisterCode),
    CONSTRAINT FK_CashRegisters_Store FOREIGN KEY (StoreID) REFERENCES core.Stores(StoreID)
);
GO

CREATE TABLE sales.CashSessions (
    CashSessionID        INT IDENTITY(1,1) PRIMARY KEY,
    CashRegisterID       INT NOT NULL,
    StoreID              INT NOT NULL,
    EmployeeID           INT NOT NULL,
    OpenedAt             DATETIME2 NOT NULL,
    ClosedAt             DATETIME2 NULL,
    OpeningAmount        DECIMAL(18,2) NOT NULL CONSTRAINT DF_CashSessions_OpeningAmount DEFAULT(0),
    ClosingAmount        DECIMAL(18,2) NULL,
    ExpectedAmount       DECIMAL(18,2) NULL,
    DifferenceAmount     DECIMAL(18,2) NULL,
    Status               NVARCHAR(30) NOT NULL CONSTRAINT DF_CashSessions_Status DEFAULT('OPEN'),
    Notes                NVARCHAR(500) NULL,
    CONSTRAINT FK_CashSessions_Register FOREIGN KEY (CashRegisterID) REFERENCES sales.CashRegisters(CashRegisterID),
    CONSTRAINT FK_CashSessions_Store FOREIGN KEY (StoreID) REFERENCES core.Stores(StoreID),
    CONSTRAINT FK_CashSessions_Employee FOREIGN KEY (EmployeeID) REFERENCES hr.Employees(EmployeeID)
);
GO

CREATE TABLE sales.Orders (
    OrderID              BIGINT IDENTITY(1,1) PRIMARY KEY,
    OrderNumber          NVARCHAR(30) NOT NULL UNIQUE,
    StoreID              INT NOT NULL,
    CashRegisterID       INT NULL,
    CashSessionID        INT NULL,
    CustomerID           INT NULL,
    EmployeeID           INT NULL,
    OrderType            NVARCHAR(30) NOT NULL CONSTRAINT DF_Orders_OrderType DEFAULT('POS'),
    OrderStatus          NVARCHAR(30) NOT NULL CONSTRAINT DF_Orders_OrderStatus DEFAULT('COMPLETED'),
    OrderSource          NVARCHAR(30) NOT NULL CONSTRAINT DF_Orders_OrderSource DEFAULT('WEB'),
    OrderDate            DATETIME2 NOT NULL,
    SubTotal             DECIMAL(18,2) NOT NULL CONSTRAINT DF_Orders_SubTotal DEFAULT(0),
    DiscountAmount       DECIMAL(18,2) NOT NULL CONSTRAINT DF_Orders_DiscountAmount DEFAULT(0),
    TaxAmount            DECIMAL(18,2) NOT NULL CONSTRAINT DF_Orders_TaxAmount DEFAULT(0),
    ShippingAmount       DECIMAL(18,2) NOT NULL CONSTRAINT DF_Orders_ShippingAmount DEFAULT(0),
    FinalAmount          DECIMAL(18,2) NOT NULL CONSTRAINT DF_Orders_FinalAmount DEFAULT(0),
    PaidAmount           DECIMAL(18,2) NOT NULL CONSTRAINT DF_Orders_PaidAmount DEFAULT(0),
    ChangeAmount         DECIMAL(18,2) NOT NULL CONSTRAINT DF_Orders_ChangeAmount DEFAULT(0),
    LoyaltyPointsEarned  INT NOT NULL CONSTRAINT DF_Orders_PointsEarned DEFAULT(0),
    LoyaltyPointsUsed    INT NOT NULL CONSTRAINT DF_Orders_PointsUsed DEFAULT(0),
    PromotionID          INT NULL,
    CouponID             INT NULL,
    Notes                NVARCHAR(1000) NULL,
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_Orders_CreatedAt DEFAULT(SYSDATETIME()),
    UpdatedAt            DATETIME2 NULL,
    CONSTRAINT FK_Orders_Store FOREIGN KEY (StoreID) REFERENCES core.Stores(StoreID),
    CONSTRAINT FK_Orders_Register FOREIGN KEY (CashRegisterID) REFERENCES sales.CashRegisters(CashRegisterID),
    CONSTRAINT FK_Orders_Session FOREIGN KEY (CashSessionID) REFERENCES sales.CashSessions(CashSessionID),
    CONSTRAINT FK_Orders_Customer FOREIGN KEY (CustomerID) REFERENCES crm.Customers(CustomerID),
    CONSTRAINT FK_Orders_Employee FOREIGN KEY (EmployeeID) REFERENCES hr.Employees(EmployeeID),
    CONSTRAINT FK_Orders_Promotion FOREIGN KEY (PromotionID) REFERENCES crm.Promotions(PromotionID),
    CONSTRAINT FK_Orders_Coupon FOREIGN KEY (CouponID) REFERENCES crm.Coupons(CouponID)
);
GO

CREATE TABLE sales.OrderItems (
    OrderItemID          BIGINT IDENTITY(1,1) PRIMARY KEY,
    OrderID              BIGINT NOT NULL,
    ProductID            INT NOT NULL,
    UnitID               INT NOT NULL,
    Quantity             DECIMAL(18,3) NOT NULL,
    UnitPrice            DECIMAL(18,2) NOT NULL,
    DiscountPercent      DECIMAL(5,2) NOT NULL CONSTRAINT DF_OrderItems_DiscountPercent DEFAULT(0),
    DiscountAmount       DECIMAL(18,2) NOT NULL CONSTRAINT DF_OrderItems_DiscountAmount DEFAULT(0),
    TaxPercent           DECIMAL(5,2) NOT NULL CONSTRAINT DF_OrderItems_TaxPercent DEFAULT(0),
    TaxAmount            DECIMAL(18,2) NOT NULL CONSTRAINT DF_OrderItems_TaxAmount DEFAULT(0),
    LineTotal            DECIMAL(18,2) NOT NULL CONSTRAINT DF_OrderItems_LineTotal DEFAULT(0),
    CostAtSale           DECIMAL(18,2) NULL,
    BatchNumber          NVARCHAR(50) NULL,
    ExpiryDate           DATE NULL,
    Notes                NVARCHAR(500) NULL,
    CONSTRAINT FK_OrderItems_Order FOREIGN KEY (OrderID) REFERENCES sales.Orders(OrderID),
    CONSTRAINT FK_OrderItems_Product FOREIGN KEY (ProductID) REFERENCES catalog.Products(ProductID),
    CONSTRAINT FK_OrderItems_Unit FOREIGN KEY (UnitID) REFERENCES catalog.Units(UnitID)
);
GO

CREATE TABLE sales.OrderPayments (
    OrderPaymentID       BIGINT IDENTITY(1,1) PRIMARY KEY,
    OrderID              BIGINT NOT NULL,
    PaymentMethodID      INT NOT NULL,
    Amount               DECIMAL(18,2) NOT NULL,
    PaidAt               DATETIME2 NOT NULL,
    TransactionRef       NVARCHAR(100) NULL,
    PaymentStatus        NVARCHAR(30) NOT NULL CONSTRAINT DF_OrderPayments_Status DEFAULT('SUCCESS'),
    Notes                NVARCHAR(500) NULL,
    CONSTRAINT FK_OrderPayments_Order FOREIGN KEY (OrderID) REFERENCES sales.Orders(OrderID),
    CONSTRAINT FK_OrderPayments_Method FOREIGN KEY (PaymentMethodID) REFERENCES sales.PaymentMethods(PaymentMethodID)
);
GO

CREATE TABLE sales.ReturnOrders (
    ReturnOrderID        BIGINT IDENTITY(1,1) PRIMARY KEY,
    ReturnNumber         NVARCHAR(30) NOT NULL UNIQUE,
    OriginalOrderID      BIGINT NOT NULL,
    StoreID              INT NOT NULL,
    CustomerID           INT NULL,
    EmployeeID           INT NULL,
    ReturnDate           DATETIME2 NOT NULL,
    Status               NVARCHAR(30) NOT NULL CONSTRAINT DF_ReturnOrders_Status DEFAULT('COMPLETED'),
    RefundAmount         DECIMAL(18,2) NOT NULL CONSTRAINT DF_ReturnOrders_RefundAmount DEFAULT(0),
    Notes                NVARCHAR(1000) NULL,
    CONSTRAINT FK_ReturnOrders_Order FOREIGN KEY (OriginalOrderID) REFERENCES sales.Orders(OrderID),
    CONSTRAINT FK_ReturnOrders_Store FOREIGN KEY (StoreID) REFERENCES core.Stores(StoreID),
    CONSTRAINT FK_ReturnOrders_Customer FOREIGN KEY (CustomerID) REFERENCES crm.Customers(CustomerID),
    CONSTRAINT FK_ReturnOrders_Employee FOREIGN KEY (EmployeeID) REFERENCES hr.Employees(EmployeeID)
);
GO

CREATE TABLE sales.ReturnOrderItems (
    ReturnOrderItemID    BIGINT IDENTITY(1,1) PRIMARY KEY,
    ReturnOrderID        BIGINT NOT NULL,
    OrderItemID          BIGINT NOT NULL,
    ProductID            INT NOT NULL,
    Quantity             DECIMAL(18,3) NOT NULL,
    RefundAmount         DECIMAL(18,2) NOT NULL,
    Reason               NVARCHAR(500) NULL,
    CONSTRAINT FK_ReturnOrderItems_ReturnOrder FOREIGN KEY (ReturnOrderID) REFERENCES sales.ReturnOrders(ReturnOrderID),
    CONSTRAINT FK_ReturnOrderItems_OrderItem FOREIGN KEY (OrderItemID) REFERENCES sales.OrderItems(OrderItemID),
    CONSTRAINT FK_ReturnOrderItems_Product FOREIGN KEY (ProductID) REFERENCES catalog.Products(ProductID)
);
GO

-- =========================================================
-- 10) AUDIT TABLES
-- =========================================================
CREATE TABLE audit.ActivityLogs (
    ActivityLogID        BIGINT IDENTITY(1,1) PRIMARY KEY,
    UserID               INT NULL,
    StoreID              INT NULL,
    ActionName           NVARCHAR(100) NOT NULL,
    EntityName           NVARCHAR(100) NULL,
    EntityID             NVARCHAR(100) NULL,
    IpAddress            NVARCHAR(50) NULL,
    UserAgent            NVARCHAR(500) NULL,
    Description          NVARCHAR(1000) NULL,
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_ActivityLogs_CreatedAt DEFAULT(SYSDATETIME()),
    CONSTRAINT FK_ActivityLogs_User FOREIGN KEY (UserID) REFERENCES core.Users(UserID),
    CONSTRAINT FK_ActivityLogs_Store FOREIGN KEY (StoreID) REFERENCES core.Stores(StoreID)
);
GO

CREATE TABLE audit.ErrorLogs (
    ErrorLogID           BIGINT IDENTITY(1,1) PRIMARY KEY,
    ErrorCode            NVARCHAR(100) NULL,
    ErrorMessage         NVARCHAR(2000) NOT NULL,
    StackTrace           NVARCHAR(MAX) NULL,
    SourceModule         NVARCHAR(200) NULL,
    UserID               INT NULL,
    StoreID              INT NULL,
    CreatedAt            DATETIME2 NOT NULL CONSTRAINT DF_ErrorLogs_CreatedAt DEFAULT(SYSDATETIME()),
    CONSTRAINT FK_ErrorLogs_User FOREIGN KEY (UserID) REFERENCES core.Users(UserID),
    CONSTRAINT FK_ErrorLogs_Store FOREIGN KEY (StoreID) REFERENCES core.Stores(StoreID)
);
GO

-- =========================================================
-- 11) INDEXES
-- =========================================================
CREATE INDEX IX_Products_ProductName ON catalog.Products(ProductName);
CREATE INDEX IX_Products_CategoryID ON catalog.Products(CategoryID);
CREATE INDEX IX_ProductPrices_ProductID_StoreID ON catalog.ProductPrices(ProductID, StoreID);
CREATE INDEX IX_StockBalances_Store_Warehouse_Product ON inventory.StockBalances(StoreID, WarehouseID, ProductID);
CREATE INDEX IX_StockMovements_ProductID_CreatedAt ON inventory.StockMovements(ProductID, CreatedAt);
CREATE INDEX IX_Customers_FullName ON crm.Customers(FullName);
CREATE INDEX IX_Customers_Phone ON crm.Customers(Phone);
CREATE INDEX IX_Orders_OrderDate ON sales.Orders(OrderDate);
CREATE INDEX IX_Orders_StoreID ON sales.Orders(StoreID);
CREATE INDEX IX_Orders_CustomerID ON sales.Orders(CustomerID);
CREATE INDEX IX_OrderItems_OrderID ON sales.OrderItems(OrderID);
CREATE INDEX IX_PO_OrderDate ON purchasing.PurchaseOrders(OrderDate);
CREATE INDEX IX_GoodsReceipts_ReceiptDate ON purchasing.GoodsReceipts(ReceiptDate);
CREATE INDEX IX_Employees_StoreID ON hr.Employees(StoreID);
GO

-- =========================================================
-- 12) CHECK CONSTRAINTS
-- =========================================================
ALTER TABLE catalog.Products
ADD CONSTRAINT CK_Products_CostPrice CHECK (CostPrice >= 0),
    CONSTRAINT CK_Products_SalePrice CHECK (SalePrice >= 0),
    CONSTRAINT CK_Products_MinStock CHECK (MinStock >= 0);

ALTER TABLE catalog.TaxRates
ADD CONSTRAINT CK_TaxRates_TaxPercent CHECK (TaxPercent >= 0 AND TaxPercent <= 100);

ALTER TABLE purchasing.PurchaseOrderItems
ADD CONSTRAINT CK_POItems_OrderedQty CHECK (OrderedQty > 0),
    CONSTRAINT CK_POItems_UnitPrice CHECK (UnitPrice >= 0);

ALTER TABLE purchasing.GoodsReceiptItems
ADD CONSTRAINT CK_GRItems_Quantity CHECK (Quantity > 0),
    CONSTRAINT CK_GRItems_UnitCost CHECK (UnitCost >= 0);

ALTER TABLE inventory.StockBalances
ADD CONSTRAINT CK_StockBalances_QOH CHECK (QuantityOnHand >= 0),
    CONSTRAINT CK_StockBalances_QR CHECK (QuantityReserved >= 0);

ALTER TABLE sales.OrderItems
ADD CONSTRAINT CK_OrderItems_Quantity CHECK (Quantity > 0),
    CONSTRAINT CK_OrderItems_UnitPrice CHECK (UnitPrice >= 0);

ALTER TABLE sales.OrderPayments
ADD CONSTRAINT CK_OrderPayments_Amount CHECK (Amount >= 0);

ALTER TABLE crm.Coupons
ADD CONSTRAINT CK_Coupons_UsedCount CHECK (UsedCount >= 0),
    CONSTRAINT CK_Coupons_UsageLimit CHECK (UsageLimit >= 0);

ALTER TABLE crm.Customers
ADD CONSTRAINT CK_Customers_LoyaltyPoints CHECK (LoyaltyPoints >= 0),
    CONSTRAINT CK_Customers_TotalSpent CHECK (TotalSpent >= 0);
GO

-- =========================================================
-- 13) FINISH
-- =========================================================
PRINT N'ConvenienceStoreDB schema created successfully.';
GO
-- core: cửa hàng, tài khoản, phân quyền, cấu hình
-- hr: nhân viên, ca làm
-- catalog: sản phẩm, ngành hàng, đơn vị tính, mã vạch, giá
-- purchasing: nhà cung cấp, phiếu nhập, đơn mua
-- inventory: kho, tồn kho, chuyển kho, kiểm kho
-- crm: khách hàng, điểm thưởng, khuyến mãi, coupon
-- sales: đơn hàng, chi tiết đơn, thanh toán, trả hàng
-- audit: log hoạt động, log lỗi