#!/usr/bin/env python
# coding: utf-8
#
# This script reads a CPS channel export file from a supported CPS and
# generates Talkgroup__, Analog__, and Digital-Other__ files suitable 
# for use by the cps-import-builder script.
#


import pandas
import csv
import sys
import os
import time
import glob
import argparse


#
#  Our internal channel dictionary contains a set of channel
#  attributes which are in stored in a dictionary for that
#  channel. Here are the keys available in the attribute dict:
#
#  Key          Comments
#  'Ch Type'        Analog or Digital
#  'RX Freq'        Receive frequency of the channel
#  'TX Freq'        Transmit frequency of the channel
#  'Power'          Power level to operate at Low,Medium,High,Turbo
#                   (Turbo & High are equivalent when not supported)
#  'Bandwidth'      Channel bandwidth 12.5 or 25
#  'CTCSS Decode'   Rx tone decode value
#  'CTCSS Encode'   Tx tone encode value
#  'RX Only'        Make channel receive only if set to "On"
#
#  Additional attributes for a digital channel:
#
#  Key
#  'Color Code'
#  'Talk Group'     Contact/TG Name
#  'Time Slot'
#  'Call Type'      Group/Private
#  'TX Permit'      Always, Color Code Free


# global lists of all CTCSS values
ctcss_list = ['67','67.0','69.4','71.9','74.4','77','79.7','82.5','85.4',
              '88.5','91.5','94.8','97.4','100','100.0','103.5','107.2',
              '110.9','114.8','118.8','123','123.0','127.3','131.8','136.5',
              '141.3','146.2','150','150.0','151.4','156.7','159.8',
              '162.2','165.5','167.9','171.3','173.8','177.3','179.9',
              '183.5','186.2','189.9','192.8','196.6','199.5','203.5',
              '206.5','210.7','218.1','225.7','229.1','233.6','241.8',
              '250.3','254.1']

cdcss_list = ['D023N','D025N','D026N','D031N','D032N','D043N','D047N','D051N',
              'D054N','D065N','D071N','D072N','D073N','D074N','D114N','D115N',
              'D116N','D125N','D131N','D132N','D134N','D143N','D152N','D155N',
              'D156N','D162N','D165N','D172N','D174N','D205N','D223N','D226N',
              'D243N','D244N','D245N','D251N','D261N','D263N','D265N','D271N',
              'D306N','D311N','D315N','D331N','D343N','D346N','D351N','D364N',
              'D365N','D371N','D411N','D412N','D413N','D423N','D431N','D432N',
              'D445N','D464N','D465N','D466N','D503N','D506N','D516N','D532N',
              'D546N','D565N','D606N','D612N','D624N','D627N','D631N','D632N',
              'D654N','D662N','D664N','D703N','D712N','D723N','D731N','D732N',
              'D734N','D743N','D754N']




def anytone_read_channels_export(channels_dict, channels_export_file,
        model, debug=False):
    """This function reads an Anytone 868/878 CPS channels export file"""

    # Header for Anytone 868
    header_row_868 = ['No.','Channel Name','Receive Frequency',
                  'Transmit Frequency','Channel Type','Transmit Power',
                  'Band Width','CTCSS/DCS Decode','CTCSS/DCS Encode',
                  'Contact','Contact Call Type','Radio ID',
                  'Busy Lock/TX Permit','Squelch Mode','Optional Signal',
                  "DTMF ID",'2Tone ID','5Tone ID','PTT ID','Color Code',
                  'Slot','CH Scan List','Receive Group List','TX Prohibit',
                  'Reverse','Simplex TDMA','TDMA Adaptive',
                  'Encryption Type','Digital Encryption',
                  'Call Confirmation','Talk Around','Work Alone',
                  'Custom CTCSS','2TONE Decode','Ranging','Through Mode',
                  'APRS Report','APRS Report Channel']

    # Header for Anytone 878
    header_row_878 = ['No.','Channel Name','Receive Frequency',
                  'Transmit Frequency','Channel Type','Transmit Power',
                  'Band Width','CTCSS/DCS Decode','CTCSS/DCS Encode',
                  'Contact','Contact Call Type','Contact TG/DMR ID','Radio ID',
                  'Busy Lock/TX Permit','Squelch Mode','Optional Signal',
                  "DTMF ID",'2Tone ID','5Tone ID','PTT ID','Color Code',
                  'Slot','Scan List','Receive Group List','PTT Prohibit',
                  'Reverse','Simplex TDMA','Slot Suit',
                  'AES Digital Encryption','Digital Encryption',
                  'Call Confirmation','Talk Around(Simplex)','Work Alone',
                  'Custom CTCSS','2TONE Decode','Ranging','Through Mode',
                  'Digi APRS RX','Analog APRS PTT Mode',
                  'Digital APRS PTT Mode','APRS Report Type',
                  'Digital APRS Report Channel','Correct Frequency[Hz]',
                  'SMS Confirmation','Exclude channel from roaming',
                  'DMR MODE','DataACK Disable','R5toneBot','R5ToneEot']


    return



def cs800d_read_channels_export(channels_dict, channels_export_file,
        debug=False):
    """This function reads a CS800D CPS channels export file"""

    analog_header_row = ['No','Channel Alias','Squelch Level',
                         'Channel Band[KHz]','Personality List','Scan List',
                         'Auto Scan Start','Rx Only','Talk Around',
                         'Lone Worker','VOX','Scrambler','Emp De-emp',
                         'Receive Frequency',
                         'RX CTCSS/CDCSS Type','CTCSS/CDCSS',
                         'RX Ref Frequency','Rx Squelch Mode',
                         'Monitor Squelch Mode',
                         'Channel Switch Squelch Mode',
                         'Transmit Frequency',
                         'TX CTCSS/CDCSS Type','CTCSS/CDCSS',
                         'TX Ref Frequency','Power Level','Tx Admit',
                         'Reverse Burst/Turn off code',
                         'TX Time-out Time[s]','TOT Re-key Time[s]',
                         'TOT Pre-Alert Time[s]',
                         'CTCSS Tail Revert Option']

    digital_header_row = ['No','Channel Alias','Digital Id', 'Color Code',
                         'Time Slot','Scan List','Auto Scan Start','Rx Only',
                         'Talk Around', 'Lone Worker', 'VOX',
                         'Receive Frequency',
                         'RX Ref Frequency', 'RX Group List',
                         'Emergency Alarm Indication',
                         'Emergency Alarm Ack','Emergency Call Indication',
                         'Transmit Frequency',
                         'TX Ref Frequency','TX Contact',
                         'Emergency System', 'Power Level','Tx Admit',
                         'TX Time-out Time[s]','TOT Re-key Time[s]',
                         'TOT Pre-Alert Time[s]','Private Call Confirmed',
                         'Data Call Confirmed','Encrypt']

    return







###############################################################################
#
# Main program...
#
###############################################################################



# Global dictionary/list structures
tg_by_num_dict = {}
tg_by_name_dict = {}
tg_name_to_id_dict = {}
zones_dict = {}
channels_dict = {}
rx_groups_dict = {}
scan_lists_dict = {}
zones_order_list = []
supported_cps_targets = ['868','878','cs800d','uv380']


def main():

    # get today's date to stamp output files with today's iso-date.
    isodate = time.strftime("%Y-%m-%d")

    # Greet the customer
    print("")
    print("CPS Export File Converter")
    print("Supported CPS targets: {}".format(supported_cps_targets))
    print("Source: https://github.com/n7ekb/cps-import-builder")
    print("")

    # get today's date to stamp output files with today's iso-date.
    isodate = time.strftime("%Y-%m-%d")

    #Setup our command line handler
    debugmode = False
    script_name = sys.argv[0]
    parser = argparse.ArgumentParser()
    parser.add_argument('--cps', action='append', required=True,
        dest='cps_target',
        help='specify CPS target; multiple targets allowed, or use special target "all" to generate files for all supported targets',
        default=[])
    parser.add_argument('--inputdir',
        help='specify directory containing input files',
        required=False, default='./input_data_files')
    parser.add_argument('--outputdir',
        help='specify directory for output files',
        required=False, default='./output_files')
    parser.add_argument('--debugmode',
        help='set the debug flag for troubleshooting', required=False,
        action='store_true')

    # parse the command line
    args = parser.parse_args()
    debugflg = args.debugmode

    # sanity check --cps target(s)
    for selection in args.cps_target:
        # if they specify all we just generate everything we support!
        if selection == 'all':
            args.cps_target = supported_cps_targets
            continue
        else:
            if selection not in supported_cps_targets:
                print("ERROR: {} not a supported CPS target.".format(selection))
                print("Supported targets are: {}".format(supported_cps_targets))
                sys.exit(-1)

    # set working directories from command line values
    inputs_dir = args.inputdir
    print("Reading input files from: '{}'.".format(inputs_dir))
    outputs_dir = args.outputdir
    print("Putting output files in: '{}'.".format(outputs_dir))


    if '868' in args.cps_target:

        print("")
        print("Converting channel export from Anytone D868UV")


    if '878' in args.cps_target:

        print("")
        print("Converting channel export from Anytone D878UV")


    if 'cs800d' in args.cps_target:

        print("")
        print("Converting channel export from Connect Systems CS800D")


    if 'uv380' in args.cps_target:

        print("")
        print("Converting channel export from Tytera MD-UV380/MD-UV390")


    print("")
    print("All done!")
    print("")



# if this file isn't being imported as a module then call ourselves as the main thing...
if __name__ == "__main__":
   main()


