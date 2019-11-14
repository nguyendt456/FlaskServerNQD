from flask import Flask,render_template,request,flash,redirect,url_for,Response
from flask_socketio import SocketIO,emit
from flask_login import LoginManager,login_user, current_user, logout_user, login_required,UserMixin
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from wtforms_components import DateTimeField, DateRange
from wtforms import Form

from sqlalchemy.orm.attributes import flag_modified
import plotly
import chart_studio as py
import plotly.graph_objs as go
import json
import datetime

app = Flask(__name__,static_url_path="/static")
app.config['SECRET_KEY'] = "chuabietlagi"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:nguyen@db/nguyen"
app.config['SQLALCHEMY_POOL_SIZE'] = 100
app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
app.config['DEBUG'] = False

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
socketio = SocketIO(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

userlist = []
for i in range(0,200):
    userlist.append('')

class taodongu(FlaskForm):
    uuid = StringField('UUID',validators=[DataRequired()])
    name = StringField('name',validators=[DataRequired(),Length(min = 6,max = 30,message=u"Tên phải từ 6 đến 40 ký tự")])
    startday = DateField('startdate', format='%d/%m/%Y',validators=[DateRange(max= datetime.date.today(),message=u'Hãy chọn ngày từ hôm nay trở về trước')])
    position = StringField('position',validators=[DataRequired()])
    submit = SubmitField(u'Tạo mới')

class dongu():
    date = db.Column('date',db.Date())
    time = db.Column('time',db.INT())
    temp = db.Column('temp',db.FLOAT())
    humidity = db.Column('humidity',db.FLOAT())

class device(db.Model,UserMixin):
    __tablename__ = "Devices"
    id = db.Column('UserId',db.INT())
    uuid = db.Column('uuid',db.String(),nullable = False,unique = True,primary_key=True)
    name = db.Column('name',db.String(),nullable = False)
    status = db.Column('status',db.String(16),nullable = False)
    date = db.Column('dateactive',db.Date())
    position = db.Column('position',db.String(),unique = True)
    data = db.Column('data',db.JSON(),unique = False,nullable = False)
    minmax = db.Column('minmax',db.JSON(),unique = False, nullable = False)

class createuser(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])
    password = StringField('Password',validators=[DataRequired()])
    email = StringField('Email',validators=[DataRequired()])
    name = StringField('Name',validators=[DataRequired()])
    address = StringField('Address',validators=[DataRequired()])
    submit = SubmitField('Submit')

class login_form(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField(u'Đăng nhập')

class changepasswd(FlaskForm):
    oldpass = PasswordField('Password',validators=[DataRequired()])
    newpass = PasswordField('Password',validators=[DataRequired(),Length(min = 6,max = 40,message=u"Mật khẩu phải từ 6 ký tự trở lên")])
    retype = PasswordField('Password',validators=[DataRequired(),InputRequired(),EqualTo('newpass',message=u'Nhập khớp mật khẩu mới')])
    submit = SubmitField(u'Đổi mật khẩu')

class login_user_data(db.Model, UserMixin):
    __tablename__ = 'UserLogin'
    id = db.Column('id',db.Integer,nullable = False, unique = True,primary_key=True)
    username = db.Column('username',db.String(16), nullable = False, unique = True)
    password = db.Column('password',db.String(60) , nullable = False)
    email = db.Column('email',db.String(120),nullable = False,unique = True)
    name = db.Column('name',db.String,unique = False)
    address = db.Column('address',db.String, nullable = False) 
    def get_id(self):
           return (self.id)

@login_manager.user_loader
def load_user(user_id):
    usid = login_user_data.query.get(user_id)
    print(usid)
    return usid

@app.route('/',methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index')) 
    form = login_form()
    print(form)
    if form.validate_on_submit():
        user = login_user_data.query.filter_by(username = form.username.data).first()
        if user and bcrypt.check_password_hash(user.password,str(form.password.data)):    
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash(u'Wrong Password, Please login again!','danger')
            return redirect(url_for('login'))
    return render_template('login.html',title = 'Login',form = form)

@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@app.route("/index")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    user = login_user_data.query.filter_by(id = current_user.id).first()
    return render_template('index.html', content = user)

@app.route("/user",methods = ['GET','POST'])
def user():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    form = changepasswd()
    content = []
    if form.validate_on_submit():
        user = login_user_data.query.filter_by(id = current_user.id).first()
        if bcrypt.check_password_hash(user.password,str(form.oldpass.data)):
            user.password = bcrypt.generate_password_hash(str(form.newpass.data))
            db.session.commit()
            flash(u'Đổi mật khẩu thành công !','success')
            return render_template("user.html",form = form,title = 'Submit',content = content)
        elif form.oldpass.data != user.password:
            flash(u'Sai Mật khẩu cũ !','danger')
        else:
            flash(u'Nhập đúng mật khẩu mới !','danger')
    return render_template("user.html",form = form,title = 'Submit', content = content)

@app.route("/root",methods = ['GET','POST'])
def root():
    if not current_user.id == 1:
        return redirect(url_for("index"))
    form = createuser()
    if form.validate_on_submit():
        loginuser = login_user_data()
        loginuser.id = login_user_data.query.count() + 1
        loginuser.username = form.username.data
        loginuser.password = bcrypt.generate_password_hash(str(form.password.data))
        loginuser.email = form.email.data
        loginuser.name = form.name.data
        loginuser.address = form.address.data  
        db.session.add(loginuser)
        db.session.commit()
        flash(u'Thêm người dùng thành công !','success')
    return render_template("root.html",form = form)

@app.route("/list",methods = ['GET','POST'])
def listdongu():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    devices = device.query.filter_by(id = current_user.id,status = "online")
    content = []
    x = []
    graphstore = []
    for i in range(0,devices.count()):
        x.append(datetime.date.today() - devices[i].date)
        trace1 = go.Scatter(
            x = devices[i].data['x'],
            y = devices[i].data['temp'],
            mode = 'lines',
            name = 'Nhiet do',
            line = dict(color = 'rgb(255,50,50)')
        )
        trace2 = go.Scatter(
            x = devices[i].data['x'],
            y = devices[i].data['humidity'],
            mode = 'lines',
            name = 'Do am',
            yaxis = 'y2',
            line = dict(color = 'rgb(50,50,255)')
        )       
        temptrace = json.dumps(trace1,cls = plotly.utils.PlotlyJSONEncoder)
        humtrace = json.dumps(trace2,cls = plotly.utils.PlotlyJSONEncoder)
        graphstore.append({'temptrace':temptrace,'humtrace':humtrace})
    if request.is_json:
        donguinfo = request.get_json()
        trackuser = login_user_data.query.filter_by(id = current_user.id).first()
        if bcrypt.check_password_hash(trackuser.password,donguinfo['p']):
            dongune = device.query.filter_by(uuid = donguinfo['uuid']).first()
            dongune.id = 0
            name = dongune.name
            dongune.name = 'unknown'
            socketio.emit(
                'error',
                {'error': ' ','success':u'Xóa thành công %s!'%(name)},
                room = userlist[current_user.id],
                namespace = '/sensor'
            )
            db.session.commit()
        else:
            socketio.emit('error',
            {'error': u'Nhập sai mật khẩu !','success': ' '},
            room = userlist[current_user.id],
            namespace = '/sensor')
    return render_template("list.html",content = content,devices = devices,x=x,graphs = graphstore)

@app.route("/createnew",methods = ['GET','POST'])
def createsomethingnew():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    content = []
    form = taodongu()
    if form.validate_on_submit():
        searchforuuid = device.query.filter_by(uuid = form.uuid.data).first()
        if searchforuuid != None:
            if searchforuuid.id == 0 and searchforuuid.status == 'online':
                searchforuuid.id = current_user.id
                searchforuuid.name = form.name.data
                searchforuuid.date = form.startday.data
                searchforuuid.position = form.position.data
                db.session.commit()
                flash(u'Tạo thành công đống ủ mới !','success')
            else:
                flash(u'Mã đống ủ đã có người sử dụng !','danger')
        else:
            flash(u'Nhập sai mã đống ủ !','danger')
    return render_template("createob.html",content=content,form = form)

@app.route("/giatricambien",methods = ['GET','POST'])
def sensordata():
    if request.is_json:
        sensor = request.get_json()
        databasedt = db.session.query(device).filter_by(uuid = sensor['uuid']).first()
        if databasedt.minmax["tempmin"] > sensor['temp']:
            databasedt.minmax["tempmin"] = sensor['temp']
        if databasedt.minmax["tempmax"] < sensor['temp']:
            databasedt.minmax["tempmax"] = sensor['temp']
        if databasedt.minmax["hummin"] > sensor['humidity']:
            databasedt.minmax["hummin"] = sensor['humidity']
        if databasedt.minmax["hummax"] < sensor['humidity']:
            databasedt.minmax["hummax"] = sensor['humidity']
        timenow = str(datetime.datetime.now().time().hour) + ':' + str(datetime.datetime.now().time().minute) +'(' + str((datetime.date.today()-databasedt.date).days) +')'
        if len(databasedt.data["x"]) != 0:
            timestr = databasedt.data["x"][len(databasedt.data["x"])-1]
            if int(timestr[timestr.find('(')+1:timestr.find(')')]) < int((datetime.date.today()-databasedt.date).days):
                databasedt.data["timestep"].append(timenow)
        print(timenow)
        databasedt.data["x"].append(timenow)
        databasedt.data["temp"].append(sensor['temp'])
        databasedt.data["humidity"].append(sensor['humidity'])
        flag_modified(databasedt,"data")
        flag_modified(databasedt,"minmax")
        db.session.commit()
        if userlist[databasedt.id] != '':
            socketio.emit('temphum',sensor,room = userlist[databasedt.id],namespace='/sensor')
            return Response(status=200, response="OK")
    return Response(status=200, response="ERROR")

@socketio.on('user',namespace = '/user')
def secureuser(username):
    if not current_user.is_authenticated:
        return False
    global userlist
    userlist[current_user.id] = request.sid

if __name__ == '__main__':
    socketio.run(app,host="0.0.0.0",port=80)
