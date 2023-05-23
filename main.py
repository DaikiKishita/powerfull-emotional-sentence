from asari.api import Sonar
from flask import Flask,render_template,request,Blueprint
from flask_sqlalchemy import SQLAlchemy
import testapp
import time

app=Flask(__name__)
app.config.from_object("testapp.config")
db=SQLAlchemy(app)
#results=Blueprint("templates",__name__)


class Words(db.Model):
    __tablename__="Words"
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    word=db.Column(db.String(255),nullable=False,unique=True)
    Positiver=db.Column(db.Float,nullable=False)

with app.app_context():
    db.create_all()

def insert_words_to_DB(word,percent):
    if word!="":
        insert_word=Words(
            word=word,
            Positiver=percent,     
        )
        try:
            db.session.add(insert_word)
            db.session.commit()
        except:
            print("=======================")
            print("        ERROR          ")
            print("=======================")
            print(" 一意制約に違反しました ")
            print("\n      {}       \n".format(word))

def text_mining(word):
    sonar=Sonar()
    words=[word]
    sonar_list=list(map(sonar.ping,words))
    return sonar_list[0]["classes"][1]["confidence"]

@app.route("/",methods=["GET","POST"])
def index():
    if request.method=="POST":
        word1=request.form["word1"]
        word2=request.form["word2"]
        s=int(request.form["s"])
        e=int(request.form["e"])
        WP1=round(text_mining(word1),2)*100
        WP2=round(text_mining(word2),2)*100

        insert_words_to_DB(word1,WP1,)
        time.sleep(1)
        insert_words_to_DB(word2,WP2,)
        if word1=="" and word2=="":
            return render_template("index.html",result_text="入力なし")
        if s>e or s<0:
            return render_template("index.html",result_text="しっかりと範囲を決めてください")
        
        if s<=WP1<=e and s<=WP2<=e:
            if WP1> WP2:
                win="player1 WIN!!!!"
            elif WP1< WP2:
                win ="player2 WIN!!!!"
            else:
                win="同点!!!!!!!!"
            return render_template("index.html",result_text="結果表示",result1=f'{WP1}%',result2=f'{WP2}%',result_win=win)
        elif not(s<=WP1<=e) and s<=WP2<=e:
            return render_template("index.html",result_text="結果発表",result1="不戦敗",result2=f'{WP2}%',result_win="player2 win!!!!!")
        elif s<=WP1<=e and not(s<=WP2<=e):
            return render_template("index.html",result_text="結果発表",result1=f'{WP1}%',result2="不戦敗",result_win="player1 win!!!!!")
        else:
            return render_template("index.html",result_text="結果発表",result1="不戦敗",result2="不戦敗",result_win="勝負つかず")
    else:
        return render_template("index.html")

@app.route("/result")
def show_tables():
    word_result=[]
    posi_result=[]
    all_records = Words.query.all()
    if all_records==[]:
        return render_template("result.html",OK="False")
    else:
        for i in all_records:
            word_result.append(i.word)
            posi_result.append(i.Positiver)
        return render_template("result.html",resultss=zip(word_result,posi_result),OK="True")

@app.route("/result/search_DB",methods=["GET","POST"])
def action():
    if request.method=="POST":
        search_word=request.form["search"]
        search_type=request.form["search_type"]
        if search_type=="perfect_search":
            search_DB=Words.query.filter_by(word=search_word).first()
            if search_DB==None:
                return render_template("search.html",search_OK="0")
            else:
                a=[search_DB.word]
                b=[search_DB.Positiver]
                return render_template("search.html",actions=zip(a,b),search_OK="1")
        elif search_type=="part_search":
            search_DB=Words.query.filter(Words.word.like("%"+search_word+"%")).all()
            if search_DB==[]:
                return render_template("search.html",search_OK="0")
            else:
                a=[]
                b=[]
                for i in search_DB:
                    a.append(i.word)
                    b.append(i.Positiver)
                return render_template("search.html",actions=zip(a,b),search_OK="1")
        else:
            return render_template("search.html",search_OK=None)
    else:
        return render_template("search.html",search_OK=None)

@app.route("/result/delete_DB",methods=["GET","POST"])
def delete():
    if request.method=="POST":
        db.session.query(Words).delete()
        db.session.commit()
        return render_template("delete.html",data_exist="False")
    else:
        word_result=[]
        posi_result=[]
        all_records = Words.query.all()
        if all_records==[]:
            return render_template("delete.html",data_exist="False")
        else:
            for i in all_records:
                word_result.append(i.word)
                posi_result.append(i.Positiver)
            return render_template("delete.html",actions=zip(word_result,posi_result),data_exist="True")

if __name__=="__main__":
    app.run(debug=True)