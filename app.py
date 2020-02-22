from flask import Flask, render_template, json, request, redirect, session, jsonify
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid

mysql = MySQL()
app = Flask(__name__)
app.config.from_object('config')

mysql.init_app(app)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/pricing')
def showPricing():
    return render_template('pricing.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        extension = os.path.splitext(file.filename)[1]
        f_name = str(uuid.uuid4()) + extension
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
    return json.dumps({'filename': f_name})


@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/showAddBlog')
def showAddBlog():
    return render_template('addBlog.html')


@app.route('/addUpdateLike', methods=['POST'])
def addUpdateLike():
    try:
        if session.get('user'):
            _blogId = request.form['blog']
            _like = request.form['like']
            _user = session.get('user')

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_AddUpdateLikes', (_blogId, _user, _like))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'status': 'OK'})
            else:
                return render_template('error.html', error='An error occurred!')

        else:
            return render_template('error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        conn.close()


@app.route('/getAllBlogs')
def getAllBlogs():
    try:
        if session.get('user'):
             
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_GetAllBlogs')
            result = cursor.fetchall()
         
            blogs_dict = []
            for blog in result:
                blog_dict = {
                        'Id': blog[0],
                        'Title': blog[1],
                        'Description': blog[2],
                        'FilePath': blog[3]}
                blogs_dict.append(blog_dict)       
 
            return json.dumps(blogs_dict)
        else:
            return render_template('error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/showDashboard')
def showDashboard():
    if session.get('user'):
        return render_template('dashboard.html')
    else:
        return render_template('signin.html')


@app.route('/showSignin')
def showSignin():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('signin.html')


@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('signin.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


@app.route('/deleteBlog', methods=['POST'])
def deleteBlog():
    try:
        if session.get('user'):
            _id = request.form['id']
            _user = session.get('user')

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_deleteBlog', (_id, _user))
            result = cursor.fetchall()

            if len(result) is 0:
                conn.commit()
                return json.dumps({'status': 'OK'})
            else:
                return json.dumps({'status': 'An Error occurred'})
        else:
            return render_template('error.html', error='Unauthorized Access')
    except Exception as e:
        return json.dumps({'status': str(e)})
    finally:
        cursor.close()
        conn.close()


@app.route('/getBlogById', methods=['POST'])
def getBlogById():
    try:
        if session.get('user'):
            _id = request.form['id']
            _user = session.get('user')
 
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_GetBlogById', (_id, _user))
            result = cursor.fetchall()

            blog = []
            # blog.append({'Id':result[0][0],'Title':result[0][1],'Description':result[0][2]})
            blog.append({'Id': result[0][0], 'Title':result[0][1], 'Description': result[0][2], 'FilePath': result[0][3],
                         'Private': result[0][4], 'Done': result[0][5]})

            return json.dumps(blog)
        else:
            print("fail getBlogById()")
            return render_template('error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/getBlog')
def getBlog():
    try:
        if session.get('user'):
            _user = session.get('user')
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetBlogByUser', (_user,))
            blogs = cursor.fetchall()
            blogs_dict = []
            for blog in blogs:
                blog_dict = {
                        'Id': blog[0],
                        'Title': blog[1],
                        'Description': blog[2],
                        'Date': blog[4]}
                blogs_dict.append(blog_dict)
            return json.dumps(blogs_dict)
        else:
            print("error : getBlog()")
            return render_template('error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/addBlog', methods=['POST'])
def addBlog():
    try:
        if session.get('user'):
            _title = request.form['inputTitle']
            _description = request.form['inputDescription']
            _user = session.get('user')

            if request.form.get('filePath') is None:
                _filePath = ''
            else:
                _filePath = request.form.get('filePath')
            if request.form.get('private') is None:
                _private = 0
            else:
                _private = 1
            if request.form.get('done') is None:
                _done = 0
            else:
                _done = 1            

            conn = mysql.connect()
            cursor = conn.cursor()
            # cursor.callproc('sp_addBlog',(_title,_description,_user))
            cursor.callproc('sp_addBlog', (_title, _description, _user, _filePath, _private, _done))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return redirect('/userHome')
            else:
                return render_template('error.html', error='An error occurred!')

        else:
            return render_template('error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        conn.close()


@app.route('/updateBlog', methods=['POST'])
def updateBlog():
    try:
        if session.get('user'):
            _user = session.get('user')
            _title = request.form['title']
            _description = request.form['description']
            _blog_id = request.form['id']

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_updateBlog', (_title, _description, _blog_id, _user))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'status': 'OK'})
            else:
                return json.dumps({'status': 'ERROR'})
    except Exception as e:
        return json.dumps({'status': 'Unauthorized access'})
    finally:
        cursor.close()
        conn.close()


@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _username = request.form.get('inputEmailSign')
        _password = request.form.get('inputPasswordSign')

        # connect to mysql
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin', (_username,))
        data = cursor.fetchall()

        if len(data) > 0:
            if check_password_hash(str(data[0][3]), _password):
                session['user'] = data[0][0]
                # return redirect('/userHome')
                return render_template('/showDashboard', code=302)
            else:
                return render_template('error.html', error='Wrong Email address or Password.')
        else:
            return render_template('error.html', error='Wrong Email address or Password.')

    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        con.close()


@app.route('/signUp', methods=['POST', 'GET'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:
            
            # All Good, let's call MySQL
            
            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser', (_name, _email, _hashed_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'message': 'User created successfully !'})
            else:
                return json.dumps({'error': str(data[0])})
        else:
            return json.dumps({'html': '<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close() 
        conn.close()


if __name__ == "__main__":
    app.run(port=5050)
