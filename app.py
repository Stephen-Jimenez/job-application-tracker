from flask import Flask, g, redirect, render_template, request, session, url_for
from flask_bcrypt import Bcrypt
from database import connect_to_database

app = Flask(__name__)
app.secret_key = "XXXXX"
bcrypt = Bcrypt(app)

@app.before_request
def before_request():
    if "applicant_id" in session:
        cnx = connect_to_database()
        record = cnx.get_applicant_info(session["applicant_id"])
        if record:
            g.applicant_id = session["applicant_id"]
            g.email = record[0]
            g.first_name = record[1]
            g.last_name = record[2]
        cnx.close_connection()


@app.route("/")
def login_register():
    return render_template("index.html")

@app.route("/register_user", methods = ["GET", "POST"])
def register_user():
    if request.method == "POST":
        error = None
        email = request.form["email"]
        cnx = connect_to_database()
        if cnx.get_applicant_id(email) != 0:
            error = "A user with this email address already exists."
            cnx.close_connection()
            return render_template("index.html", error = error)
        else:
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            password = request.form["password"]
            password_confirm = request.form["password_confirm"]
            if password != password_confirm:
                error = "Passwords do not match."
                cnx.close_connection()
                return render_template("index.html", error = error)
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            cnx.add_applicant(first_name, last_name, email, hashed_password)
            cnx.close_connection()
            error = "User added. Please log in."
            return render_template("index.html", error = error)
    return redirect("/")
            
@app.route("/login", methods=["GET", "POST"])
def log_in():
    if request.method == "POST":
        session.pop("applicant_id", None)
        email = request.form["email"]
        password = request.form["password"]
        cnx = connect_to_database()
        record = cnx.check_password(email, password)
        if record:
            applicant_id = record[0]
            session["applicant_id"] = applicant_id
            cnx.close_connection()
            return redirect(url_for('render_home'))
        cnx.close_connection()
        login_error = "There was a problem logging in. Please check your credentials and try again."
        return render_template("index.html", login_error = login_error)
    return redirect("/")

@app.route("/logout")
def log_out():
    session.pop("applicant_id", None)
    return redirect(url_for("login_register"))

@app.route("/home")
def render_home():
    if "applicant_id" not in session:
        return redirect("/")
    return render_template("home.html")
    

@app.route("/add_application", methods=["GET", "POST"])
def add_application():
    if request.method == "POST":
        applicant_id = request.form["applicant_id"]
        position = request.form["position"]
        company = request.form["company"]
        application_date = request.form["application_date"]
        print(f"applicant_id: {applicant_id}")
        print(f"position: {position}")
        print(f"company: {company}")
        print(f"application_date: {application_date}")
        cnx = connect_to_database()
        cnx.add_application(applicant_id, position, company, application_date)
        cnx.close_connection()
        return redirect(url_for('get_applications'))
    return redirect(url_for('render_home'))

@app.route("/delete_application/<application_id>")
def delete_application(application_id):
    if "applicant_id" in session:
        applicant_id = session["applicant_id"]
        cnx = connect_to_database()
        return_tuple = cnx.get_applicant_id_from_application_id(application_id)
        test_id = return_tuple[0]
        if test_id == applicant_id:
            cnx.delete_application(application_id)
            cnx.close_connection()
            return redirect(url_for('get_applications'))
        cnx.close_connection()
        return redirect(url_for('render_home'))
    return redirect("/")

@app.route("/get_applications", methods=["GET", "POST"])
def get_applications():
    if "applicant_id" in session:
        applicant_id = session["applicant_id"]
        cnx = connect_to_database()
        applications = cnx.get_applications(applicant_id)
        cnx.close_connection()
        return render_template("applications.html", applications = applications)
    return redirect("/")

@app.route("/get_unrejected_applications", methods=["GET", "POST"])
def get_unrejected_applications():
    if "applicant_id" in session:
        applicant_id = session["applicant_id"]
        cnx = connect_to_database()
        applications = cnx.get_unrejected_applications(applicant_id)
        cnx.close_connection()
        return render_template("applications.html", applications = applications)
    return redirect("/")

@app.route("/get_rejected_applications", methods=["GET", "POST"])
def get_rejected_applications():
    if "applicant_id" in session:
        applicant_id = session["applicant_id"]
        cnx = connect_to_database()
        applications = cnx.get_rejected_applications(applicant_id)
        cnx.close_connection()
        return render_template("applications.html", applications = applications)
    return redirect("/")


@app.route("/add_interview/<application_id>")
def add_interview(application_id):
    if "applicant_id" in session:
        applicant_id = session["applicant_id"]
        cnx = connect_to_database()
        return_tuple = cnx.get_applicant_id_from_application_id(application_id)
        cnx.close_connection()
        test_id = return_tuple[0]
        if test_id == applicant_id:
            return render_template("add_interview.html", application_id = application_id)
        return redirect(url_for('render_home'))
    return redirect("/")   

@app.route("/add_interview_to_database", methods=["GET", "POST"])
def add_interview_to_database():
    if "applicant_id" in session:
        if request.method == "POST":
            application_id = request.form["application_id"]
            interviewer_name = request.form["interviewer_name"]
            interview_date = request.form["interview_date"]
            cnx = connect_to_database()
            cnx.add_interview(application_id, interviewer_name, interview_date)
            cnx.close_connection()
            return redirect(url_for('get_applications'))
        return redirect(url_for('render_home'))
    return redirect("/")

@app.route("/view_interviews/<application_id>")
def view_interviews(application_id):
    if "applicant_id" in session:
        cnx = connect_to_database()
        interviews = cnx.get_interviews(application_id)
        return render_template("render_interviews.html", interviews = interviews)
    return redirect("/")
    
@app.route("/add_rejection_date/<application_id>")
def add_rejection_date(application_id):
    if "applicant_id" in session:
        applicant_id = session["applicant_id"]
        cnx = connect_to_database()
        return_tuple = cnx.get_applicant_id_from_application_id(application_id)
        cnx.close_connection()
        test_id = return_tuple[0]
        if test_id == applicant_id:
            return render_template("add_rejection_date.html", application_id = application_id)
        return redirect(url_for('render_home'))
    return redirect("/")

@app.route("/add_rejection_date_to_database", methods=["GET", "POST"])
def add_rejection_date_to_database():
    if "applicant_id" in session:
        if request.method == "POST":
            application_id = request.form["application_id"]
            rejection_date = request.form["rejection_date"]
            cnx = connect_to_database()
            cnx.add_rejection_date(application_id, rejection_date)
            cnx.close_connection()
            return redirect(url_for('get_applications'))
        return redirect(url_for('render_home'))
    return redirect("/")


if __name__ == "__main__":
    app.run()