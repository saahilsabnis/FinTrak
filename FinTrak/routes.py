from flask import render_template, request, session, url_for, flash, jsonify, redirect, request
from FinTrak import app, db, bcrypt
from FinTrak.forms import RegistrationForm, LoginForm, UpdateAccountForm, BudgetForm
from FinTrak.models import User, Expenses, Categories, Budgets
from flask_login import login_user, current_user, login_required, logout_user
from sqlalchemy import desc, extract, func
from datetime import datetime
import datetime as dt

@app.route("/")
def home():
    lastfive = []
    weeklabels = []
    monthlabels = []
    weekdata = []
    monthdata = []
    catlabels = []
    catdata = []
    weekcard = 0
    monthcard = 0
    yearcard = 0
    yeartotal = 0

    now = datetime.today()
    weekago = now - dt.timedelta(days = 7)
    monthago = now  #use only month for extracting the data

    if current_user.is_authenticated:

        lastfive = Expenses.query.filter_by(user_id = current_user.id).order_by(desc(Expenses.date)).limit(5).all()
        categories = Categories.query.filter_by(user_id = current_user.id).all()

        startw = weekago
        endw = now
        for x in range(5):
            lastweek = Expenses.query.filter_by(user_id = current_user.id).filter(Expenses.date >= startw, Expenses.date <= endw).all()
            weekdata.insert(0, sum(item.amount for item in lastweek))
            weeklabels.insert(0, startw.strftime('%d/%m')+"-"+endw.strftime('%d/%m'))
            endw, startw = startw, startw - dt.timedelta(days = 7)

        
        for x in range(5):
            lastmonth = Expenses.query.filter_by(user_id = current_user.id).filter(extract('month', Expenses.date) == monthago.month).all()
            monthlabels.insert(0, monthago.strftime("%b"))
            monthdata.insert(0, sum(item.amount for item in lastmonth))
            monthago = monthago - dt.timedelta(days= 32)

        exps = Expenses.query.filter_by(user_id = current_user.id).all()
        for x in categories:
            catlabels.append(str(x))
            catdata.append(sum(item.amount for item in exps if item.category == str(x)))

        userbudget = Budgets.query.filter_by(user_id = current_user.id).all()
        yeardata = Expenses.query.filter_by(user_id = current_user.id).filter(extract('year', Expenses.date) == now.year).all()
        weekcard = [weekdata[-1],float(userbudget[0].weeklybudget),"{:.2f}".format(weekdata[-1]*100/float(userbudget[0].weeklybudget))]
        monthcard = [monthdata[-1],float(userbudget[0].monthlybudget),"{:.2f}".format(monthdata[-1]*100/float(userbudget[0].monthlybudget))]
        for x in yeardata:
            yeartotal+= x.amount
        yearcard = [yeartotal, float(userbudget[0].yearlybudget), "{:.2f}".format(yeartotal*100/float(userbudget[0].yearlybudget))]


    return render_template("home.html", title = "Home", lastfive = lastfive, weeklabels = weeklabels, weekdata = weekdata, monthlabels = monthlabels, 
                            monthdata = monthdata, catlabels = catlabels, catdata = catdata, weekcard = weekcard, monthcard = monthcard, yearcard = yearcard)

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        budgetdefault = Budgets(weeklybudget = 0, monthlybudget = 0, yearlybudget = 0, user_id = int(current_user.id))
        db.session.add(user, budgetdefault)
        db.session.commit()
        flash(f"Your account is created!", 'success')
        return redirect(url_for("login"))
    return render_template("register.html", title = "Register", form = form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            flash("Logged in.", "success")
            next = request.args.get("next")
            return redirect(next) if next else redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check your credentials and try again.", "danger") 
    return render_template("login.html", title = "Login", form = form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for("static", filename = "profile_pics/" + current_user.image_file)
    return render_template("account.html", title = "My Account", image_file = image_file, form = form)    


@app.route("/addexpense", methods=["GET", "POST"])
@login_required
def addexpense():
    from FinTrak.forms import AddExpense
    form = AddExpense()
    if form.validate_on_submit():
        expense = Expenses(description = form.description.data, category = str(form.category.data), amount = int(form.amount.data),
                  date = form.date.data, paidby = form.paidby.data, user_id = int(current_user.id))
        db.session.add(expense)
        db.session.commit()
        flash("Expense Added!", 'success')
        return redirect(url_for('home'))
    return render_template("addexpense.html", title = "Add Expense", form = form)


@app.route("/category/addcategory", methods = ["GET","POST"])
@login_required
def addcategory():
    from FinTrak.forms import CategoryAdd
    form = CategoryAdd()
    if form.validate_on_submit():
        catinput = Categories(name = str(form.name.data), user_id = int(current_user.id))
        db.session.add(catinput)
        db.session.commit()
        flash("Category added!", "success")
        return redirect(url_for("home"))
    return render_template("addcategory.html", title = "Category Manager", form = form)    

@app.route("/category/removecategory", methods = ["GET", "POST"])
@login_required
def removecategory():
    from FinTrak.forms import CategoryRemove
    form = CategoryRemove()
    if form.validate_on_submit():
        delete = Categories.query.filter_by(name = str(form.name.data)).first()
        db.session.delete(delete)
        db.session.commit()
        flash("Category removed!", "success")
        return redirect(url_for("home"))
    return render_template("removecategory.html", title = "Category Manager", form = form)


@app.route("/expenses", methods = ["GET", "POST"])
@login_required
def expenses():
    history = Expenses.query.filter_by(user_id = current_user.id).order_by(Expenses.date).all()
    return render_template("expenses.html", title = "Expenses", history = history)


@app.route("/budgets", methods = ["GET", "POST"])
@login_required
def budgets():
    form = BudgetForm()
    
    now = datetime.today()
    userbudget = Budgets.query.filter_by(user_id = current_user.id).all()
    weekcard = float(userbudget[0].weeklybudget)
    monthcard = float(userbudget[0].monthlybudget)
    yearcard = float(userbudget[0].yearlybudget)
    if form.validate_on_submit():
        budgetupdate = Budgets.query.filter_by(user_id = current_user.id).first()
        budgetupdate.weeklybudget = form.weeklybudget.data
        budgetupdate.monthlybudget = form.monthlybudget.data
        budgetupdate.yearlybudget = form.yearlybudget.data
        db.session.commit()
        flash("Budgets Updated!", "success")
        return redirect(url_for("home"))
    return render_template("budgets.html", title = "Budgets", form = form, weekcard = weekcard, monthcard = monthcard, yearcard = yearcard)