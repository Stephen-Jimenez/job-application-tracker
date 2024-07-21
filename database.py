import pymysql

class connect_to_database:
    def __init__(self):
        timeout = 10
        self.cnx = pymysql.connect(
            charset="utf8mb4",
            connect_timeout=timeout,
            cursorclass=pymysql.cursors.DictCursor,
            db="ApplicationTrackerApp",
            host="mysql-1e6432be-application-tracker.g.aivencloud.com",
            password="AVNS_GjZJg_kfi_7XHlZURGy",
            read_timeout=timeout,
            port=26554,
            user="avnadmin",
            write_timeout=timeout,
        )
        self.cursor = pymysql.cursors.Cursor(self.cnx) 
    
    def get_applicant_id(self, email):
        query = "SELECT GetApplicantId(%s)"
        args = []
        args.append(email)
        self.cursor.execute(query, args)
        applicant_id = self.cursor.fetchone()[0]
        return applicant_id
    
    def get_applicant_info(self, id):
        query = "SELECT Email, FirstName, LastName FROM Applicants WHERE Id = %s"
        args = [id]
        self.cursor.execute(query, args)
        record = self.cursor.fetchone()
        return record
    
    def add_applicant(self, first_name, last_name, email, password):
        self.cursor.callproc("AddApplicant", [first_name, last_name, email, password])
        self.cnx.commit()

    def check_password(self, email, password):
        from app import bcrypt
        query = "SELECT Id, Password FROM Applicants WHERE Email = %s"
        args = [email]   
        self.cursor.execute(query, args)
        record = self.cursor.fetchone()
        if not record:
            return None
        if bcrypt.check_password_hash(record[1], password):
            return record
        return None
    
    def add_application(self, applicant_id, position, company, application_date):
        self.cursor.callproc("AddApplication", [applicant_id, position, company, application_date])
        self.cnx.commit()

    def delete_application(self, application_id):
        query = "DELETE FROM Applications WHERE Id = %s"
        args = [application_id]
        self.cursor.execute(query, args)
        self.cnx.commit()

    def get_applications(self, applicant_id):
        self.cursor.callproc('GetAllApplications', [applicant_id])
        applications = self.cursor
        applications_list = []
        for application in applications:
            if len(application) == 6:
                application_dict = {}
                application_dict['id'] = application[0]
                application_dict["position"] = application[2]
                application_dict["company"] = application[3]
                application_dict["date"] = application[4]
                application_dict["rejection date"] = application[5]
                applications_list.append(application_dict)
        return applications_list
        
    def get_unrejected_applications(self, applicant_id):
        self.cursor.callproc('GetAllApplications', [applicant_id])
        applications = self.cursor
        applications_list = []
        for application in applications:
            if application[5] == None:
                application_dict = {}
                application_dict['id'] = application[0]
                application_dict["position"] = application[2]
                application_dict["company"] = application[3]
                application_dict["date"] = application[4]
                application_dict["rejection date"] = application[5]
                applications_list.append(application_dict)
        return applications_list
        
    def get_rejected_applications(self, applicant_id):
        self.cursor.callproc('GetAllApplications', [applicant_id])
        applications = self.cursor
        applications_list = []
        for application in applications:
            if application[5] != None:
                application_dict = {}
                application_dict['id'] = application[0]
                application_dict["position"] = application[2]
                application_dict["company"] = application[3]
                application_dict["date"] = application[4]
                application_dict["rejection date"] = application[5]
                applications_list.append(application_dict)
        return applications_list

    def get_interviews(self, application_id):
        self.cursor.callproc('GetInterviews', [application_id])
        interviews = self.cursor
        interviews_list = []
        for interview in interviews:
            relation_dict = {}
            relation_dict['interviewer'] = interview[1]
            relation_dict['interview_date'] = interview[2]
            interviews_list.append(relation_dict)
        return interviews_list
    
    def get_applicant_id_from_application_id(self, application_id):
        query = "SELECT Applicant FROM Applications WHERE Id = %s"
        args = [application_id]
        self.cursor.execute(query, args)
        record = self.cursor.fetchone()
        return record
    
    def add_interview(self, application_id, interviewer_name, interview_date):
        self.cursor.callproc("AddInterview", [application_id, interviewer_name, interview_date])
        self.cnx.commit()

    def add_rejection_date(self, application_id, rejection_date):
        self.cursor.callproc("AddRejectionDate", [application_id, rejection_date])
        self.cnx.commit()

    def close_connection(self):
        self.cursor.close()
        self.cnx.close()