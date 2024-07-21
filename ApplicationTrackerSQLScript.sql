DROP DATABASE IF EXISTS ApplicationTrackerApp;
CREATE DATABASE ApplicationTrackerApp;
USE ApplicationTrackerApp;

DROP TABLE IF EXISTS Applicants;
CREATE TABLE Applicants (
Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
Email VARCHAR(50) NOT NULL,
FirstName VARCHAR(50) NOT NULL,
LastName VARCHAR(50) NOT NULL,
Password VARCHAR(100) NOT NULL,
UNIQUE (Email)
);

DROP TABLE IF EXISTS Companies;
CREATE TABLE Companies(
CompanyName VARCHAR(100) NOT NULL PRIMARY KEY
);

DROP TABLE IF EXISTS Positions;
CREATE TABLE Positions(
PositionName VARCHAR(100) NOT NULL PRIMARY KEY
);

DROP TABLE IF EXISTS Applications;
CREATE TABLE Applications(
Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
Applicant INT NOT NULL,
Position VARCHAR(100) NOT NULL,
Company VARCHAR(100) NOT NULL,
DateOfApplication DATE NOT NULL,
DateOfRejection DATE,
FOREIGN KEY (Applicant) REFERENCES Applicants (Id),
FOREIGN KEY (Company) REFERENCES Companies (CompanyName),
FOREIGN KEY (Position) REFERENCES Positions (PositionName)
);

DROP TABLE IF EXISTS Interviews;
CREATE TABLE Interviews(
Application INT NOT NULL,
Interviewer VARCHAR(100) NOT NULL,
DateofInterview DATE NOT NULL,
PRIMARY KEY (Application, Interviewer, DateOfInterview),
FOREIGN KEY (Application) REFERENCES Applications (Id) ON DELETE CASCADE
);

DROP FUNCTION IF EXISTS GetApplicantId;
DELIMITER $$
CREATE FUNCTION GetApplicantId(ParamEmail VARCHAR(50))
RETURNS INT DETERMINISTIC
BEGIN
DECLARE ApplicantId INT;
SELECT Id INTO ApplicantId FROM Applicants 
WHERE Email = ParamEmail;
IF ApplicantId IS NULL THEN RETURN 0;
END IF;
RETURN ApplicantId;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS AddApplicant;
DELIMITER $$
CREATE PROCEDURE AddApplicant(
ParamFirstName VARCHAR(50),
ParamLastName VARCHAR(50),
ParamEmail VARCHAR(50),
ParamPassword VARCHAR(100)
)
BEGIN
DECLARE ApplicantIdCheck INT;
SELECT GetApplicantId(ParamEmail) INTO ApplicantIdCheck;
IF ApplicantIdCheck = 0 THEN 
INSERT INTO Applicants (FirstName, LastName, Email, Password) VALUES (ParamFirstName, ParamLastName, ParamEmail, ParamPassword);
END IF;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS AddCompany;
DELIMITER $$
CREATE PROCEDURE AddCompany(ParamCompanyName VARCHAR(100))
BEGIN
DECLARE CompanyCheck VARCHAR(100);
SELECT CompanyName INTO CompanyCheck
From Companies WHERE CompanyName = ParamCompanyName;
IF CompanyCheck IS NULL THEN
INSERT INTO Companies (CompanyName) VALUES (ParamCompanyName);
END IF;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS AddPosition;
DELIMITER $$
CREATE PROCEDURE AddPosition(ParamPositionName VARCHAR(100))
BEGIN
DECLARE PositionCheck VARCHAR(100);
SELECT PositionName INTO PositionCheck
FROM Positions WHERE PositionName = ParamPositionName;
IF PositionCheck IS NULL THEN
INSERT INTO Positions (PositionName) VALUES (ParamPositionName);
END IF;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS AddApplication;
DELIMITER $$
CREATE PROCEDURE AddApplication(
ParamApplicantId INT,
ParamPositionName VARCHAR(100),
ParamCompanyName VARCHAR(100),
ParamDateOfApplication DATE
)
BEGIN
CALL AddPosition(ParamPositionName);
CALL AddCompany(ParamCompanyName);
INSERT INTO Applications (Applicant, Position, Company, DateOfApplication)
VALUES (ParamApplicantId, ParamPositionName, ParamCompanyName, ParamDateOfApplication);
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS GetAllApplications;
DELIMITER $$
CREATE PROCEDURE GetAllApplications(ParamApplicantId INT)
BEGIN
SELECT * FROM Applications WHERE Applicant = ParamApplicantId;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS AddInterview;
DELIMITER $$
CREATE PROCEDURE AddInterview(ParamApplicationId INT, ParamInterviewer VARCHAR(100), ParamDateOfInterview DATE)
BEGIN
INSERT INTO Interviews (Application, Interviewer, DateOfInterview)
VALUES (ParamApplicationId, ParamInterviewer, ParamDateOfInterview);
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS GetInterviews;
DELIMITER $$
CREATE PROCEDURE GetInterviews(ParamApplicationId INT)
BEGIN
SELECT * FROM Interviews WHERE Application = ParamApplicationId;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS AddRejectionDate;
DELIMITER $$
CREATE PROCEDURE AddRejectionDate(ParamApplicationId INT, ParamRejectionDate DATE)
BEGIN
UPDATE Applications SET DateOfRejection = ParamRejectionDate WHERE Id = ParamApplicationId;
END $$
DELIMITER ;
