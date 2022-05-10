JiraReportingAutomator
======================
Author: Marcel Słabosz

Configuration
=============
The script reads configuration from a ini file.
Use config_template.ini file as a configuration template. Copy it or edit in place.
Provide configuration file as `-c/--config` parameter. Default configuration file name: `config.ini`


The worklog naming convention
=============================
The name of the worklog starts with the issue key to which we want to log time.
Optionally after the key, there is a separation string " - " and the next element is a worklog description.

Planned functionalities:
- to indicate that the worklog should be registered with overtime attribute right after the separation string " - "
  should appear "(!)" string.


Exit Codes
==========

* 0 - ok 
* 1 - an error while connecting to the JIRA
* 2 - an error while reading the input file
* 3 - a parse file error
* 4 - an issue with the given key does not exist
* 5 - the file is already processed
* 255 - not implemented function

Output files
============

After successful processing of the input_file in the same directory as input_file output files will be created. 
out_{file_name}.csv - for correctly processed rows, 
err_{file_name}.csv - for rows that wasn't processed correctly. 

out_{...}.csv format for operation -m add
-----------------------------------------

CSV file with columns:
* worklog_id - A unique worklog id in Jira system, can be used to revert operation
* issue_key - The issue key for which worklog was made, 
* work_time_minutes - logged time in format hh:mm:ss
* date - the date of the work

example:
```
worklog_id,issue_key,work_time_minutes,date
1666061,SOME_PROJ-500,0:02:00,2019-02-07 00:00:00+01:00
```

err_{...}.csv format for operation -m add
-----------------------------------------

CSV file with columns:
* issue_key - The issue key for which worklog try to be made,
* is_overtime,
* description - worklog description,
* work_time_minutes - time to log in format hh:mm:ss,
* work_date - the date of the work,
* work_time_secondes - original time to log (without round) in format hh:mm:ss,
* error_message - the caught error message

How to
======
Look at this section to find guide for common operations

How to process input file again.
--------------------------------
If file was already processed, script will stop working before process data and exit with code 5.
The check is performed base on existence of the output files.

To process input file again remove output files created on previous run.
See Output files section for the file names.
