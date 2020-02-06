from flask import Flask,request,render_template
from flask_bootstrap import Bootstrap
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.exceptions import BadRequest
import psycopg2
import os

# Init app
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
Bootstrap(app)

# Init database
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cursor = conn.cursor()

@app.route('/')
def index():
    cmd = """SELECT m.id, 
           m.name, 
           mal.author, 
           mal.lab, 
           m.priority, 
           m.estimated_gene_count, 
           t.state, 
           t.created_at AS last_updated 
    FROM   memos AS m 
           JOIN (SELECT DISTINCT ON (memo) memo, 
                                           created_at, 
                                           state 
                 FROM   timestamps 
                 ORDER  BY memo, 
                           created_at DESC) AS t 
             ON t.memo = m.id 
           JOIN (SELECT DISTINCT ON (memo) memo, 
                                           author, 
                                           lab 
                 FROM   memos_authors_labs 
                 ORDER  BY memo, 
                           position ASC) AS mal 
             ON mal.memo = m.id 
    ORDER  BY last_updated DESC """
    cursor.execute(cmd)
    data = cursor.fetchall()
    return render_template("index.html",value=data)

@app.route('/faq')
def faq():
    return render_template("faq.html")

@app.route('/memo/<uuid>')
def memo_table(uuid):
    cursor.execute("SELECT name,short_description,justification,estimated_gene_count,priority,urgency,memo_link,synmemo_link,doi FROM memos WHERE id=%s",(uuid,))
    data = cursor.fetchone()
    cursor.execute("SELECT author,lab,position FROM memos_authors_labs WHERE memo=%s ORDER BY position",(uuid,))
    authors = cursor.fetchall()
    cursor.execute("SELECT state,notes,created_at FROM timestamps WHERE memo=%s ORDER BY created_at DESC",(uuid,))
    table_data = cursor.fetchall()
    return render_template("memo.html",memo=data,authors=authors,state_table=table_data)

#@app.route('/memos_full')
#def memos_full():
#    cmd = "SELECT id,name,short_description,justification,priority,urgency,estimated_gene_count,memo_link,synmemo_link,doi FROM memos ORDER BY priority DESC"
#    cursor.execute(cmd)
#    data = cursor.fetchall()
#    return render_template("memos_full.html",value=data)
#
#@app.route('/memos/<uuid>')
#def get_memo_name(uuid):
#    cmd = "SELECT m.name,t.state,t.created_at,t.notes FROM memos as m JOIN timestamps AS t ON t.memo = m.id WHERE m.id = %s ORDER BY t.created_at DESC"
#    cursor.execute(cmd, (uuid,))
#    data = cursor.fetchall()
#    return render_template("memo_times.html",value=data)

if __name__ == '__main__':
    app.run(debug=True)

