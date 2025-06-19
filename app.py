from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    score = db.Column(db.Integer, default=0)

# Quiz model
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100), nullable=False)
    question = db.Column(db.String(255), nullable=False)
    option1 = db.Column(db.String(100), nullable=False)
    option2 = db.Column(db.String(100), nullable=False)
    option3 = db.Column(db.String(100), nullable=False)
    option4 = db.Column(db.String(100), nullable=False)
    correct_option = db.Column(db.String(100), nullable=False)  # 1, 2, 3, or 4

# Score model
class UserScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, default=0)

    # Ensure (user, topic) is unique
    __table_args__ = (db.UniqueConstraint('user_id', 'topic'),)


# ✅ User Authentication
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None  # Initialize error variable

    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        # Check if user already exists before trying to add
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error = "Account already exists"
            return render_template('register.html', error=error)

        try:
            new_user = User(username=username, password=password, score=0)
            db.session.add(new_user)
            db.session.commit()

            topics = db.session.query(Quiz.topic).distinct().all()
            for topic in topics:
                new_user_score = UserScore(user_id=new_user.id, topic=topic[0], score=None)
                db.session.add(new_user_score)

            db.session.commit()
            return redirect(url_for('login'))

        except IntegrityError:
            db.session.rollback()
            error = "Account already exists"

    return render_template('register.html', error=error)





@app.route('/unregister')
def unregister():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Find the user by session username
    user = User.query.filter_by(username=session['username']).first()

    if user:
        # Delete associated scores
        UserScore.query.filter_by(user_id=user.id).delete()

        # Delete the user
        db.session.delete(user)
        db.session.commit()

    # Clear session
    session.clear()

    # Redirect to welcome/home page
    return redirect(url_for('home'))




@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid username or password"
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    # Remove user_id from session if it exists
    session.pop('user_id', None)
    session.pop('username', None)
    return render_template('logout.html')

# ✅ User Dashboard (Score Tracking)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if not user:
        # User has been deleted
        session.pop('user_id', None)
        session.pop('username', None)
        return redirect(url_for('login'))

    score = user.score
    return render_template('dashboard.html', user=user, score=score)



# ✅ Quiz System
@app.route('/quiz/<topic>', methods=['GET', 'POST'])
def quiz(topic):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    questions = Quiz.query.filter_by(topic=topic).all()

    if request.method == 'POST':
        current_score = 0
        total = len(questions)

        for q in questions:
            selected_option = request.form.get(f'question_{q.id}')
            if selected_option and int(selected_option) == int(q.correct_option):
                current_score += 1

        user_score = UserScore.query.filter_by(user_id=user.id, topic=topic).first()
        previous_score = user_score.score if user_score else 0

        # If no entry, create one
        if not user_score:
            user_score = UserScore(user_id=user.id, topic=topic, score=current_score)
            db.session.add(user_score)
            diff = current_score  # Since previous score is 0
        else:
            diff = current_score - user_score.score
            if current_score > user_score.score:
                user_score.score = current_score
            else:
                diff = 0  # No change in total score

        if diff > 0:
            user.score += diff

        db.session.commit()

        return render_template(
            'quiz_result.html',
            previous_score=previous_score,
            current_score=current_score,
            total=total,
            user=user
        )

    return render_template('quiz.html', questions=questions, topic=topic)




# ✅ Keep Your Existing Routes (Unchanged)
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')




@app.route('/where-clause')
def where_clause():
    return render_template('./topics/where_clause.html', active_topic='where_clause')
@app.route('/crud')
def crud():
    return render_template('./topics/crud.html', active_topic='crud')
@app.route('/order-by')
def order_by():
    return render_template('./topics/order_by.html', active_topic='order_by')

@app.route('/group-by')
def group_by():
    return render_template('./topics/group_by.html', active_topic='group_by')

@app.route('/aggregate-functions')
def aggregate_functions():
    return render_template('./topics/aggregate_functions.html', active_topic='aggregate_functions')

@app.route('/data-constraints')
def data_constraints():
    return render_template('./topics/data_constraints.html', active_topic='data_constraints')

@app.route('/joining-data')
def joining_data():
    return render_template('./topics/joining_data.html', active_topic='joining_data')

@app.route('/functions')
def functions():
    return render_template('./topics/functions.html', active_topic='functions')


@app.route('/indexes')
def indexes():
    return render_template('./topics/indexes.html', active_topic='indexes')


@app.route('/display_score')
def user_score_display():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if not user:
        # User has been deleted
        session.pop('user_id', None)
        session.pop('username', None)
        return redirect(url_for('login'))

    score = user.score
    return render_template('user_score_display.html', user=user, score=score)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created within the app context
    app.run(debug=True)
