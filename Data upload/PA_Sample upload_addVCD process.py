# Check whether required packages are inststalled
import subprocess
import sys

reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
#print(installed_packages)

packages = ['pyodbc','pandas', 'requests', 'regex']

for package in packages:
    try:
        if package not in installed_packages:
            print(package + ' is not installed.')
            sys.exit()
    except:
        print('Error : Package does not exist. See Readme in Github for package installation')

# Import relevant modules
try:
    import pyodbc
    import os
    import requests
    from datetime import datetime
    import re
    
except:
    print('Error in importing modules.')

# Function to check whether Project exists or not. Input argument is project_id (varchar), ex. PAT999
def check_Project(project_id):
    # check whether Project ID already exists
    sql = "SELECT Project_ID from Projects WHERE Project_Id = \'" + project_id + "\'"
    cursor.execute(sql)
    data = cursor.fetchall()
    for id in data:
        if project_id == id[0] and len(data)==1:
            print("Project " + project_id+ " exists.")
            return True
        else :
            print("Error in Checking Project")
            raise

# Function to check whether sample exists. Input argument is sammple_name (varchar), ex. PET010
def check_Sample(sample_name):
    # check whether Sample already exists
    sql = "SELECT id,Name from Samples WHERE Name = \'" + sample_name + "\'"
    cursor.execute(sql)
    data = cursor.fetchall()
    for id in data:
        print(id)
        if sample_name == id[1] and len(data)==1:
            print("Sample " + id[1]+ " exists.")
            return True
        else :
            print("Error in Checking whether Sample exists")
            raise

# Function to check whether Process exists or not. Input arguments are sample_name (varchar), ex. PET010, and process_name (varchar), ex. 'Characterisation'
def check_Process(sample_name,process_name):
    # check whether Process already exists
    sql = "SELECT Processes.SampleId, Processes.Name, Samples.name FROM Processes \
        INNER JOIN Samples ON Processes.SampleId = Samples.Id \
        WHERE Samples.Name = \'" +sample_name+ "\' AND Processes.Name = \'" +process_name+ "\'"
    cursor.execute(sql)
    data = cursor.fetchall()
    for id in data:
        if process_name == id[1] and len(data)==1:
            print("Process " +id[1]+ " exists for " + id[2])
            return True
        else :
            print("Error in Checking Process")
            raise
               
# Function to check whether Subprocess exists or not. Input arguments are process_id (int), ex. 1052, and subprocess_id (varchar), ex. 'VCD1'
def check_SubProcess(process_id,subprocess_name):
    # check whether SubProcess already exists
    sql = "SELECT ProcessId, Name FROM Subprocesses WHERE ProcessId = \'" + str(process_id) + "\' AND Name = \'" +subprocess_name+ "\'"
    cursor.execute(sql)
    data = cursor.fetchall()
    for id in data:
        if len(data) == 1:
            sql = "SELECT Samples.Name from Samples INNER JOIN Processes ON Samples.id = Processes.SampleId WHERE Processes.id = \'" + str(process_id) + "\'"
            cursor.execute(sql)
            sample = cursor.fetchone()
            sample_name = sample[0]
            print("SubProcess " +subprocess_name+ " exists for " + sample_name )
            return True
        else :
            print("Error in Checking SubProcess")

# Function to add sample. Input arguments are Project_id, ex. PAT999, and sample_name, ex. "PET101"
def add_Sample(project_id = "", sample_name = ""):
    # Assign project id
    project_id = project_id.strip() # remove white spaces from project name
    sql = "SELECT ID FROM Projects WHERE Project_id = \'" +project_id+"\'"
    cursor.execute(sql)
    x = cursor.fetchone()
    project_id = x[0]
    substrate = ['Glass', 'OPT', 'PEN-BCC-5179944', 'PET-BCC-5179720', 'Silicon']
    for index,sub in enumerate(substrate):
        print(index, '. ', sub)

    ch = input("Choose substrate index : ")
    sample_substrate = substrate[int(ch)]
    # Assign sample name based on substrate 
    sql = "SELECT MAX(SubstrateNumber) from Samples WHERE Substrate LIKE \'%" +sample_substrate+"%\'"
    cursor.execute(sql)
    data = cursor.fetchall()
    for row in data:
        sub_num = row[0]+1
        sample_name  = sample_substrate[:3].upper()+str(row[0]+1).zfill(3)
        print("Available sample name : "+sample_name)
         
    # Assign sample details
    sample_desc = input("Enter Sample description : ")
    sample_com = input("Enter Sample comments : ")
    sample_date = datetime.now()

    # Insert sample details in database
    val = (project_id, sample_substrate, sub_num, sample_desc, sample_com, sample_date, login)
    sql = "INSERT INTO Samples (projectId, substrate, substratenumber, description, comments, createdOn, createdBy) VALUES (?,?,?,?,?,?,?)"
    cursor.execute(sql,val)
  
    # Commit the changes made to the database
    conn.commit()

    # Fetch the last sample uploaded
    try:
        sql = "SELECT Id from Samples WHERE Name = \'" +sample_name+ "\'"
        cursor.execute(sql)
        x = cursor.fetchone()
        sample_id = x[0]  
        print("Checking whether Sample is added to the database :")
        if check_Sample(sample_name) :
            return sample_name
    except :
        print("Error in adding sample " + sample_name)
        raise

# Function to add Process. Input argument is sample_name., ex. "PET010"
def add_Process(sample_name):
    #Assign sample_id
    try :
        sql = "SELECT Id from Samples WHERE Name = \'" +sample_name+ "\'"
        cursor.execute(sql)
        x = cursor.fetchone()
        sample_id = x[0]       
    except :
        print("Sample does not exist")
        raise
    
    # Function to enter new process details
    def process_details():
        process_name = "Deposition"
        process_desc = "Thin film deposition"
        process_com = ""
        process_date = datetime.now()
        pro = [process_name, process_desc, process_com, process_date] # do not chage the order
        return pro

    # Call process details
    pro = process_details()
              
    # Insert process details in database
    val = (sample_id, pro[0], pro[1], pro[2], pro[3], login)
    sql = "INSERT INTO Processes (sampleId, name, description, comments, createdOn, createdBy) VALUES (?,?,?,?,?,?)"
    cursor.execute(sql,val)
    # Commit the changes made to the database
    conn.commit()
    
    # Fetch the last process uploaded
    try:
        print("Checking whether Processes is added to the database now :")
        if check_Process(sample_name, pro[0]) : 
            pass
            
    except :
        print("Error in adding Process " + pro[0])
        raise

    cursor.execute("SELECT Processes.id FROM Processes INNER JOIN Samples ON Processes.SampleID = Samples.Id \
                    WHERE Samples.name = \'" +sample_name+ "\' AND Processes.Name = \'" +pro[0]+ "\'")
    process_id = cursor.fetchone()[0]
    return process_id

# Function to add SubProcess. Input argument is process id (int), ex. 1029, and subprocess_id (varchar), ex. 'VCD1'
def add_SubProcess(process_id, subprocess_name):
    subprocessTypeId = 15
    subprocess_id = 'VCD'
    subprocess_desc = 'Virtual cathode deposition'
    subprocess_com = ""
    (subprocess_par1, subprocess_par2, subprocess_par3) = ("Dep2","Cu001","G001")
    subprocess_date = datetime.now()

    # Insert subprocess details in database
    val = (subprocess_name, subprocess_id, subprocessTypeId, subprocess_par1, subprocess_par2, subprocess_par3, subprocess_desc, \
        subprocess_date, login, login, process_id, subprocess_com)
    sql = "INSERT INTO SubProcesses (name, subprocessid, subprocessTypeId, parameterValue1, parameterValue2, parameterValue3, \
        description,createdOn,createdBy, uploadedby, ProcessId, comments) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
    cursor.execute(sql,val)
    
    # Commit the changes made to the database
    conn.commit()

    # Fetch the last subprocess uploaded
    try:
        print("Checking whether subprocesses is added to the database now:")
        if check_SubProcess(process_id, subprocess_name) : 
            print("Subprocess successfully added")
            return
    except :
        print("Error in adding SubProcess" + subprocess_name)
        raise

choose = input("Do you want to access database? \n 1. Yes \n 2. No \n")
# Connect to the server
if choose == "1":
    # Contact admin for UID and PWD
    UID = input("Enter your user id : ")
    PWD = input("Enter password : ")

    #######Connection will be done using this conection string#######
    connection_string = "DefaultEndpointsProtocol=https;AccountName=metasqlstorage;AccountKey=VoSW7No7d0pMH29Cp2cbQrV4J4AoaZyMPCG5Ml\
    zmF+c0e6SvGlkvrbvdbuFe02Ee4OHedcoau4KD+AStDgvEIA==;EndpointSuffix=core.windows.net"

    ###### SQL connection part #
    conn = pyodbc.connect('Driver={SQL Server};'
                        'Server=meta-sql-resources.database.windows.net;'
                        'Database=metamaterial;'
                        'UID='+UID+';'
                        'PWD='+PWD+';'
                        'Trusted_Connection=no;'
                        'Encrypt=yes;')

    cursor = conn.cursor()
    print("Connected to the server \n")

    # Login Id used for data logging
    userid = input("Enter your login (name.surname) : ")
    login = userid + '@metamaterial.com'
    #########################################################

while choose == "1":
    project_id = input("Enter Project ID : ")
    sample_name = add_Sample(project_id=project_id,sample_name=[])
    process_id = add_Process(sample_name=sample_name)
    add_SubProcess(process_id=process_id, subprocess_name='VCD')
    choose = input("Do you want to access database? \n 1. Yes \n 2. No \n")

conn.close()
