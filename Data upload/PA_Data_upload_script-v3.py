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
    #import pandas as pd
    import requests
    from datetime import datetime
    import re
    #import csv
except:
    print('Error in importing modules.')

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

# Fiunction to add Project. No Input arguments
def add_Project():
    # Enter new project details
    project_id = input("Enter Project ID : ")
    # check whether Project ID already exists
    while check_Project(project_id):
        choice = input("Do you want to add samples to this project? \n 1. Yes \n 2. No \n 3. Exit \n")
        match choice:
            case "1" : 
                add_Sample(project_id=project_id, sample_name=[])
                return
            case "2" : project_id = input("Enter new Project ID : ")
            case _ : return
            
    else :   
        project_name = input("Enter Project name : ")
        project_desc = input("Enter Project description : ")
        project_com = input("Enter Project comments : ")
        project_date = datetime.now()

        # Insert project details in database
        val = (project_id, project_name, project_desc, project_com, project_date, login)
        sql = "INSERT INTO Projects (project_id, name, description, comments, createdOn, createdBy) VALUES (?,?,?,?,?,?)"
        cursor.execute(sql,val)
        
        # Commit the changes made to the database
        conn.commit()

        # Fetch the last project uploaded
        try:
            print("Checking whether Project is added to the database now:")
            if check_Project(project_id) :
                choice = input("Do you want to add samples to this project?  \n 1. Yes \n 2. No \n")
                match choice:
                    case "1": add_Sample(project_id=project_id, sample_name=[])
                    case _ : pass
        except:
            print("Error in adding project" + project_id)
            raise

# Function to add sample. Input arguments are Project_id, ex. PAT999, and sample_name, ex. "PET101"
def add_Sample(project_id = "", sample_name = ""):
    # Assign project id
    sql = "SELECT ID FROM Projects WHERE Project_id = \'" +project_id+"\'"
    cursor.execute(sql)
    x = cursor.fetchone()
    project_id = x[0]
    # Assign sample id
    #if len(sample_name) == 0 :
    # Choose substrate
    sql = "SELECT DISTINCT Substrate from Samples"
    cursor.execute(sql)
    data = cursor.fetchall()
    choice_list =[]
    for idx, row in enumerate(data):
        print(idx, '. ', row[0])
        choice_list.append(idx)
    # Print option for new process
    print(str(idx+1) + ' . New substrate')
    # input choice
    choice = int(input("Choose substrate index from the list above : "))
    if choice in choice_list:
        sample_substrate = data[choice][0]
    else :
        sample_substrate = input("Enter new substrate")

    # Assign sample name based on substrate 
    sql = "SELECT MAX(SubstrateNumber) from Samples WHERE Substrate LIKE \'%" +sample_substrate+"%\'"
    cursor.execute(sql)
    data = cursor.fetchall()
    for row in data:
        sub_num = row[0]+1
        sample_name  = sample_substrate[:3].upper()+str(row[0]+1).zfill(3)
        print("Available sample name : "+sample_name)
    
    # Enter new sample details
    while check_Sample(sample_name):
        choice = input("Do you want to add a process to this sample? \n 1. Yes \n 2. No \n 3. Exit \n")
        match choice:
            case "1" : 
                add_Process(sample_name)
                return
            case "2" : sample_name = input("Enter new Sample Name : ")
            case _ : return
            
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
            choice = input("Do you want to add processes to this sample?  \n 1. Yes \n 2. No \n")
            match choice:
                case"1": add_Process(sample_name)
                case _ : pass
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
        process = input("Enter the type of Process? \n 1. Deposition \n 2. Characterisation \n 3. New Process \n")
        match process:
            case "1" : 
                process_name = "Deposition"
                process_desc = "Thin film deposition"
            case "2" : 
                process_name = "Characterisation"
                process_desc = "All types of measurements done on the samples"
            case "3" : 
                process_name = input("Enter New Process name : ")
                process_desc = input("Enter Process description : ")
            case _ : 
                print("Entered number is not in the ist. Exiting...")
                return
        process_com = ""
        process_date = datetime.now()
        pro = [process_name, process_desc, process_com, process_date] # do not chage the order
        return pro

    # Call process details
    pro = process_details()
    # check whether process exists
    while check_Process(sample_name, pro[0]):
        choice = input("Do you want to add sub-processes to this Process?  \n 1. Yes \n 2. No \n 3. Exit \n")
        match choice:
            case "1" : 
                cursor.execute("SELECT Processes.id FROM Processes INNER JOIN Samples ON Processes.SampleID = Samples.Id \
                    WHERE Samples.name = \'" +sample_name+ "\' AND Processes.Name = \'" +pro[0]+ "\'")
                process_id = cursor.fetchone()[0]
                add_SubProcess(process_id, subprocess_name=[])
                return
            case "2" : 
                print("Enter new process : \n")
                pro = process_details()
                if len(pro) == 0:
                    return
            case _ : return
    
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
            choice = input("Do you want to add subprocesses to this Process?  \n 1. Yes \n 2. No \n")
            match choice:
                case"1": 
                    cursor.execute("SELECT Processes.id FROM Processes INNER JOIN Samples ON Processes.SampleID = Samples.Id \
                    WHERE Samples.name = \'" +sample_name+ "\' AND Processes.Name = \'" +pro[0]+ "\'")
                    process_id = cursor.fetchone()[0]
                    add_SubProcess(process_id, subprocess_name=[])
                case _ : return
            
    except :
        print("Error in adding Process " + pro[0])
        raise

def default_values(code):
    match code:
        case "SP":
            subprocess_par1 = "Tencor 7"
            subprocess_par2 = ""
            subprocess_par3 = ""
        case "FPP":
            subprocess_par1 = "osilla probe station"
            subprocess_par2 = "1.27"
            subprocess_par3 = ""
        case "VCD":
            subprocess_par1 = "Dep2"
            subprocess_par2 = "Cu001"
            subprocess_par3 = "G001"
        case _ :
            subprocess_par1 = ""
            subprocess_par2 = ""
            subprocess_par3 = ""
    
    return (subprocess_par1, subprocess_par2, subprocess_par3)

        
# Function to add SubProcess. Input argument is process id (int), ex. 1029, and subprocess_id (varchar), ex. 'VCD1'
def add_SubProcess(process_id, subprocess_name):
    # Select from Subprocess list
    sql = "SELECT Id, Name, Code from SubProcessTypes"
    cursor.execute(sql)
    x = cursor.fetchall()
    # determine code from subprocess name
    def subpro_code(subprocess_name):     
        sp = subprocess_name.split()
        code = ''
        if len(sp)==1:
            subprocess_id = sp[0][:3]
        else :
            for i in range(0,len(sp)):
                code = code + sp[i][0]
            subprocess_id = code
        return subprocess_id
    
    # Assign subprocess name
    if len(subprocess_name) == 0 :
        choice_list = []
        for idx,row in enumerate(x) : 
            print(idx,' .',row[1], ' - ', row[2])
            choice_list.append(idx)
        # Print option for new process
        print(str(idx+1) + '. New subProcess')
        # Choose from the list of Sub processes
        choice = int(input("Enter the subProcess index from list above: "))
        # Assign subProcess details for the selected option
        if choice in choice_list:
            # Assign subprocess name based on choice from the list
            sql = "SELECT MAX(Name) from Subprocesses WHERE ProcessId = \'" +str(process_id)+ "\'"
            cursor.execute(sql)
            data = cursor.fetchall()
            for row in data:
                if row[0] == None:
                    subprocess_name = x[choice][2]+"1"
                else:
                    print(row[0])
                    match = re.match(r"([a-z]+)([0-9]+)", row[0], re.I)
                    items = match.groups()
                    subprocess_name = items[0]+str(int(items[1])+1)
                    print("Available subprocess name " + subprocess_name)
            # Assign subprocess details
            subprocessTypeId = x[choice][0]
            subprocess_desc = x[choice][1]
            subprocess_id = x[choice][2]
            subprocess_com = ""
            (subprocess_par1, subprocess_par2, subprocess_par3) = default_values(x[choice][2])
        else :
            subprocess_name = input("Enter SubProcess name : ")
            subprocessTypeId = x[-1][0]+1
            subprocess_id = subpro_code(subprocess_name)
            subprocess_desc = input("Enter SubProcess description : ")
            subprocess_com = input("Enter SubProcess comments : ")
            subprocess_name = input("Enter SubProcess Name : ")
            subprocess_par1 = input("Enter SubProcess parameter1 (Leave blank if NA) : ")
            subprocess_par2 = input("Enter SubProcess parameter1 (Leave blank if NA) : ")
            subprocess_par3 = input("Enter SubProcess parameter1 (Leave blank if NA) : ")
    
    else:
        code_list=[]
        for idx,row in enumerate(x) : 
            code_list.append(row[2])
        # Assign index of the subprocess passed as argument
        try:
            match = re.match(r"([a-z]+)([0-9]+)", subprocess_name, re.I)
            items = match.groups()
            subprocess_id = items[0]
            choice = code_list.index(subprocess_id)
            if subprocess_id in code_list:
                subprocessTypeId = x[choice][0]
                subprocess_desc = x[choice][1]
                subprocess_com = ""
                (subprocess_par1, subprocess_par2, subprocess_par3) = default_values(x[choice][2])
        except:
            print('Error : Subprocess code does not exist')
            raise
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

# Function to upload file using Web API
def upload_file(path,file):
    sample_name = re.split('_|-', file)[0]
    subprocess_name = re.split('_|-', file)[-1].split('.')[0]
    filename = file.split('.')[0]
    filetype = file.split('.')[-1]
    filepath = path + "\\" + file
        
    # Find ID of the sub-process to be updated
    sql = "SELECT Subprocesses.Id, Subprocesses.Attachment FROM Subprocesses \
        INNER JOIN Processes ON Subprocesses.ProcessId = Processes.Id \
        INNER JOIN Samples ON Samples.Id = Processes.SampleId \
        WHERE Subprocesses.name = \'" +subprocess_name+ "\' AND Samples.Name = \'" +sample_name+ "\'"
    cursor.execute(sql)
    x = cursor.fetchall()
    for row in x: 
        id = row[0]
        attachment = row[1]
        #print(id)
    
    if attachment == None :
        # upload data using api
        
        url = "https://metamaterial.azurewebsites.net/api/Subprocess/Upload/"+str(id)+'/'+login
        #print(url)
        payload={}
        #files=[('files',(filename,open(filepath,'rt'),filetype))]
        files=[('files',(file,open(filepath,'rb'),filetype))]
        #files={'files':(file,open(filepath,'rt'),filetype)}
        headers = {'Authorization': 'Basic bWV0YW1hdGVyaWFsOnd4Ukt3eVpMWTBVa1ZBRWI='}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        #response = requests.post(url, headers=headers, data=payload, files=files)
        if response.ok:
            print("Upload completed successfully!")
            #print(response.text)
        else:
            print("Something went wrong!")
    else :
        print("Attachemnt already exists.")

# Function to check the directory and files to upload
def check_file():
    path = input("Enter file location : ")
    # Change the directory
    try:
        os.chdir(path)
    except:
        print("File location is not correct")
        raise
    
    # Determine the type of deposition to minimise computational time
    process = input("Enter the type of Process? \n 1. Deposition \n 2. Characterisation \n")
    match process:
        case "1" : process_name = "Deposition"
        case "2" : process_name = "Characterisation"
    
    # Function to check subprocess and call upload file
    def call_upload(sample_name, subprocess_name, path, file):
        # check whether subprocess exists for this sample
        sql = "SELECT Processes.Id FROM Processes JOIN Samples ON Processes.SampleId = Samples.Id WHERE Samples.Name = \'" + sample_name + "\'AND Processes.Name = \'" + process_name + "\'"
        cursor.execute(sql)
        process_id = cursor.fetchone()[0]
        if check_SubProcess(process_id, subprocess_name):
            upload_file(path, file)
        else:
            # Add subprocess without prompt
            add_SubProcess(process_id, subprocess_name)
            upload_file(path, file)
            '''
            choice = input("SubProcess does not exist for this sample. Do you want to add it ?  \n 1. Yes \n 2. No \n")
            match choice:
                case "1":
                    add_SubProcess(process_id, subprocess_name)
                    upload_file(path, file)
                case _: pass
            '''

    # iterate through all file
    for file in os.listdir():
        # Extract sample ID from filename
        sample_name = re.split('_|-', file)[0]
        subprocess_name = re.split('_|-', file)[-1].split('.')[0]
        print(sample_name,subprocess_name)
        
        # Check whether sample exists in the database
        if check_Sample(sample_name):
            # check whether process exists for this sample
            if check_Process(sample_name=sample_name, process_name=process_name):
                call_upload(sample_name, subprocess_name, path, file)
            else:
                choice = input("Process does not exist for this sample. Do you want to add it ?  \n 1. Yes \n 2. No \n")
                match choice:
                    case "1" :
                        add_Process(sample_name)
                        call_upload(sample_name, subprocess_name, path, file)
                    case _: pass
        else :
            choice = input("Sample does not exist. Do you want to add it ?  \n 1. Yes \n 2. No \n")
            match choice:
                case "1": 
                    project_id = input("Enter Project ID : ")
                    add_Sample(project_id=project_id, sample_name=sample_name)
                    call_upload(sample_name, subprocess_name, path, file)
                case _: pass

choice  = input(" Choose from the list below : \n 1. Add Project \n 2. Add Sample \n 3. Add Process \n 4. Add SubProcess \n 5. Upload files to a SubProcess \n 6. Exit \n")
match choice:
    case "1": add_Project() # calls add_project first; add_sample, add_process, add_subprocess are called from there in appropriate order
    case "2": 
        # Enter new project details
        project_id = input("Enter Project ID : ")
        add_Sample(project_id=project_id,sample_name=[])
    case "3":
        project_id = input("Enter Project ID : ")
        sample_name = input("Enter Sample Name : ")
        add_Process(sample_name)
    case "4":
        project_id = input("Enter Project ID : ")
        sample_name = input("Enter Sample Name : ")
        add_Process(sample_name) # add_sub_process is called from add_Process in the correct order
    case "5" : check_file()
    case _ : pass
conn.close()
