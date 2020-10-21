# anytone-cps-import-builder
AnyTone DMR Radio CPS Import File Builder

This Python tool was inspired by K7ABD's Anytone Config Builder
(https://github.com/K7ABD/anytone-config-builder).  I wanted to make some
custom tweaks to the original tool but was thwarted by the prospects
of dealing with Perl - not a language I've ever warmed up to.  So I
re-invented the wheel and created a Python version here using a Jupyter
Notebook environment.

This initial version generates Channel, Zone, and Talkgroup files
for the Anytone AT-D878UV DMR CPS Software version 1.21.  The tool
uses input files using K7ABD's original format:  Analog__*.csv,
Digital_Others__*.csv, Digital_Repeaters__*.csv, and Talkgroups__*.csv.
The script expects the input files to be placed in an "input_data_files"
directory, and allows multiple individual files of each input file
type.  This makes it easier to organize the input files into modules.
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

TODO:  Add script to generate Connect Systems CS800D import files.
