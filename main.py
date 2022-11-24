import os
from datetime import timedelta
import secrets


import pandas as pd
from flask import Flask, render_template, request, url_for, redirect, session, send_file

from users import User
from paid import Paid
from config import *


app = Flask(__name__)
app.secret_key = "........"
app.permanent_session_lifetime = timedelta(minutes=120)

users = User()
paid_ = Paid()

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	if 'user' in session:
		return redirect(url_for('dashboard'))

	else:
		if request.method == 'POST':
			session.permanent = True
			name = request.form['name']
			std = request.form['std']
			school = request.form['school']
			email = request.form['email']
			ph1 = request.form['ph1']
			ph2 = request.form['ph2']
			prc = request.form['prc']
			prp = request.form['prp']
			exp = request.form['exp']
			fp = request.form['fp']
			notes = request.form['notes']
			paid=0
			secret = secrets.token_urlsafe(4)

			users.data_entry(name,std,school,email,ph1,ph2,prc,prp,exp,fp,notes, paid, secret)


			return redirect(url_for('dashboard'))


		else:
			return render_template('register.html')



@app.route('/pop')
def pop():
	if 'user' in session:
		session.pop('user')
		return redirect(url_for('register'))

	else:
		return redirect(url_for('register'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
	if 'admin' in session:
		return redirect(url_for('admin'))

	else:
		if request.method=='POST':
			usr = request.form['username']
			passw = request.form['password']

			if passw==pw_admin and usr=='shakhyar' or usr=='parikhit' or usr=='murtaza' or usr=='iku':
				session['admin'] = 'usr'
				return redirect(url_for('admin'))

			else:
				return render_template('admin_login.html', msg='Wrong password')

		else:
			return render_template('admin_login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
	if 'admin' in session:
		if request.method == "POST":
			action = request.form['btn']
			flag = action[:action.index(':')]

			if flag == "reject":
				secret = action[action.index(':')+1:]
				print(secret)
				users.delete_entry(secret)
				return redirect(url_for('admin'))

			elif flag == "paid":
				# extracts the information of the given pid, redirects to profit page, and returns to dashboard
				secret = action[action.index(':')+1:]
				users.update_entry(secret)
				print(secret)
				return redirect(url_for('admin'))


		else:
			all_list = users.read_all()
			length = len(all_list)
			d = users.count_disec()
			a = users.count_aippm()
			n = users.count_neppm()
			i = users.count_ipc()
			up = len(users.read_unpaid())
			pd = len(paid_.read_all())
			total = pd*250
			return render_template('admin.html', l=all_list, size=length, d=d, a=a, n=n, ipc=i, up=up, pd=pd, total=total)
	else:
		return redirect(url_for('admin_login'))


@app.route('/admin-logout')
def admin_logout():
	if 'admin' in session:
		session.pop('admin')
		return redirect(url_for('admin_login'))
	else:
		return redirect(url_for('admin_login'))

@app.route('/payments', methods=['GET', 'POST'])
def payments():
	if 'admin' in session:
		if request.method == "POST":
			action = request.form['btn']
			flag = action[:action.index(':')]

			if flag == "paid":
				secret = action[action.index(':')+1:]
				print(secret)
				users.update_entry(secret)
				name = users.read_sec(secret)
				paid_.data_entry(name, secret)
				return redirect(url_for('payments'))


			elif flag=='resurrection':
				secret = action[action.index(':')+1:]
				paid_entries = users.paid_check()

				for _paid in paid_entries:
					paid_.data_entry(_paid[0], _paid[12])

				return redirect(url_for('payments'))


			else:
				return redirect(url_for('payments'))

		else:
			all_list = users.read_unpaid()
			leng = len(all_list)
			return render_template('payments.html', l=all_list, num=leng)

	else:
		return redirect(url_for('admin_login'))


@app.route('/paid', methods=['GET', 'POST'])
def paid():
	if 'admin' in session:
		if request.method == "POST":
			action = request.form['btn']
			flag = action[:action.index(':')]

			print(flag, action)


			if flag=='delete':
				secret = action[action.index(':')+1:]
				paid_.delete_entry(secret)
				return redirect(url_for('paid'))
			else:
				return redirect(url_for('paid'))

		else:
			all_list = paid_.read_all()
			leng = len(all_list)
			return render_template('paid.html', l=all_list, num=leng)


	else:
		return redirect(url_for('admin_login'))

@app.route('/download')
def download():
	if 'admin' in session:
		try:
			os.remove(r'E:\smmsmun22\site\static\data.csv')
		except Exception as e:
			print(e)
		l = users.read_all()
		df = pd.DataFrame((l), columns =['Name','Standard','School','Email','ph1','ph2','prc','prp','exp','fp','notes','paid','secret'])

		df.to_csv(csv_path)

		return send_file(csv_path, as_attachment=True)
	else:
		return redirect(url_for('admin_login'))

@app.route('/dashboard')
def dashboard():
	return render_template('dashboard.html')


@app.route('/change/<token>', methods=['GET', 'POST'])
def change(token):
	if 'user' in session:
		if request.method == 'POST':
			com = request.form['prc']
			users.update_prc(token, com)
			return redirect(url_for('dashboard'))

		else:
			return render_template('change.html')

	else:
		return redirect(url_for('login'))



@app.route('/more-downloads', methods=['GET', 'POST'])
def more_downloads():
	if 'admin' in session:
		return render_template('more-downloads.html')

	else:
		return redirect(url_for('admin_login'))



@app.route('/download-disec')
def download_disec():
	if 'admin' in session:
		try:
			os.remove(r'E:\smmsmun22\site\static\data.csv')
		except Exception as e:
			print(e)
		_disec = users.disec()
		df = pd.DataFrame((_disec), columns =['Name','Standard','School','Email','ph1','ph2','prc','prp','exp','fp','notes','paid','secret'])

		df.to_csv(disec_)

		return send_file(disec_, as_attachment=True)
	else:
		return redirect(url_for('admin_login'))



@app.route('/download-aippm')
def download_aippm():
	if 'admin' in session:
		try:
			os.remove(r'E:\smmsmun22\site\static\data.csv')
		except Exception as e:
			print(e)
		_aippm = users.aippm()
		df = pd.DataFrame((_aippm), columns =['Name','Standard','School','Email','ph1','ph2','prc','prp','exp','fp','notes','paid','secret'])

		df.to_csv(aippm_)

		return send_file(aippm_, as_attachment=True)
	else:
		return redirect(url_for('admin_login'))

if __name__ == '__main__':
	app.run(debug=True)