## Welcome to MightyScreen Pages.
MightyScreen is a simple but comprehensive data analysis tool for high-throughput screens. 



## How to use.
Simply upload your data file and start playing. 
Don't have data? You can click "Load Demo" button in upload page.



## Supported file format.
####file format
CSV files

####supported plate format
The program is only tested on 384-plate format. But to support other plate format is not hard. Please send us a sample input file and we can add support to that.

####required columns
    plate, well
these 2 columns are required by MightyScreen.

####reserved name spaces
    identifier, plate_well, hit, welltype, create_date
MightyScreen already specified the meaning for the above columns. You can choose to include them or not, but don't name your experimental readouts with these names.

####supported chemical identifiers
    name, cid, name, smiles, inchi, sdf, inchikey, formula, listkey, identifier(the export file from MightyScreen)
Columns with these will be used to connect your screening compound to PubChem chemical records. But they are not required.
For ICCB users, these are not required, just choose HMS as chemical identifier when uploading. 




## Am I required to register?
Definitely not. Anonymous users have all the functionalities but we recommend user to register before they start doing relatively long term projects.



## Data policy.
We currently have 4T storage space for the incoming data. But eventually we gonna get to a point that we need to clean up old data. The currently plan is to delete data that is over 6 months old. So, please don't reply on mightyscreen to store your data. Often keep an backup of your data using 'ExportData' in the menu.



## Contribute.
We welcome any support from our community. Please fork our rep and hack away. We'll try to merge them in on a regular basis.



## Authors and Contributors
Author: @longfei-wang
Contributor: @yangqinwhu



## Support or Contact or Bug report.
You are welcome to write to mightyscreen@gmail.com.
