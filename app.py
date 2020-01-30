from flask import Flask,request,render_template
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.exceptions import BadRequest
import psycopg2
import os


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cursor = conn.cursor()

@app.route('/memos')
def get_memos():
    cmd = """SELECT m.NAME, 
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
        ORDER  BY last_updated DESC """
    cursor.execute(cmd)
    data = cursor.fetchall()
    return render_template("memos.html",value=data)

if __name__ == '__main__':
    app.run(debug=True)

