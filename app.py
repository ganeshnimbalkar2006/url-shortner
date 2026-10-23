from flask import Flask,render_template
from inputForm import InputForm
app= Flask(__name__)

@app.route("/",methods=["GET","POST"])

def home():
    form=InputForm()
    if request.method == "POST":
        if form.validate_on_submit():
            print(form.url_input.data)
        else:
            print("failed")   
    return render_template("index.html",form=form)

if __name__ == "__main__":
    app.run(debug=True)