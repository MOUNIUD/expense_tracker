from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Create DB table
def init_db():
    conn = sqlite3.connect('database/expenses.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category']
        amount = request.form['amount']
        description = request.form['description']

        conn = sqlite3.connect('database/expenses.db')
        c = conn.cursor()
        c.execute("INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
                  (date, category, amount, description))
        conn.commit()
        conn.close()

        return redirect('/view')
    return render_template('add_expense.html')

@app.route('/view')
def view_expenses():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    conn = sqlite3.connect('database/expenses.db')
    c = conn.cursor()

    if start_date and end_date:
        c.execute("SELECT * FROM expenses WHERE date BETWEEN ? AND ?", (start_date, end_date))
    else:
        c.execute("SELECT * FROM expenses")

    expenses = c.fetchall()
    conn.close()
    return render_template('view_expenses.html', expenses=expenses)

@app.route('/delete/<int:id>')
def delete_expense(id):
    conn = sqlite3.connect('database/expenses.db')
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/view')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    conn = sqlite3.connect('database/expenses.db')
    c = conn.cursor()

    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category']
        amount = request.form['amount']
        description = request.form['description']

        c.execute('''
            UPDATE expenses
            SET date = ?, category = ?, amount = ?, description = ?
            WHERE id = ?
        ''', (date, category, amount, description, id))

        conn.commit()
        conn.close()
        return redirect('/view')

    c.execute("SELECT * FROM expenses WHERE id = ?", (id,))
    expense = c.fetchone()
    conn.close()
    return render_template('edit_expense.html', expense=expense)

@app.route('/summary')
def summary():
    conn = sqlite3.connect('database/expenses.db')
    c = conn.cursor()
    c.execute('SELECT category, SUM(amount) FROM expenses GROUP BY category')
    data = c.fetchall()
    conn.close()

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    return render_template('summary.html', categories=categories, amounts=amounts)
@app.route('/monthly')
def monthly_summary():
    conn = sqlite3.connect('database/expenses.db')
    c = conn.cursor()
    c.execute("""
        SELECT strftime('%Y-%m', date) AS month, SUM(amount)
        FROM expenses GROUP BY month ORDER BY month
    """)
    data = c.fetchall()
    conn.close()

    months = [row[0] for row in data]
    totals = [row[1] for row in data]

    return render_template('monthly.html', months=months, totals=totals)

@app.route('/clear_all', methods=['POST'])
def clear_all():
    conn = sqlite3.connect('database/expenses.db')
    c = conn.cursor()
    c.execute("DELETE FROM expenses")
    conn.commit()
    conn.close()
    return redirect('/view')



@app.route('/test')
def test():
    return render_template('test_summary.html')

init_db()  # Initialize DB before app runs, both locally and on Render

if __name__ == '__main__':
    app.run(debug=True)
