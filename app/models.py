from app import db
import zipfile

class User(db.Document):
     email = db.EmailField(unique=True)
     password = db.StringField(default=True)
     active = db.BooleanField(default=True)
    
     phone_number = db.StringField(required=False)

     def __dict__(self):
         return {'username':self.username,'password':self.password,'phone_number':self.phone_number}


class Barcode(db.Document):
     code = db.StringField(required=False)
     user = db.ReferenceField(User)

     def __dict__(self):
         return {'code':self.code}

class Files(db.Document):
    filename = db.StringField(required=False)
    user = db.ReferenceField(User)
    file_url = db.StringField(required=False)
    def __dict__(self):
        return {'filename':self.filename}


def  get_all_barcodes(user):
    if user:
        barcodes =  Barcode.objects(user = user)
    else:
        barcodes =  Barcode.objects()

    barcodes_dict =  [code.__dict__()  for code in barcodes]
    return barcodes_dict


def  get_zip_files_count(user):
    files = []
    if user:
        files =  Files.objects(user = user)
    else:
        files =  Files.objects()
    print 'this is file list' , len(files)
    file_counts =  [zip_file_count(file.file_url) for file in files]
    print 'this is list'
    return sum(file_counts)

def zip_file_count(zip_file_url):
    fh = open(zip_file_url, 'rb')
    try:
      z = zipfile.ZipFile(fh)
      print 'this is list' ,z.namelist()
      return len(z.namelist())
    except:
      return 0
         
  
