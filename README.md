# DMR Radio CPS Import File Builder

This project was inspired by [K7ABD's Anytone Config Builder](https://github.com/K7ABD/anytone-config-builder).  
I wanted to make some custom tweaks to the original tool but was 
thwarted by the prospects of dealing with Perl - not a language 
I've ever warmed up to.  So I re-invented the wheel and created 
a Python script.

The current version generates Channel, Zone, and Talkgroup files
for the Anytone AT-D878UV DMR CPS Software version 1.21.  The tool
uses input files formatted in K7ABD's original format:  Analog__*.csv,
Digital_Others__*.csv, Digital_Repeaters__*.csv, and Talkgroups__*.csv.
The script expects the input files to be placed in an "input_data_files"
directory, and allows multiple files of each input file type.  
This makes it easier to organize the input files into modules.
For example Analog__OR_north_repeaters, Analog__WA_west_repeaters, etc.

Unlike the original K7ABD functionality, the channels are all unique -
subsequent "definitions" of a channel (like re-using in a different
zone) use the parameters of the first definition seen.   I also added
a Zone_Order.csv file to allow specifying what order you want the zones
to appear in the codeplug.  Zones not listed in the Zone_Order file will
be added after the zones listed in the Zone_Order file in the order that
they're processed.

The script also allows for multiple Talk Group names for a Talk Group ID.
When processing the Talkgroups__*.csv files, the first name used in the
first definition of a Talk Group ID is the name that will be used for
all channels in the generated CPS import file.  By carefully crafting a
Talkgroups__xxx.csv file with a filename that is alphabetically first
in the list of Talkgroup__*.csv file names you can easily re-map all
talk groups to use that first file's naming convention.

# Usage

Here is the usage message from the current Anytone 878 script:

```
  usage: anytone-cps-import-builder.py [-h] [--inputdir INPUTDIR] 
       [--outputdir OUTPUTDIR] [--debugmode]

  optional arguments:
    -h, --help             show this help message and exit
    --inputdir INPUTDIR    Directory containing input files
    --outputdir OUTPUTDIR  Target directory for output files
    --debugmode            Set debug flag for troubleshooting
```

The default input directory is "./input_data_files" and the default
output directory is "./output_files".  I've provided an initial set
of channel definition files and Zone_Order.csv file in the 
"reference_data_files" directory.  You can copy all of these files
to the "input_data_files" directory and run the script to build a 
sample set of import files.  The resulting code plug is close to 
what I use in my Anytone 878 here in the Rainier area (Thurston 
Couny, WA).  Feel free to submit your own "Callsign_shared_files" 
directory for inclusion in this project repository. 

# Help Needed

We would like to build a collection of well-maintained channel definition 
files used by this script for anywhere in the world that a DMR radio might
go.  If you have channels you'd like to share, look at the "N7EKB_shared_files"
directory to see an example of the suggested naming convention and file format.
GitHub pull requests for new content are greatly appreciated!

Be sure to checkout the open issues and see if you can help out with any
of them.
