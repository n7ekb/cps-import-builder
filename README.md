# DMR Radio CPS Import File Builder

## Introduction

If you would like to manage DMR Talk Group, Channel, and Zone 
definitions outside of your radio manufacturer's CPS software
using an SCM-friendly textual format, then this tool may be
for you!  If your CPS software supports the import of ".csv" 
(comma separated values) or ".xlsx" files then this tool will
allow you to maintain all of your Talk Group, Channel, and Zone 
definition information in a set of independent, text-based ".csv" 
files.  The Python script in this project takes care of converting
these independent definition files to suitably-formatted import 
files for use by your manufacturer's CPS software.

If you have radios from different manufacturers this tool may
allow you to synchronize the Talk Groups, Channels, and in some
cases the Zones across each of your radios without manual editing.
You maintain one set of definition files, and can target the 
following supported CPS software packages:

* Anytone AT-D868UV CPS Version 1.35
* Anytone AT-D878UV CPS Version 1.21
* Connect Systems CS800D CPS Version R4.03.07
* Tytera MD-UV380/MD-UV390

Future support planned:

* CHIRP (for analog channels)



# Input File Overview

There are four main input file types used by this tool which 
together define a set of Analog and DMR channels for your 
radio(s).  The file type is indicated by a prefix in the file
name.  The prefixes are:  

* Analog__
* Talkgroups__
* Digital-Others__
* Digital-Repeaters__

The layout and purpose of each of these files is described in 
more detail in separate sections for each file type below.

For normal functionality the tool expects at least one file of
each type in it's "input directory".  To facilitate management 
of the input files, the tool allows any number of files for each 
input type to be present in it's working "input directory".  
The input directory defaults to "./input_data_files", but any 
directory can be specified as a command line argument to the 
script. 

The script processes the files in the order shown in the prefix
list above.  If there are more than file one of each type, the 
script will process the input files in alphabetic order.  This 
behavior is significant if you have a talkgroup or channel 
definition in more than one file.  The script ignores subsequent
re-definitions, keeping the attributes of the first definition 
that it sees while processsing.  If you are using reference 
definition files and you want to override a specific talkgroup 
or channel definition without altering the reference file, you 
can simply create a file containing your overriding definition
and give it a filename that sorts first alphabetically.  

A set of sample input files are provided in this repository, 
located in the "N7EKB_shared_files" directory under the 
"reference_data_files" directory.  If you look at this directory,
you'll notice for example that there is an "Analog__" file named
"Analog__N7EKB_MURS_Channels.csv" which defines analog channels
for the MURS radio service.  There is another "Analog__" file
named "Analog__NOAA_WX_Channels.csv" which defines analog channels
for the NOAA weather service in the United States.  By carefully
organizing your reference channel definition files into modules 
like this, you can easily create separate, purpose-specific input 
directories that you can point the script to for processing.
This facilitates building one codeplug for friends and family,
another for your EMCOMM team, another for a trip to a different
area, etc.

Advanced users are encouraged to fork this repository and then 
create and maintain their own "CALLSIGN_shared_files" directory 
under "reference_data_files".  Pull requests for updates to 
such directories will be gladly added to this project repo.  


## Analog__\*.csv

#### Layout

```
Zone, Channel Name, Bandwidth, Power, RX Freq, TX Freq, CTCSS Decode, CTCSS Encode, TX Prohibit
```

#### Description

This file type provides definitions of analog FM channels.

#### Column Details

1. Zone.  The Zone column is used to specify the name of the zone this
channel should be assigned to.  If you want the same channel
to appear in multiple zones, you can specify it on multiple 
rows with different Zone Name values.

2. Channel Name.  The channel name must be unique and can be up to 16 characters
long.  If the script encounters another definition later with
the same name, it will maintain the first definition and issue
a warning message.

3. Bandwidth.  The bandwidth value can be either 12.5 or 25, representing 
narrow or wide FM mode is used for the channel.

4. Power.  The power represents the RF output power setting to be used
by the channel.  The value can be "Low", "Medium", "High", 
or "Turbo".  Depending on the radio CPS, "High" and "Turbo" 
may be equivalent.  The script translates these to the 
appropriate values accepted by the CPS software.

5. RX Freq.  The receive frequency for the channel specified as a numeric
value in MHz.

6. TX Freq.  The transmit frequency for the channel specified as a numeric
value in MHz.

7. CTCSS Decode.  The value of the CTCSS or DCS tone decoded upon receive for
the channel.  The value can be "Off" if CTCSS/DCS is not 
used for receive on this channnel.  

8. CTCSS Encode.  The value of the CTCSS or DCS tone used for transmitting
on the channel.  The value can be "Off" if CTCSS/DCS is not 
used for transmit on this channnel.

9. TX Prohibit.  If set to "On", this value marks the channel as
receive-only - no transmit will be allowed.  If set to "Off", then 
transmitting is allowed on the channel.  Remember to set this to
"On" for any channels with transmit frequency values that lie outside
of ranges you are licensed to operate within.

## Talkgroups__\*.csv

#### Layout

```
TG Name, TG ID
```

#### Description

Files with the Talkgroups__ prefix define the name and DMR ID (talk group number)
of talkgroups used with DMR mode channels.
 
The script allows multiple talkgroup names for the same talkgroup ID.
When processing the Talkgroups__\*.csv files, the name used in the
first definition of a talkgroup ID is the name that will be used for
all channels in the generated CPS import file.  By carefully crafting a
Talkgroups__xxx.csv file with a filename that sorts alphabetically first
in the list of Talkgroup__\*.csv file names you can easily re-map all
talkgroups to use that first file's naming convention.  This is an
important behavior if you are trying to override the channel names
generated by entries in a Digital-Repeater__\*.csv file. 

**Note:**  This file type does NOT have a header row.  In other words, you
will not have "TG Name,TG ID" as the first row in the file - just data rows.

#### Column Details

1. TG Name.  The name for your talkgroup.  Can be up to 16 characters long.

2. TG ID.  The DMR ID number of the talk group.  This can be any number 
from 1-?.

## Digital-Others__

#### Layout

```
Zone, Channel Name, Power, RX Freq, TX Freq, Color Code, Talk Group, TimeSlot, Call Type, TX Permit
```

#### Description

This file type provides definitions of digital mode DMR channels.

#### Column Details

1. Zone.  The Zone column is used to specify the name of the zone this
channel should be assigned to.  If you want the same channel
to appear in multiple zones, you can specify it on multiple 
rows with different Zone Name values.

2. Channel Name.  The channel name must be unique and can be up to 16 characters
long.  If the script encounters another definition later with
the same name, it will maintain the first definition and issue
a warning message.

3. Power.  The power represents the RF output power setting to be used
by the channel.  The value can be "Low", "Medium", "High", 
or "Turbo".  Depending on the radio CPS, "High" and "Turbo" 
may be equivalent.  The script translates these to the 
appropriate values accepted by the CPS software.

4. RX Freq.  The receive frequency for the channel specified as a numeric
value in MHz.

5. TX Freq.  The transmit frequency for the channel specified as a numeric
value in MHz.

6. Color Code.  The digital equivalent of CTCSS/CTDSS, this is a value
between 1 and 14. 

8. Talk Group.  This is the name of the talk group to associate with
the channel.  The value can be a maximum of 16 characters and must be
defined in one (or more) of the Talkgroup__\*.csv input files.

9. TimeSlot.  This is a value of "1" or "2", and defines the DMR time slot
for this channel.

10. Call Type.  The call type can be either "Group Call" or "Private Call".

11. TX Permit.  This value can be "Same Color Code" or "Always".  For 
repeaters you want to use "Same Color Code".  For simplex channels, the
convention is "Always".


## Digital-Repeaters__
  
#### Layout

```
Zone Name, Comment, Power, RX Freq, TX Freq, Color Code, TG 1... TG n
```

#### Description

This file type provides definitions of digital mode DMR channels
for a group of repeaters.  The PNW Digital Network makes their
repeater information available in this format.  Each row is a
specific repeater with columns for a Zone assignment, comment, 
power level, RX/TX frequency and color code, followed by a column 
for each talkgroup potentially available.  The column value of 
"1", "2", or "-", signifies what slot the repeater offers that 
talkgroup on, or if "-" is specified, means the repeater doesn't
carry that particular talkgroup.

By default, the script generates a channel for each talkgroup 
carried by a repeater with the appropriate parameters and zone
assignment.  The channel name is formed from the zone name plus 
the talkgroup name.  To ensure the channel name doesn't exceed
the 16 character limit, a means to specify a shortened name is
provided in the zone name and and talkgroup name values (see 
column details below).

#### Column Details

1. Zone Name.  The zone name is actually two fields delimited by
a semi-colon.  The first part is the actual Zone Name which 
will be used (up to 16 characters) as the zone assignment for
the channels generated for the row.  The second part is an 
abbreviated value that will be used as a prefix to the channel
names created for the row.  The channel names are formed from 
the prefix plus the talkgroup name for each talkgroup on the 
row which has a slot value (either "1" or "2").  On radios
whose CPS doesn't accept imports for Zone files this prefix
is a key to finding the channels you want when building
your zones in the CPS. 

2. Comment.  This is a comment that is ignored by the script.

3. Power.  The power represents the RF output power setting to be used
by the channel.  The value can be "Low", "Medium", "High", 
or "Turbo".  Depending on the radio CPS, "High" and "Turbo" 
may be equivalent.  The script translates these to the 
appropriate values accepted by the CPS software.

4. RX Freq.  The receive frequency for the channel specified as a numeric
value in MHz.

5. TX Freq.  The transmit frequency for the channel specified as a numeric
value in MHz.

6. Color Code.  The digital equivalent of CTCSS/CTDSS, this is a value
between 1 and 14. 

8. TG 1... TG n.  These subsequent column headings signify a 
talkgroup name that is potentially available in this repeater
network.  The value can be a maximum of 16 characters.  This 
talkgroup name value must be defined in one (or more) of the 
Talkgroup__\*.csv input files.  An optional semi-colon delimter 
followed by an abbreviated talkgroup name can be appended to 
the column heading.  This abbreviated name will be used by the
script when forming the channel name.  Channel names cannot 
exceed 16 characters.


# Usage

Here is the usage message from the current script:

```

CPS Import File Builder
Supported CPS targets: ['868', '878', 'cs800d', 'uv380']
Source: https://github.com/n7ekb/cps-import-builder

usage: cps-import-builder.py [-h] --cps CPS_TARGET [--inputdir INPUTDIR]
                             [--outputdir OUTPUTDIR]
                             [--zone_order_file ZONE_ORDER_FILE] [--tg_filter]
                             [--rptr_filter] [--debugmode]

optional arguments:
  -h, --help             show this help message and exit
  --cps CPS_TARGET       specify CPS target; multiple targets allowed, or use
                         special target "all" to generate files for all
                         supported targets
  --inputdir INPUTDIR    specify directory containing input files
  --outputdir OUTPUTDIR  specify directory for output files
  --zone_order_file ZONE_ORDER_FILE
                         specify file to control zone order. Only useful for
                         CPS targets that support zone file import/export
  --tg_filter            set the tg_filter flag; the file 'Digital-Repeaters-
                         MyTalkgroups.csv must be present in the input files
                         directory when this flag set
  --rptr_filter          set the rptr_filter flag; the file 'Digital-Repeaters-
                         MyRepeaters.csv must be present in the input files
                         directory when this flag set
  --debugmode            set the debug flag for troubleshooting

```

# Help Needed

We would like to build a collection of well-maintained channel definition 
files used by this script for anywhere in the world that a DMR radio might
go.  If you have channels you'd like to share, look at the "N7EKB_shared_files"
directory to see an example of the suggested naming convention and file format.
GitHub pull requests for new content are greatly appreciated!

Be sure to checkout the open issues and see if you can help out with any
of them.  If you have an idea for a new feature or improvement, please 
file an issue.
