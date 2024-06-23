import pymupdf
import os

base_dir = os.getcwd()
key_dir = os.path.join(base_dir, 'keys')
data_dir = os.path.join(base_dir, 'data')
pdf_dir = os.path.join(data_dir, 'pdf')
os.chdir(pdf_dir)
filelist = [
    "크라운 호프.pdf",
    "export_240428_0512_.pdf",
]

# The desired output document. In this case, we choose a new PDF.
doc = pymupdf.open()  # an omitted argument causes creation of a new PDF

# Now loop through names of input files to insert each.
for filename in filelist:
    doc.insert_file(filename)  # appends it to the end

doc.save("export_240428_0512.pdf")
doc.close()