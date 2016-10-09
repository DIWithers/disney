from flask import Flask, render_template, request, redirect, session
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()
#Add to the app (flask object) some config data for our connection
#config is a dictionary
app.config['MYSQL_DATABASE_USER'] = 'x'
app.config['MYSQL_DATABASE_PASSWORD'] = 'x'
app.config['MYSQL_DATABASE_DB'] = 'disney'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
#use the mysql object's method "init_app" and pass it the flask object
mysql.init_app(app)

#Make one re-usable connection
conn = mysql.connect()
#set up cursor object which sql can use and run queries
cursor = conn.cursor()

#secret key needed for sessions to work #salt for the session #gets encrypted
app.secret_key = "drhshsdgeajhsrjgewaetjtdyjsrhwefwe4352352"

@app.route("/") #can also specify GET or POST methods #GET is default when unspecified
def index():
	header_query = "SELECT content FROM page_content WHERE page ='home' AND location = 'header' AND status = '1'"
	cursor.execute(header_query)
	header_text = cursor.fetchall()
	#can be converted from a tuple...
	# a_list = list(header_text)
	left_query = "SELECT image_link, header_text, content, id FROM page_content WHERE page ='home' AND location = 'left_block' AND status = '1'"
	cursor.execute(left_query)
	left_block = cursor.fetchall()

	return render_template("index.html",
		header = header_text,
		left = left_block
		)

@app.route("/admin")
def admin():
	#get the variable 'message' out of the query if it exists
	if request.args.get("message"):
	# return request.args.get("message")
		return render_template("admin.html",
			message = "Login Failed"	
		)
	else:
		return render_template("admin.html")

@app.route("/logout")
def logout():
	session.clear() #ends session
	return redirect("/admin?message=LoggedOut")


		

@app.route("/admin_submit", methods=["GET", "POST"])
def admin_submit():
	print request.form #returns a dictionary... #equiv to req.body
	if request.form["username"] == "admin" and request.form["password"] == "admin":
		#ticket needed to protect portal
		session["username"] = request.form["username"]
		return redirect("/admin_portal")
		# return request.form["username"] + '----' + request.form["password"] #...which you can access by key
	else:
		return redirect("/admin?message=login_failed")

@app.route("/admin_portal")
def admin_portal():
	if "username" in session: #session username exists (local to browser)
		home_page_query = "SELECT image_link, header_text, content, location, id FROM page_content WHERE page = 'home' AND status = '1'"
		cursor.execute(home_page_query)
		data = cursor.fetchall()
		return render_template("admin_portal.html",
			home_page_content = data
			)
	else:
		return redirect("/admin?message=You_Must_Log_In")

@app.route("/admin_update", methods=["POST"])
def admin_update():
	if "username" in session:
		body = request.form["content"]
		header = request.form["header_text"]
		image = request.files["image_link"]
		image.save("static/images/" + image.filename)
		image_path = image.filename
		query = "INSERT INTO page_content VALUES (DEFAULT, 'home', %s, %s, 1, 1, 'left_block', NULL, %s)"
		cursor.execute(query, (header, body, image_path))
		conn.commit()

		return redirect("/admin_portal")
		# header_text = cursor.fetchall()
	else:
		return redirect("/admin?message=You_Must_Log_In")

@app.route("/edit/<id>", methods=["GET", "POST"])
def edit(id):
	if request.method == "GET":
		query = "SELECT header_text, content, image_link, id, status, priority FROM page_content WHERE id = %s" % id
		cursor.execute(query)
		data = cursor.fetchone()
		return render_template("edit.html",
			data = data
		)
	else: #post
		# print request.form
		header_text = request.form["header_text"]
		print header_text
		content = request.form["content"]
		image_link = request.form["image_link"]
		status = request.form["status"]
		priority = request.form["priority"]
		query = "UPDATE page_content SET header_text = %s, content = %s, status = %s, priority = %s, image_link = %s WHERE id = %s"
		cursor.execute(query, (header_text, content, status, priority, image_link, id))
		print query
		print id
		conn.commit()
		# data = cursor.fetchall()
		# print data
		return redirect("/admin_portal?success=Updatesuccessful")

@app.route("/delete/<id>", methods =["GET", "POST"])
def delete(id):
	query = "DELETE FROM page_content WHERE id = %s"
	cursor.execute(query, (id))
	conn.commit()
	return redirect("/admin_portal")

@app.route("/content/<id>", methods = ["GET", "POST"])
def content(id):
	print id
	query = "SELECT image_link_big, header_text, content FROM page_content WHERE id = %s" % id

	cursor.execute(query)
	data = cursor.fetchall()
	print data
	return render_template("content.html",
		content = data
		)

if __name__ == "__main__":
	app.run(debug=True)