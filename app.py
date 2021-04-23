from flask import Flask, request, jsonify
import add

app = Flask(__name__)


@app.route('/create_user', methods=["POST"])
def create_user():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        add.reg_user(user_id, fname, lname)
        return "ok"


@app.route('/subs_categ', methods=["POST"])
def subs_categ():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        category = request.form.get('category')
        rus_category = request.form.get('rus_category')
        return jsonify({"answer": add.edit_categ(user_id, category, rus_category)})


@app.route('/get_news/<user_id>')
def get_news(user_id):
    news = add.get_news(user_id)
    return jsonify(news)


@app.route('/get_keynews/<user_id>')
def get_keynews(user_id):
    news = add.get_keynews(user_id)
    return jsonify(news)


@app.route('/select_categ/<user_id>')
def select_categ(user_id):
    cats = add.select_req(user_id)
    categories = {
        "business": cats[1],
        "entertainment": cats[2],
        "health": cats[3],
        "science": cats[4],
        "sports": cats[5],
        "technology": cats[6],
        "general": cats[7],
    }
    return jsonify(categories)


@app.route('/subs_keywords', methods=["POST"])
def subs_keywords():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        keywords = request.form.get('keywords')
        print(user_id, keywords)
        return jsonify({"status": add.del_or_add_keyword(user_id, keywords)})


@app.route('/get_keywords/<user_id>')
def get_keywords(user_id):
    return jsonify({"keywords": add.select_keywords(user_id)})


if __name__ == '__main__':
    add.create_database()
    app.run()
