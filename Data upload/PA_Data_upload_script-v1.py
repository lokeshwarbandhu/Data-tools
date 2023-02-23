import pyodbc
import sys
import os
import pandas as pd
import requests
import json
import requests
from datetime import datetime
#import sqlite3

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
            break
        else :
            print("Error in checking Project")
            raise

# Function to check whether sample exists. Input argument is sammple_name (varchar), ex. PET010
def check_Sample(sample_name):
    # check whether Project ID already exists
    sql = "SELECT id,Name from Samples WHERE Name = \'" + sample_name + "\'"
    cursor.execute(sql)
    data = cursor.fetchall()
    for id in data:
        if sample_name == id[1] and len(data)==1:
            print("Sample " + id[1]+ " exists.")
            return True
            break
        else :
            print("Error in checking Sample")
            raise

# Function to check whether Process exists or not. Input arguments are sample_name (varchar), ex. PET010, and process_name (varchar), ex. 'Characterisation'
def check_Process(sample_name,process_name):
    # check whether Project ID already exists
    sql = "SELECT Processes.SampleId, Processes.Name, Samples.name FROM Processes \
        INNER JOIN Samples ON Processes.SampleId = Samples.Id \
        WHERE Samples.Name = \'" +sample_name+ "\' AND Processes.Name = \'" +process_name+ "\'"
    cursor.execute(sql)
    data = cursor.fetchall()
    for id in data:
        if process_name == id[1] and len(data)==1:
            print("Process " +id[1]+ " exists for " + id[2])
            return True
            break
        else :
                print("Error in checking Process")
                raise
               
# Function to check whether Subprocess exists or not. Input arguments are process_id (int), ex. 1052, and subprocess_id (varchar), ex. 'VCD1'
def check_SubProcess(process_id,subprocess_name):
    # check whether Project ID already exists
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
            break
        else :
            print("Error in checking SbProcess")

# Fiunction to add Project. No Input arguments
def add_Project():
    # Enter new project details
    project_id = input("Enter Project ID : ")
    # check whether Project ID already exists
    if check_Project(project_id):
        choice = input("Do you want to add samples to this project? \n 1. Yes \n 2. No \n")
        return project_id
            
    else :   
        project_id = input("Enter new Project ID : ")
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
            print("Checking Project in database :")
            if check_Project(project_id) :
                choice = input("Do you want to add samples to this project?  \n 1. Yes \n 2. No \n")
                match choice:
                    case "1": return project_id
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
    if len(sample_name) == 0 :
        # Enter new sample details
        sample_name = input("Enter Sample Name : ")
    else :
        sample_name = sample_name
    
    # Assign substrate
    sample_substrate = ""
    sql = "SELECT Name, Substrate from Samples WHERE Name LIKE \'" +sample_name[0:3]+"%\'"
    cursor.execute(sql)
    x = cursor.fetchall()
    for row in x:
        sample_substrate = row[1]
        break
    if len(sample_substrate) == 0:
        sample_substrate = input("Enter new sustrate : ")
    
    # Assign sample details
    sample_desc = input("Enter Sample description : ")
    sample_com = input("Enter Sample comments : ")
    sample_date = datetime.now()

    # Insert sample details in database
    val = (project_id, sample_name, sample_substrate, sample_desc, sample_com, sample_date, login)
    sql = "INSERT INTO Samples (projectId, name, substrate, description, comments, createdOn, createdBy) VALUES (?,?,?,?,?,?,?)"
    cursor.execute(sql,val)
  
    # Commit the changes made to the database
    conn.commit()

    # Fetch the last sample uploaded
    try:
        sql = "SELECT Id from Samples WHERE Name = \'" +sample_name+ "\'"
        cursor.execute(sql)
        x = cursor.fetchone()
        sample_id = x[0]  
        print("Checking Sample in database :")
        if check_Sample(sample_name) :
            choice = input("Do you want to add processes to this sample?  \n 1. Yes \n 2. No \n")
            return choice
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
        
    
    # Enter new process details
    process = input("Enter the type of Process? \n 1. Deposition \n 2. Characterisation \n 3. New Process \n")
    match process:
        case "1" : 
            process_name = "Deposition"
            process_desc = "Thin film deposition"
        case "2" : 
            process_name = "Characterisation"
            process_desc = "All types of measurements done on the samples"
        case _ : 
            process_name = input("Enter New Process name : ")
            process_desc = input("Enter Process description : ")
    process_com = ""
    process_date = datetime.now()

    # Insert process details in database
    val = (sample_id, process_name, process_desc, process_com, process_date, login)
    sql = "INSERT INTO Processes (sampleId, name, description, comments, createdOn, createdBy) VALUES (?,?,?,?,?,?)"
    cursor.execute(sql,val)

    choice = input("Do you want to add sub-processes to this Process?  \n 1. Yes \n 2. No \n")
    match choice:
        case "1" : 
            cursor.execute("SELECT Processes.id FROM Processes INNER JOIN Samples ON Processes.SampleID = Samples.Id \
                WHERE Samples.name = \'" +sample_name+ "\' AND Processes.Name = \'" +process_name+ "\'")
            process_id = cursor.fetchone()[0]
            return process_id
        case _ : pass
    
    # Commit the changes made to the database
    conn.commit()

    # Fetch the last process uploaded
    try:
        print("Checking Processes in database :")
        if check_Process(sample_id, process_name) : pass
    except :
        print("Error in adding Process" + process_name)
        raise

        
# Function to add SubProcess. Input argument is process id (int), ex. 1029, and subprocess_id (varchar), ex. 'VCD1'
def add_SubProcess(process_id, subprocess_name):
    # Enter new subprocess details
    sql = "SELECT Id, Name, Code from SubProcessTypes"
    cursor.execute(sql)
    x = cursor.fetchall()
    for idx, row in enumerate(x) : 
        print(row[0], '. ',row[1])
    # Print option for new process
    print(str(idx+1) + '. New subProcess')
    # Choose from the list of Sub processes
    choice = int(input("Enter the subProcess index from list above: "))
    # Assign subProcess details for the selected option
    if choice in range(1,idx):
        subprocess_name = subprocess_name
        subprocessTypeId = x[choice-1][0]
        subprocess_desc = x[choice-1][1]
        subprocess_com = ""
    else :
        subprocess_name = input("Enter SubProcess name : ")
        subprocessTypeId = input("Enter SubProcess ID : ")
        subprocess_desc = input("Enter SubProcess description : ")
        subprocess_com = input("Enter SubProcess comments : ")
    
    subprocess_date = datetime.now()
    subprocess_par1 = ""
    subprocess_par2 = ""
    subprocess_par3 = ""
    
    # Insert subprocess details in database
    val = (subprocess_name, subprocessTypeId, subprocess_par1, subprocess_par2, subprocess_par3, subprocess_desc, \
        subprocess_date, login, process_id, subprocess_com)
    sql = "INSERT INTO SubProcesses (name, subprocessTypeId, parameterValue1, parameterValue2, parameterValue3, \
        description,createdOn,createdBy, ProcessId, comments) VALUES (?,?,?,?,?,?,?,?,?,?)"
    cursor.execute(sql,val)

    # Commit the changes made to the database
    conn.commit()

    # Fetch the last subprocess uploaded
    try:
        print("Checking subprocesses in database :")
        if check_SubProcess(process_id, subprocess_name) : pass
    except :
        print("Error in adding SubProcess" + subprocess_name)
        raise

# Function to upload file using Web API
def upload_file(path,file):
    sample_id = file.split('_')[0]
    subprocess_id = file.split('_')[-1].split('.')[0]
    filename = file.split('.')[0]
    filetype = file.split('.')[-1]
    filepath = path + "\\" + file
    #data = pd.read_csv(filepath)
    
    # Find ID of the sub-process to be updated
    sql = "SELECT Subprocesses.Id FROM Subprocesses \
        INNER JOIN Processes ON Subprocesses.ProcessId = Processes.Id \
        INNER JOIN Samples ON Samples.Id = Processes.SampleId \
        WHERE Subprocesses.name = \'" +subprocess_id+ "\' AND Samples.Name = \'" +sample_id+ "\'"
    cursor.execute(sql)
    x = cursor.fetchall()
    for row in x: 
        id = row[0]
        #print(id)
    
    # upload data using api
    url = "https://metamaterial.azurewebsites.net/api/Subprocess/Upload/"+str(id)
    #print(url)
    payload={}
    files=[('files',(filename,open(filepath,'rb'),filetype))]
    headers = {'Authorization': 'Basic bWV0YW1hdGVyaWFsOnd4Ukt3eVpMWTBVa1ZBRWI='}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    print(response.text)
    print("File uploaded for "+sample_id+ " in Subprocess : "+subprocess_id)

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
    # iterate through all file
    for file in os.listdir():
        # Extract sample ID from filename
        sample_name = file.split('_')[0]
        subprocess_name = file.split('_')[-1].split('.')[0]
        print(sample_name,subprocess_name)

        # Check whether sample exists in the database
        if check_Sample(sample_name):
            # check whether process exists for this sample
            if check_Process(sample_name=sample_name, process_name=process_name):
                # check whether subprocess exists for this sample
                sql = "SELECT Processes.Id FROM Processes JOIN Samples ON Processes.SampleId = Samples.Id WHERE Samples.Name = \'" + sample_name + "\'"
                cursor.execute(sql)
                process_id = cursor.fetchone()[0]
                if check_SubProcess(process_id, subprocess_name):
                    upload_file(path, file)
                else:
                    choice = input("SubProcess does not exist for this sample. Do you want to add it ?  \n 1. Yes \n 2. No \n")
                    match choice:
                        case "1":
                            add_SubProcess(process_id, subprocess_name)
                            upload_file(path, file)
                        case _: pass
            else:
                choice = input("Process does not exist for this sample. Do you want to add it ?  \n 1. Yes \n 2. No \n")
                match choice:
                    case "1" :
                        process_id = add_Process(sample_name)
                        if process_id:
                            add_SubProcess(process_id, subprocess_name)
                            upload_file(path, file)
                        else : print("Error in adding process")
                    case _: pass
        else :
            choice = input("Sample does not exist. Do you want to add it ?  \n 1. Yes \n 2. No \n")
            match choice:
                case "1": 
                    project_id = add_Project()
                    if project_id:
                        option = add_Sample(project_id=project_id, sample_name=sample_name)
                        match option:
                            case "1": 
                                process_id = add_Process(sample_name)
                                if process_id:
                                    add_SubProcess(process_id, subprocess_name)
                                    upload_file(path, file)
                            case _: pass
                    else : pass
                case _ : pass

check_file()
conn.close()
