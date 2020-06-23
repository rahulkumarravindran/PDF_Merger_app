from flask import Flask,render_template,request,flash,redirect,url_for,send_file
from werkzeug.utils import secure_filename
import os
import img2pdf
from PyPDF2 import PdfFileMerger, PdfFileReader
import time
from flask_sqlalchemy import SQLAlchemy

current_dir=os.getcwd()

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///test.db'
db=SQLAlchemy(app)



class PDFinfo(db.Model):
        id=db.Column(db.Integer,primary_key=True)
        filepath=db.Column(db.String(200))
        filenames=db.Column(db.String(400))
        count=db.Column(db.Integer)

        def __init__(self,id,filepath,filenames,count):
            self.id=id
            self.filepath=filepath
            self.filenames=filenames
            self.count=count


def allowed_file_format(filename):
    if '.pdf' in filename.lower():
        return True
    else:
        return False

def allowed_image_format(filename):
    if '.jpg' in filename.lower() or '.png' in filename.lower():
        return True
    else:
        return False


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/aboutus")
def aboutUs():
    return render_template('aboutus.html')

@app.route("/imagetopdf",methods=['GET','POST'])
def imagetopdf():
    if(request.method=='POST'):
        starttime=int(time.time()*1000)
        files_user_order=[]
        count=0
        files=request.files.getlist('myimage')
        fullpath=current_dir+'\\uploads\\'
        try:
            os.mkdir(fullpath+str(starttime))
            fullpath=fullpath+str(starttime)+"\\"
        except:
            os.mkdir(fullpath+str(starttime+1))
            fullpath=fullpath+str(starttime+1)+"\\"
        for file in files:
            if file.filename=='':
                flash('File not selected')
                return redirect(request.url)
            if file and allowed_image_format(file.filename):
                #return current_dir
                filename=secure_filename(file.filename)
                count+=1
                #return file
                file.save(fullpath+filename)
                files_user_order.append(fullpath+filename)
                #flash('File saved')

            else:
                return "Upload the supported file formats"
        #image_files = [fullpath+f for f in os.listdir(fullpath) if f.lower().endswith('.jpg') or f.lower().endswith('.png')]
        image_files=files_user_order
        with open(fullpath+"img2pdf.pdf", "ab") as f:
            f.write(img2pdf.convert(image_files))
        if count>0:
            return download(fullpath+"img2pdf.pdf")
    else:
        return render_template("image.html")


@app.route("/download",methods=['GET','POST'])
def download(downloadLink):
    #return render_template('download.html',downloadLink=send_file(downloadLink))
    if(request.method=="POST"):
        return send_file(downloadLink)
    else:
        return render_template('download.html',downloadLink=downloadLink)

@app.route("/pdfmerge",methods=['GET','POST'])
def pdfmerge():
    if request.method=="POST":
        starttime=int(time.time()*1000)
        files_user_order=[]
        count=0
        """if 'file' not in request.files:
            flash('No File found')
            return redirect(request.url)"""
        files=request.files.getlist('myfile')
        fullpath=current_dir+'\\uploads\\'
        try:
            os.mkdir(fullpath+str(starttime))
            fullpath=fullpath+str(starttime)+"\\"
        except:
            os.mkdir(fullpath+str(starttime+1))
            fullpath=fullpath+str(starttime+1)+"\\"
        for file in files:
            if file.filename=='':
                flash('File not selected')
                return redirect(request.url)
            if file and allowed_file_format(file.filename):
                #return current_dir
                filename=secure_filename(file.filename)
                count+=1
                #return file
                file.save(fullpath+filename)
                files_user_order.append(str(filename))
                #flash('File saved')

            else:
                return "Upload the supported file formats"

        new_entry=PDFinfo(starttime,fullpath,",".join(files_user_order),count)
        db.create_all()
        db.session.add(new_entry)
        db.session.commit()
        #text_files = [f for f in os.listdir(fullpath) if f.endswith('.pdf') or f.endswith('.PDF')]

        #text_files = reorder(files_user_order)
        return render_template('reorder.html',files_user_order=files_user_order,len= len(files_user_order),starttime=starttime)
        """mergedObject = PdfFileMerger()
        for f in text_files:
            mergedObject.append(PdfFileReader(fullpath+f, 'rb'))
        mergedObject.write(fullpath+"merged_pdf.pdf")
        if count>0:
            return download(fullpath+"merged_pdf.pdf")"""
            #return download("https://www.google.com/url?sa=i&url=https%3A%2F%2Ftime.com%2F3063984%2Fhappy-34th-birthday-harry-potter-youre-way-older-than-we-thought-you-were%2F&psig=AOvVaw103RCwvLmPv1HV7r82W6PH&ust=1590574634086000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCOiJ-bKm0ekCFQAAAAAdAAAAABAH")

    else:
        return render_template("PDFmerge.html")

# the page where the uploaded filenames are listed and user if allowed to reorder them
@app.route("/reorder/<int:starttime>", methods=["GET","POST"])
def reorder(starttime):
    if request.method=='POST':
        required_row=PDFinfo.query.filter_by(id=starttime).first()
        files_user_order=required_row.filenames.split(',')
        fullpath=required_row.filepath
        length=len(files_user_order)
        count=required_row.count

        reordered_list=["0" for i in range(length)]
        inputTxtBox=request.form.getlist('txt')
        for i in range(length):
            reordered_list[int(inputTxtBox[i])-1]=files_user_order[i]

        mergedObject = PdfFileMerger()
        for f in reordered_list:
            mergedObject.append(PdfFileReader(fullpath+f, 'rb'))
        mergedObject.write(fullpath+"merged_pdf.pdf")
        if count>0:
            return download(fullpath+"merged_pdf.pdf")

    else:
        return render_template('reorder.html',files_user_order=files_user_order,len= len(files_user_order))


if(__name__=="__main__"):
    app.secret_key = 'super secret key'
    app.run(debug=True)
