from flask import Flask,render_template,request,flash,redirect,url_for,send_file
from werkzeug.utils import secure_filename
import os
import img2pdf
from PyPDF2 import PdfFileMerger, PdfFileReader
import time

current_dir=os.getcwd()

app=Flask(__name__)

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
                #flash('File saved')

            else:
                return "Upload the supported file formats"
        image_files = [fullpath+f for f in os.listdir(fullpath) if f.lower().endswith('.jpg') or f.lower().endswith('.png')]
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
                #flash('File saved')

            else:
                return "Upload the supported file formats"
        text_files = [f for f in os.listdir(fullpath) if f.endswith('.pdf') or f.endswith('.PDF')]
        mergedObject = PdfFileMerger()
        for f in text_files:
            mergedObject.append(PdfFileReader(fullpath+f, 'rb'))
        mergedObject.write(fullpath+"merged_pdf.pdf")
        if count>0:
            return download(fullpath+"merged_pdf.pdf")
            #return download("https://www.google.com/url?sa=i&url=https%3A%2F%2Ftime.com%2F3063984%2Fhappy-34th-birthday-harry-potter-youre-way-older-than-we-thought-you-were%2F&psig=AOvVaw103RCwvLmPv1HV7r82W6PH&ust=1590574634086000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCOiJ-bKm0ekCFQAAAAAdAAAAABAH")

    else:
        return render_template("PDFmerge.html")

if(__name__=="__main__"):
    app.secret_key = 'super secret key'
    app.run(debug=True)
