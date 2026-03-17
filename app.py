from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "secret123"


# ---------- HOME PAGE ----------
@app.route("/")
def home():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM requests ORDER BY id DESC")
    requests = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        requests=requests
    )

# ---------- REGISTER DONOR ----------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        blood = request.form["blood"]
        city = request.form["city"]
        phone = request.form["phone"]
        last_donation = request.form["last_donation"]
        available = request.form["available"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO donors (name, blood_group, city, phone, last_donation, available)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (name, blood, city, phone, last_donation, available))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")


# ---------- SEARCH DONOR ----------
@app.route("/search", methods=["GET", "POST"])
def search():

    donors = []

    if request.method == "POST":

        blood = request.form["blood"]
        city = request.form["city"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM donors
        WHERE blood_group=? AND city=? AND available='yes'
        """, (blood, city))

        data = cursor.fetchall()

        conn.close()

        donors = []

        for d in data:

            last_date = d[5]

            try:
                last = datetime.strptime(last_date, "%Y-%m-%d")
                next_date = last + timedelta(days=90)

                if datetime.now() >= next_date:
                    status = "Eligible"
                else:
                    status = "Not Eligible"

            except:
                status = "Eligible"

            donors.append(d + (status,))


    return render_template("search.html", donors=donors)

# ---------- ADMIN DASHBOARD ----------
@app.route("/admin")
def admin():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM donors")
    donors = cursor.fetchall()

    cursor.execute("SELECT * FROM requests")
    requests = cursor.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        donors=donors,
        requests=requests
    )
# ---------- DELETE DONOR ---------@app.route("/admin")
def admin():

    if "role" not in session or session["role"] != "admin":
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM donors")
    donors = cursor.fetchall()

    cursor.execute("SELECT * FROM requests")
    requests = cursor.fetchall()

    cursor.execute("SELECT * FROM donations")
    donations = cursor.fetchall()


    conn.close()

    return render_template(
    "admin.html",
    donors=donors,
    requests=requests,
    donations=donations
)
@app.route("/delete_donor/<int:id>")
def delete_donor(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM donors WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/admin")
# ---------- DELETE REQUEST ----------
@app.route("/delete_request/<int:id>")
def delete_request(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM requests WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/admin")
# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session["user"] = username
            session["role"] = user[3]

            if user[3] == "admin":
                return redirect("/admin")
            else:
                return redirect("/")

        else:
            return "Invalid login"

    return render_template("login.html")
# ---------- LOGOUT ----------
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")
# ---------- ADD DONATION ----------
@app.route("/add_donation", methods=["GET", "POST"])
def add_donation():

    if request.method == "POST":

        donor_name = request.form["name"]
        blood = request.form["blood"]
        hospital = request.form["hospital"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO donations
        (donor_name, blood_group, date, hospital)
        VALUES (?, ?, date('now'), ?)
        """, (donor_name, blood, hospital))

        conn.commit()
        conn.close()

        return redirect("/admin")

    return render_template("add_donation.html")
@app.route("/request", methods=["GET", "POST"])
def request_blood():

    if request.method == "POST":

        name = request.form["name"]
        blood = request.form["blood"]
        city = request.form["city"]
        contact = request.form["contact"]
        emergency = request.form["emergency"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO requests
        (name, blood_group, city, contact, emergency, date)
        VALUES (?, ?, ?, ?, ?, date('now'))
        """, (name, blood, city, contact, emergency))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("request.html")
# ---------- RUN SERVER ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)