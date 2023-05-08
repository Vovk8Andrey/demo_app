from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db' # включаем нужную бд, могут быть разные MySQL, Postgres  т.д.
db = SQLAlchemy(app) # при помощи класса SQLAlchemy создаем объект бд и передаем туда объект который создан на основе класса Flask


class Article(db.Model): # наследуем все от db.Model
    id = db.Column(db.Integer, primary_key=True) # уникальное поле id при помощи primary_key
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id  # когда будем выбирать объект на основе этого класса, то у нас будет выдаваться сам этот объект и еще его id



#отслеживаем URL-адрес и предоставляем определнную инфо-ю
# если пользователь на главной странице, то выводим "Hello", если на странице about, то пишем "страничка про нас"

#делаем декоратор для  отслеживания url-адреса. (Какой url отслеживаем -> указываем в кавычках)
@app.route('/')
@app.route('/home')
def index():
    return render_template("index.html")     #импортируем из фласка эту функцию, для обработки html документов


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/posts')
def posts(): # получаем записи из бд и дальше передавай этот объект в сам шаблон
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template("posts.html", articles=articles) # в этом шаблоне получаем доступ по полю articles(можем называть как угодно, но для удобнства назвали articles)


@app.route('/posts/<int:id>')
def post_detail(id):
    article = Article.query.get(id)
    return render_template("post_detail.html", article=article)


@app.route('/posts/<int:id>/delete')
def post_delete(id):
    article = Article.query.get_or_404(id)

    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except:
        return "При удалении статьи произошла ошибка"


@app.route('/posts/<int:id>/update', methods=['POST', 'GET'])
def post_update(id):
    article = Article.query.get(id)  # нужно отобразить саму форму и в форме отобразить все те данные, что есть у существуюшей статьи
    if request.method == "POST":
        article.title = request.form["title"]    # достали данные в article и просто меняем те значения, что у нас в формочке
        article.intro = request.form["intro"]
        article.text = request.form["text"]

        try:
            db.session.commit()             # session.add мы убрали, так как нам ничего не нужно добавлять
            return redirect('/posts')
        except:
            return "При редактировании статьи произошла ошибка"
    else:

        return render_template("post_update.html", article=article)


@app.route('/create-article', methods=['POST', 'GET'])
def create_article():
    if request.method == "POST":
        title = request.form["title"]                     # создаем переменные, полученные из формочки(то, что в html)
        intro = request.form["intro"]
        text = request.form["text"]

        article = Article(title=title, intro=intro, text=text)     # Полученные данные нужно сохранить в оюъект класса Article объект, который потом нужно будет сохранять в бд
        try:
            db.session.add(article)                           # отлавливаем ошибки и сохраняем все в бд. add - добавляет данные
            db.session.commit()                               # сохраняем внесенные данные
            return redirect('/posts')                              # Если успешное добавление статьи, то перенаправляем пользователя на главную страницу
        except:
            return "При добавлении статьи произошла ошибка"
    else:
        return render_template("create_article.html")

# @app.route('/user/<string:name>/<int:id>')      # если нужно указывать определенные значения, они записываются в кавычках и с типом данных
# def user(name, id):
#     return "User page: " + name + " - " + str(id)


# прежде чем будем запускать весь проект, нужно написать еще одно условие
# проверка: если мы запускаем весь проект через app.py, то мы должны запускать как фласк приложение
if __name__ == "__main__":
    app.run(debug=True) #запускаем локальный сервер(сам наш проект). Debug=True - параметр для вывода ошибок вывода на сайте. Когда закидываем на сервер, то меняем на False



