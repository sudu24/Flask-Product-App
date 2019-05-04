from flask import Flask, render_template, request, redirect, url_for
from werkzeug import secure_filename
from flask_mysqldb import MySQL
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

app = Flask(__name__)

UPLOAD_FOLDER = r'C:\Users\Sudhakar\Desktop\deepika\static\images\products'
ALLOWED_EXTENSIONS = set(['jpeg','jpg','png'])

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'products'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


# init MySQL
mysql = MySQL(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET','POST'])
def home():
    cur = mysql.connection.cursor()
    count = cur.execute("SELECT * FROM product")
    mysql.connection.commit()
    res = cur.fetchall()
    cur.close()

    if request.method == 'POST':
        name = request.form['search']
        cur = mysql.connection.cursor()
        count = cur.execute("SELECT * FROM product WHERE name = %s", [str(name)])
        res = cur.fetchall()
        mysql.connection.commit()
        print(res)
        return render_template('index.html', count = count, product=res)

    return render_template('index.html', product=res, count=count)


@app.route('/add_product/', methods=['GET','POST'])
def add_product():
    if request.method == 'POST':

        name = request.form['name']
        price = request.form['price']
        file = request.files['location']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO product(name,price,location) VALUES(%s,%s,%s)",[name,price,file.filename])
        mysql.connection.commit()
        cur.close()

        if file:
            filename = secure_filename(file.filename)
            print(filename)
            #filename = '2.jpg'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print(name, price, file)

        return render_template('add_product.html')

    return render_template('add_product.html')


@app.route('/send_mail/<string:id>', methods=['GET', 'POST'])
def send_mail(id):
    print(id)

    cur = mysql.connection.cursor()
    count = cur.execute("SELECT * FROM product WHERE id = %s", [id])
    res = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    print(res)
    name = res['name']
    price = res['price']
    fromaddr = "someone@gmail.com"
    toaddr = "tomail@gmail.com"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Student Registration"
    mail_text = " Product name: %s \n Price: %s " % (name, price)
    body = mail_text
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "s24u5j92u")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.secret_key = "sfadsfsdfa"
    app.run(debug=True)