from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "pinkpenny_secret_key"

# Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="pinkpenny"
)

# Home Page
@app.route('/')
def hello():
    return render_template('index.html')


# About Page
@app.route('/about')
def about():
    return render_template('about.html')


# Contact Page
@app.route('/contact')
def contact():
    return render_template('contact.html')


# Login Page
@app.route('/user', methods=['GET', 'POST'])
def user():

    message = ""

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor()

        sql = """
        SELECT * FROM users
        WHERE email=%s AND password=%s
        """

        cursor.execute(sql, (email, password))

        user = cursor.fetchone()

        if user:

            session['user_id'] = user[0]
            session['fullname'] = user[1]

            return redirect('/finance')

        else:
            message = "Invalid Email or Password"

    return render_template(
        'user.html',
        message=message
    )

    
# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():

    message = ""

    if request.method == 'POST':

        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor()

        try:

            sql = """
            INSERT INTO users(fullname,email,password)
            VALUES (%s,%s,%s)
            """

            cursor.execute(
                sql,
                (fullname, email, password)
            )

            db.commit()

            return redirect('/user')

        except mysql.connector.Error:

            message = "Email already exists"

    return render_template(
        'register.html',
        message=message
    )


# Finance Analyzer Page
@app.route('/finance', methods=['GET', 'POST'])
def finance():

    if 'user_id' not in session:
     return redirect('/user')
    result = None

    if request.method == 'POST':

        income = float(request.form['income'])
        rent = float(request.form['rent'])
        food = float(request.form['food'])
        transport = float(request.form['transport'])
        shopping = float(request.form['shopping'])
        entertainment = float(request.form['entertainment'])
        other = float(request.form['other'])

        expenses = (
            rent + food + transport +
            shopping + entertainment + other
        )

        savings = income - expenses

        savings_rate = round((savings / income) * 100, 2)

        # SAVE TO DATABASE
        cursor = db.cursor()

        sql = """
        INSERT INTO finance_records
        (user_id, income, expenses, savings, savings_rate)
        VALUES (%s, %s, %s, %s, %s)
        """

        user_id = session['user_id']

        cursor.execute(
       sql,
    (
        user_id,
        income,
        expenses,
        savings,
        savings_rate
    )
)

        db.commit()

        result = {
            'income': income,
            'expenses': expenses,
            'savings': savings,
            'rate': savings_rate
        }

    return render_template(
        'finance.html',
        result=result
    )

    return render_template(
        'finance.html',
        result=result
    )

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/user')
@app.route('/history')
def history():

    if 'user_id' not in session:
        return redirect('/user')

    cursor = db.cursor(dictionary=True)

    sql = """
    SELECT *
    FROM finance_records
    WHERE user_id=%s
    ORDER BY created_at DESC
    """

    cursor.execute(
        sql,
        (session['user_id'],)
    )

    records = cursor.fetchall()

    return render_template(
        'history.html',
        records=records
    )

if __name__ == '__main__':
    app.run(debug=True)