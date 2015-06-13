#!/usr/bin/env python
# -*- coding: utf-8 -*-


## openbabel and pybel is needed for parse finger print calculation
#import pybel
#import openbabel
import json
import datetime, os

#==============================================================================

class library(object):
    """ Compound library class to store items belong to the class"""
    def __init__(self,sdf_file):
        self._name = 'ICCB_HMS'
        self._source = sdf_file
        self._mols = [mol for mol in pybel.readfile('sdf', self._source)]  
        self._updated_mols = self._mols
        self._parsed_lib = []
        self._count_read = 0
        self._count_write = 0

                   
    def get_name(self):
        return self._name
    
    def get_source(self):
        return self._source
    
    def get_mols(self):
        return self._mols
    
    def get_updated_mols(self):
        return self._updated_mols
    
    def get_parsed_lib(self):
        return self._parsed_lib

    def get_count_readed(self):
        return len(self._mols)

    def get_count_parsed(self):
        return self._count_parsed
    
    def get_count_write(self):
        return self._count_write    
    
    def set_updated_mols(self, mols):
        self._updated_mols = mols
    
    def set_parsed_lib(self, parsed_lib):
        self._parsed_lib = parsed_lib

    def set_count_read(self,count):
        self._count_read = count

    def set_count_parsed(self,count):
        self._count_parsed = count

    def set_count_write(self,count):
        self._count_write = count



    
    def _fp_to_ascii(self,fp):
        """ function to convert fp format to ascii\n
        Need _ascii_to_fp to convert back to fp \n
        Function _count_bits is needed to calculate similarity using Tanimoto function\n
        for library class, only _fp_to_ascii is needed to convert fp to ascii 
        to store in the databse and use in the future
        """
        return "".join( ["%08x"%num for num in fp])
        
    def _ascii_to_fp(self,ascii):
        ret = []
        for i in range( 0, 256, 8):
            ret.append( int( ascii[i:i+8], 16))
        return ret
    
    def _count_bits(self,num):
        count = 0
        while num:
            count += num & 1
            num >>= 1
        return count
    
    def _tanimoto(self,fp1,fp2):
        """input two finger prints in fp format\n
        return tanimoto coefficient between the two fps\n
            
        fingerprint stored in library are in ascii format, need to use \n
        ascii_to_fp(fp) function to convert it back first    
        """
        common,all =0,0
        for i, num in enumerate(fp2):
            num1 = fp1[i]
            common += self._count_bits(num1 & num)
            all += self._count_bits(num1 | num)
        tanimoto = 1.0*common/all
        return tanimoto

    def _sdf_to_csmi(self,single_sdf_mol):
        """convert a single sdf to canonical smile string
        Can be used to convert multiple properities
        """
        output = pybel.Outputfile('sdf', 'temp.sdf', overwrite = True) 
        output.write(single_sdf_mol)
        output.close           
        conv = openbabel.OBConversion()
    
        ### Sections to convert file format
        ## Convert from sdf to can    
        conv.OpenInAndOutFiles('temp.sdf', 'temp.out')
        conv.SetInAndOutFormats('sdf','can')
        ## write option for 
        conv.SetOptions('in', conv.OUTOPTIONS)    
        conv.Convert()
        conv.CloseOutFile()
        canonical_smiles = open('temp.out').next()
#        line = open('temp.out').next()
#        canonical_smiles = line.split()[0]
    
        conv.OpenInAndOutFiles('temp.sdf', 'temp.out')
        conv.SetInAndOutFormats('sdf','inchikey')
        try:        
            conv.Convert()
            conv.CloseOutFile()
            inchikey = open('temp.out').next()
        except:
            inchikey = 'c'
            
        return [canonical_smiles,inchikey]        
    
    def _update(self):  
        """add chemical properties into each molecules in sdf formation\n
        
         Update the self._updated_mols, which will be used by other functions\n
         
         In current case, it will be used by updateAndWrite() and parse()"""
        
        new_mols = []
        for mol in self.get_mols(): 
            ### Step1: obtain info to be updated
            ##fingerprint fp2, fp3, fp4(google openbabel fingerprint for details)
            fp2s = self._fp_to_ascii(mol.calcfp().fp)
            fp3s = self._fp_to_ascii(mol.calcfp(fptype = 'FP3').fp)
            
            ## For some unknown reason, fp4 calculation causes Segmentation Fault.
            ## So we decided to not include fp4 information.
#            fp4s = self._fp_to_ascii(mol.calcfp(fptype = 'FP4').fp)    
            ## Obtain logP, TPSA from descvalues set
            descvalues = mol.calcdesc(["logP", "TPSA"])
            ## get formula
            formula = mol.formula
            ## get canonical_smiles and inchikey
            canonical_smiles,inchikey = self._sdf_to_csmi(mol)
            
            ###Step2: update info. Have to provide in dictionary pairs.
            ###The key will become a searchable key in mol.data.keys()
            mol.data.update({'Fp2':fp2s})
            mol.data.update({'Fp3':fp3s})
#            mol.data.update({'Fp4':fp4s})
            mol.data.update(descvalues)  
            mol.data.update({'Formula':formula})
            mol.data.update({'Canonical_Smiles':canonical_smiles})
            mol.data.update({'InChiKey':inchikey})
            
            ###Step3: Write the updated molecule
            new_mols.append(mol)
            
        self.set_updated_mols(new_mols)
        
    def updateAndWrite(self):
        if self.get_updated_mols() == self.get_mols():
            self._update()
        output = pybel.Outputfile('sdf', "%s_updated.sdf"
        %(self._source.split('.')[0]), overwrite = True)
        for mol in self.get_updated_mols():
            output.write(mol)
        output.close()
        
    def parse(self):
        pass
    
    def writeParsed(self):
        ''' Write parsed molecules, 
        which is stored in dictionary format, into a file using Json format\n
        Parsed data will be stored in parsed/ foler\n\n
        To decode json file use json.loads() \n
        eg: i = open('temp.out','rU') \n
                for l in i: \n
                    mol = json.loads(l) \n
        '''
        
        mols = self.get_parsed_lib()
        file_number = 1
        mols_per_file = 20000
        mols_in_file = 0
        directory = 'parsed/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        output_name = "%s%s_parsed.json"%(directory,(self._source.split('.')[0].split('/')[1]))
        output = open(output_name, 'w')    
        total_count = 0
        for mol in mols:
            output.write((json.dumps(mol) + '\n'))
            total_count +=1
            mols_in_file +=1
            if mols_in_file == mols_per_file:
                output.close()
                file_number +=1
                output_name = "%s%s_parsed.json"%(directory,(self._source.split('.')[0].split('/')[1]))
                output = open(output_name, 'w')
                mols_in_file = 0                           
        output.close()
        self.set_count_write(total_count)

class iccb(library):           
    ## expanable, other parse function could be provided by change this function
    def parse(self, debug = False):
        """ Parse the file using pybel.readfile function\n
        Return [parse_index,parse_detail]\n        
        
        Return an index(list structure/information) of the output and the parsed_list
        
        In the case of iccb library, it returns [index, parsed_item]\n
        Parsed_item is a list composed of \n
        [{Library_Name:self.name, Library_Info:library_info,
        Chemical_Info:chemical_info}]\
        self.name is the library name\n
        library_info is a dictionary with following keys:\n
        {'Facility_Reagent_ID','Plate_Well','Plate', 'Well','Library'}\n
        Chemical_info is a dictionary with following keys with:\n
        {'svg','sdf','PubChem_CID', 'Chemical_Name','Molecular_Weight',
        'Formula','TPSA', 'logP', 'Fp2', 'Fp3',  
        'Canonical_Smiles', 'InChI','InChiKey'}
        """

        parsed_list = []

        to_upload = ['Library_Name','Facility_Reagent_ID',
        'Plate_Well','Plate', 'Well','Library', 
        'svg','sdf','PubChem_CID', 'Chemical_Name','Molecular_Weight',
        'Formula','TPSA', 'logP', 'Fp2', 'Fp3',  
        'Canonical_Smiles', 'InChI','InChiKey']
#        parse_index = ['parse_index',[{'Library_Name':self.get_name(),'Library_Info':to_upload_library_info,
#                                       'Chemical_Info':to_upload_chemical_info}]]
     
        ## debug_code
        if debug:        
            debug1 = 0
        
        count = 0
        for mol in self.get_updated_mols():
            ##debug code: to define the iteration number
            if debug:
                if debug1>2:
                    break
                else:
                    debug1 +=1
                
            chemical_info = {}            
            for i in to_upload:
                if mol.data.has_key(i):
                    item = mol.data[i]
                    chemical_info.update({i:item})
                else: 
                    chemical_info.update({i:0})
             ## to upload addition properties      
#            additional_info = {}
#            for j in to_upload_additional_info:
#                if mol.data.has_key(j):
#                    item = mol.data[j]
#                    additional_info.update({j:item})
#                else: 
#                    additional_info.update({j:''})
            
            
            svg = mol.write(format = 'svg')
            sdf = mol.write(format = 'sdf')
            chemical_info['svg']=svg
            chemical_info['sdf']=sdf
            chemical_info['Library_Name'] = self.get_name()
            chemical_info['Plate_Well'] = (chemical_info['Plate']+chemical_info['Well'])
            parsed_list.append(chemical_info)  
            count +=1            
              
        self.set_count_parsed(count)   
        self.set_parsed_lib(parsed_list)
        
    def updateAndParse(self, debug = False):
        if self.get_updated_mols() == self.get_mols():
            self._update()
        self.parse(debug)
 

#==============================================================================   
def filelist(directory, key = 'sdf'):
    """ to return a list of filenames with sdf in it, in the provided directory
    """
    filelist=[]
    for f in os.listdir(directory):
        if key in f:
            filelist.append((directory+f))
    filelist.sort()
    return filelist

def splitlib(filename, sdf_per_file = 10000):
    """ Split big sdf file into small sdf chunk files \n
    Input: the filename, and how many sdf intended to be in each small files,
    default is 10000, suggested max is 40000 in order to be handled by openbabel \n
    Return: splited file will be stored in folder splited/
    and a log file splited.out indicates how many sdfs were written
    """
    t1 = datetime.datetime.now()   
    f = open(filename, 'rU')  
    n = 1
    directory = 'splited/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    output = open('%ssublibrary_%d.sdf'%(directory,n),'w')
    sdf_number = 0
    count = 0
    for l in f:
        if 'M  CHG  0' in l:
            continue
        elif '$$$$' not in l:
            try:
                json.dumps(l)
                output.write(l)
            except UnicodeDecodeError:
                l = '0'
                output.write(l)            
        else:
            sdf_number +=1
            output.write(l)
            count +=1
            if sdf_number == sdf_per_file:
                sdf_number = 0 
                output.close()
                n +=1
                output = open('%ssublibrary_%d.sdf'%(directory,n),'w')
                
    t2 = datetime.datetime.now()
    logfile = open('split.out','w') 
    m1 = 'readed %d sdfs \n'%count
    m2 =  "Execution time: %s" % (str(t2-t1)[:-4])
    logfile.write(m1)
    logfile.write(m2)
    logfile.close()
    

def lib_to_json(filename):
    """ the running file
    1. Split the file into individual sdf files, default 10,000 sdf/file, and stored in folder splited \n
    2. Create log/ folder to store processing informations\n    
    3. Process files in foled splited/ individually \n
    3.1. Update and parse library information using lib.updateAndParse() function \n
    3.2. Write the parse file into Json format to be loaded into mySQL databse\n        
    """
    lib_to_parse = filename
    splitlib(lib_to_parse)  
    t1 = datetime.datetime.now()    
    files = filelist('splited/', key = 'sdf')
    count_write = 0
    count_read = 0
    count_parse = 0
    directory = 'log/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    logfile = open('%sparse.out'%directory,'w')
    for f in files:
        templog = open('%sparse_temp.out'%directory,'w')        
        m0 = 'currently working on %s \n'%f
        templog.write(m0)
        templog.close()
        filelog = open('%s%s.out'%(directory,(f.split('.')[0].split('/')[1])),'w')
        lib = iccb(f)       
        lib.updateAndParse()
        lib.writeParsed()
        count_write += lib.get_count_write()
        count_read += lib.get_count_readed()
        count_parse += lib.get_count_parsed()
        m1 = '%d of molecules has been readed from %s\n'%(lib.get_count_readed(),f)
        m2 = '%d of molecules has been parsed\n'%lib.get_count_parsed()
        m3 = '%d of molecules has been written into the json file\n'%lib.get_count_write()
        filelog.write(m1+m2+m3)
        filelog.close()
        logfile.write(m0+m1+m2+m3)
    t2 = datetime.datetime.now()
    m4 = 'In total %d of molecules has been readed\n'%count_read
    m5 = 'In total %d of molecules has been parsed\n'%count_parse
    m6 = 'In total %d of molecules has been written into the json file\n'%count_write    
    m7 =  "Execution time: %s\n" % (str(t2-t1)[:-4])
    logfile.write(m4+m5+m6+m7)
    logfile.close()

def json_to_mysql(formated_dic_lib_file):
    '''import data into the mysql'''       
    conn = MySQLdb.connect(host = 'localhost',
                           user = 'root',
                           passwd = 'wanglf2011',
                           db = 'mightyscreen')    
    cur = conn.cursor()                
    
    mols = [json.loads(mol) for mol in open(formated_dic_lib_file, 'rU')]

    cur.execute("""ALTER TABLE library_library ADD UNIQUE (library_name)""")
    cur.execute("""ALTER TABLE library_sub_library ADD UNIQUE (sub_library_name)""")
    cur.execute("""ALTER TABLE library_compound ADD UNIQUE (plate_well)""")
    conn.commit()

    for mol in mols:
        
        cur.execute("""INSERT IGNORE INTO library_library(library_name, number_of_compounds, number_of_sub_librarys)
        VALUES(%s, 0, 0)
        """,mol['Library_Name'])
           
        cur.execute(""" INSERT IGNORE INTO library_sub_library
                    (sub_library_name, number_of_compounds, super_library_id)
                    VALUES (%s, 0, 
                    (SELECT id FROM library_library WHERE library_name = %s)
                    )
                """, (mol['Library'],mol['Library_Name']))

        cur.execute("""INSERT IGNORE INTO library_compound
            (library_name_id,sub_library_name_id,facility_reagent_id,plate,well,plate_well,
            pubchem_cid,chemical_name,molecular_weight,formula,tpsa,logp,
            inchikey,canonical_smiles,inchi,fp2,fp3,fp4,svg,sdf)
            VALUES((SELECT id FROM library_library WHERE library_name = %s),
            (SELECT id FROM library_sub_library WHERE sub_library_name = %s),
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (mol["Library_Name"],
            mol['Library'],
            mol["Facility_Reagent_ID"],
            mol["Plate"],
            mol["Well"],
            mol["Plate_Well"],
            mol["PubChem_CID"],
            mol["Chemical_Name"],
            mol["Molecular_Weight"],
            mol["Formula"],
            mol["TPSA"],
            mol["logP"],
            mol["InChiKey"],
            mol["Canonical_Smiles"],
            mol["InChI"],
            mol["Fp2"],
            mol["Fp3"],
            mol["Fp4"],
            mol["svg"],
            mol['sdf'],               
            )              
            )                           
        conn.commit()

    cur.execute("""
                UPDATE library_sub_library, library_compound
                SET number_of_compounds =
                (SELECT COUNT(id) FROM library_compound 
                WHERE library_compound.sub_library_name_id = library_sub_library.id)""")    
    cur.execute("""
                UPDATE library_library t1, library_sub_library t2
                SET t1.number_of_compounds =
                (SELECT SUM(number_of_compounds) FROM library_sub_library 
                WHERE t2.super_library_id = t1.id),
                t1.number_of_sub_librarys =
                (SELECT count(id) FROM library_sub_library 
                WHERE t2.super_library_id = t1.id)                
                """)
    conn.commit()
"""
def json_to_mongo(formated_dic_lib_file):
    '''import data into the mango'''  
    from models import compound
    from models import library as lib_model
    from mongoengine import * 


    db = connect('mightyscreen')

    
           
    mols = [json.loads(mol) for mol in open(formated_dic_lib_file, 'rU')]

    lib = lib_model()
    for mol in mols:
        lib = lib_model() 
        lib.library_name = mol['Library_Name']
        try:
            lib.save()
        except NotUniqueError:
            pass            

        
        com = compound()
        com.library_name = mol['Library_Name']
        com.sub_library_name = mol['Library']
        com.facility_reagent_id = str(mol["Facility_Reagent_ID"])
        com.plate= mol["Plate"]
        com.well= mol["Well"]
        com.plate_well = mol["Plate_Well"]
        com.pubchem_cid= mol["PubChem_CID"] 
        com.chemical_name = str(mol["Chemical_Name"])
        com.molecular_weight = mol["Molecular_Weight"]
        com.formula = mol["Formula"]
        com.tpsa = mol["TPSA"]
        com.logp = mol["logP"]
        com.inchikey = mol["InChiKey"]
        com.canonical_smiles = mol["Canonical_Smiles"]
        com.inchi = str(mol["InChI"])
        com.fp2= mol["Fp2"]
        com.fp3 =mol["Fp3"]
        com.fp4 = mol["Fp4"]
        com.svg = mol["svg"]
        com.sdf = mol['sdf']
        try:
	    try:	
            	com.save()
	    except ValidationError:
		com.pubchem_cid=" "
		com.save()	
        except NotUniqueError:
            pass         
"""
def json_to_djangodb(formated_dic_lib_file):
    '''import data into the mango'''
    from library.models import compound
    from library.models import library as lib_model
    from django.core.exceptions import *
     
    mols = [json.loads(mol) for mol in open(formated_dic_lib_file, 'rU')]

    for mol in mols:
        obj,created = lib_model.objects.get_or_create(library_name = mol['Library_Name'])
        obj.number_of_compounds+=1
        obj.save()

        com, created = compound.objects.get_or_create(plate_well=mol['Plate_Well'])	
        com.library_name = obj
        com.sub_library_name = str(mol['Library'])
        com.facility_reagent_id = str(mol["Facility_Reagent_ID"])
        com.plate= mol["Plate"]
        com.well= mol["Well"]
        #com.plate_well = mol["Plate_Well"]
        com.pubchem_cid= mol["PubChem_CID"]
        com.chemical_name = str(mol["Chemical_Name"])
        com.molecular_weight = mol["Molecular_Weight"]
        com.formula = mol["Formula"]
        com.tpsa = mol["TPSA"]
        com.logp = mol["logP"]
        com.inchikey = mol["InChiKey"]
        com.canonical_smiles = mol["Canonical_Smiles"]
        com.inchi = str(mol["InChI"])
        com.fp2= mol["Fp2"]
        com.fp3 =mol["Fp3"]
        com.fp4 = mol["Fp4"]
        com.svg = mol["svg"]
        com.sdf = mol['sdf']

        try:
    	    try:
                com.save()
            except ValidationError:
                com.pubchem_cid=None
                com.save()
    	except:
    	    print mol
    	    print "---------------------------------------------"


def upload(json_directory = '/home/server/iccb_parsed/parsed/'):
    files = filelist(json_directory, key = 'json')
    for f in files:
        print "currently processing "+ f
        json_to_djangodb(f)
        print "Finished processing "+ f

#lib_to_json('10ICCBL_v2.sdf')

t1 = datetime.datetime.now() 
upload()
t2 = datetime.datetime.now() 
print "Execution time: %s\n" % (str(t2-t1)[:-4])
