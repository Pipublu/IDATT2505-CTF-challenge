from flask import Flask, request, redirect
import os, zipfile, shutil

app = Flask(__name__)
loggedIn = False
UPLOAD_FOLDER = "/app/uploads"
FLAG_FILE = "/app/flag.txt"
library_link = "<br><a href='/'>Library</a>"

entries = ["Secrets", "More secrets", "Something fun"]
links = ["secrets", "more", "fun"]
uploaded_files = {} 

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

usr = "user1234"
expected = "KapteinSabeltann"

@app.route("/")
def home():
    html = """
    <h1>My personal library</h1>
    <ul>
    """
    # built in files
    for i in range(len(entries)):
      html += f"<li><a href='/library/{links[i]}'>{entries[i]}</a></li>"
      
    # uploaded files
    if (uploaded_files):
      for filename, path in uploaded_files.items():
        html += f"<li><a href='/library{path}'>{filename}</a></li>"
        
    html += "</ul><a href='/my-page'>My page</a>"
    return html


@app.route("/login", methods=["GET", "POST"])
def login():
  global loggedIn
  msg = ""
  if request.method == "POST":
      username = request.form.get("username")
      password = request.form.get("password")
      if username == usr and password == expected:
          loggedIn = True
          return redirect("/my-page")
      else:
          msg = "Username or password wrong!"
  return f"""
      <form method='POST'>
          Username: <input name='username'><br>
          Password: <input name='password' type='password'><br>
          <button type='submit'>Login</button>
      </form>
      <p style='color:red;'>{msg}</p>
      <a href='/'>Library</a>
  """


@app.route("/library/secrets")
def secrets():
	html = """
	<h1>Secrets</h1>
 
	"""
	return html + open("uploads/secrets.txt").read() + library_link

@app.route("/library/more")
def more():
	html = """
	<h1>More secrets</h1>
	"""
	return html + open("uploads/letter.txt").read() + library_link

@app.route("/library/fun")
def fun():
	html = """
	<h1>¡Que comience la búsqueda del tesoro!</h1>
	<p>¡Hola!
	Pronto el tesoro será nuestro,
	entonces podremos tomarlo con calma
	durante los próximos cien años</p>
 <p>
	Navegamos por todos los mares
	y sembramos miedo y terror.
	Cuando veas la bandera negra,
	será demasiado tarde para dar marcha atrás.
	En el fuego y el agua
	todos remamos,
	pero yo, que vengo primero,
	soy el Capitán Diente de Sable.</p>
	"""
	return html + library_link

@app.route("/library/app/uploads/<filename>")
def library_file(filename):
    if filename in uploaded_files:
        return "<h1>" + filename + "</h1>" + open(uploaded_files[filename]).read() + library_link
    else:
        return "File not found or not uploaded yet.", 404


@app.route("/treasure")
def treasure():
  return "<h1>Ai ai Captain!<h1><img src='https://picsum.photos/200/300'>" + library_link


@app.route("/my-page", methods=["GET", "POST"])
def my_page():
    if not loggedIn:
        return "Access denied for non authorized user. \n <a href='/login'>Log in</a>" + library_link
    
    msg = ""
    
    if request.method == "POST":
        f = request.files.get("file")
        if f and f.filename:
            if f.filename.lower().endswith(".zip"):
                # handle zip upload (may add existing server files via path traversal)
                handle_zip_upload(f)
                msg = f"Processed ZIP: {f.filename}"
            else:
                # normal file upload
                file_path = os.path.join(UPLOAD_FOLDER, f.filename)
                f.save(file_path)
                uploaded_files[f.filename] = file_path  # track uploaded file
                msg = f"Uploaded {f.filename}"

    html = f"""
    <h1>Welcome back user1234!</h1>
    <p style="color:green;">{msg}</p>
    <p>Entries:</p>
    <ul>
    """
    for entry in entries:
        html += f"<li>{entry}</li>\n"
    
    if uploaded_files:
        for filename in uploaded_files:
            html += f"<li>{filename}</li>\n"
    
    html += """
    </ul>
    <form method="POST" enctype="multipart/form-data">
        Upload files: <input type="file" name="file">\n
        <button type="submit">Upload</button>
    </form>
    <a href='/'>Library</a>
    """
    return html
  
def handle_zip_upload(zip_file_obj):
  tmp_zip_path = os.path.join(UPLOAD_FOLDER, "tmp_upload.zip")
  zip_file_obj.save(tmp_zip_path)

  try:
      with zipfile.ZipFile(tmp_zip_path, 'r') as z:
          for entry in z.namelist():
              if entry.endswith('/'):
                continue

              candidate = os.path.normpath(os.path.join(UPLOAD_FOLDER, entry))

              # If candidate resolves to an existing server file -> add it (CTF vulnerability)
              if os.path.exists(candidate) and os.path.isfile(candidate):
                basename = os.path.basename(entry)
                target_path = os.path.join(UPLOAD_FOLDER, basename)
                shutil.copy(candidate, target_path)
                uploaded_files[basename] = target_path
                continue

              # Extract *only* safe entries that remain inside UPLOAD_FOLDER
              upload_folder_abspath = os.path.abspath(UPLOAD_FOLDER)
              candidate_abspath = os.path.abspath(candidate)
              if candidate_abspath.startswith(upload_folder_abspath + os.sep):
                  target_dir = os.path.dirname(candidate_abspath)
                  os.makedirs(target_dir, exist_ok=True)
                  with z.open(entry) as src, open(candidate_abspath, "wb") as dst:
                      dst.write(src.read())
                  basename = os.path.basename(candidate_abspath)
                  uploaded_files[basename] = candidate_abspath
              else:
                  # Intentionally ignore entries that would extract outside uploads
                  pass

  finally:
      try:
          os.remove(tmp_zip_path)
      except OSError:
          pass

if __name__ == "__main__":
	app.run()
