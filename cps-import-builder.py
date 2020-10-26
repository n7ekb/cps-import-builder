#!/usr/bin/env python
# coding: utf-8
#
# This notebook contains code that reads in K7ABD formatted Anytone Config Builder
# files into a generic in-memory set of python DMR codeplug structures and then
# generates files suitable for import into the Connect Systems CS800D CPS.
# 
# Developed/tested for CPS Release Version: R4.03.07.
#


import pandas 
import csv
import sys
import os 
import time
import glob
import argparse

#
# CS800D Export File format - Analog Tab Columns
#
# Col   Header Name         Comments/Default
#   0   No
#   1   Channel Alias
#   2   Squelch Level       (Normal)
#   3   Channel Band[KHz]   (12.5)  12.5/25
#   4   Personality List    (Personality 1)   
#   5   Scan List           (None)
#   6   Auto Scan Start     (Off)
#   7   Rx Only             (Off)
#   8   Talk Around         (Off)
#   9   Lone Worker         (Off)
#  10   VOX                 (Off)
#  11   Scrambler           (Off)
#  12   Emp De-emp          (Off)
#  13   Receive Frequency   
#  14   RX CTCSS/CDCSS Type (NONE/CTCSS/CDCSS)
#  15   CTCSS/CDCSS         (tone value - number val only for DCS)
#  16   RX Ref Frequency    (Middle) Low/Middle/High
#  17   Rx Squelch Mode     (CTCSS/DCS and Audio)
#  18   Monitor Squelch Mode            (Carrier)
#  19   Channel Switch Squelch Mode     (RX Squelch Mode)
#  20   Transmit Frequency  
#  21   TX CTCSS/CDCSS Type (NONE/CTCSS/CDCSS)
#  22   CTCSS/CDCSS         (tone value - number val only for DCS)
#  23   TX Ref Frequency    (Middle)  Low/Middle/High
#  24   Power Level         (Low) Low/High
#  25   Tx Admit            (Aways Allow) Note misspelling
#  26   Reverse Burst/Turn off code     (Off)
#  27   TX Time-out Time[s] (60)
#  28   TOT Re-key Time[s]  (0)
#  29   TOT Pre-Alert Time[s]           (0)
#  30   CTCSS Tail Revert Option        (180)
#
#
# CS800D Export File format - Digital Tab Columns
#
# Col   Header Name         Comments/(Default)
#   0   No
#   1   Channel Alias       
#   2   Digital ID          Radio/DMR ID - can be different per channel
#   3   Color Code          1-14
#   4   Time Slot           (Slot 1)  Slot 1/Slot 2
#   5   Scan List           (None)
#   6   Auto Scan Start     (Off)
#   7   Rx Only             (Off)  Off/On
#   8   Talk Around         (Off)
#   9   Lone Worker         (Off)
#  10   VOX                 (Off)
#  11   Receive Frequency   
#  12   RX Ref Frequency    (Middle) Low/Middle/High
#  13   RX Group List       (None) 
#  14   Emergency Alarm Indication      (Off)
#  15   Emergency Alarm Ack             (Off)
#  16   Emergency Call Indication       (Off)
#  17   Transmit Frequency
#  18   TX Ref Frequency    (Middle) Low/Middle/High
#  19   TX Contact          TG Name
#  20   Emergency System    (None)
#  21   Power Level         (High)    Low/Middle/High
#  22   TX Admit            (Always)  Always/Color Code Free
#  23   TX Time-out Time[s] (60)
#  24   TOT Re-key Time[s]  (0)
#  25   TOT Pre-Alert Time[s]           (0)
#  26   Private Call Confirmed          (Off)
#  27   Data Call Confirmed             (Off)
#  28   Encrypt             (Off)
#
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
#  'Talk Group'
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



def cs800d_write_channels_export(channels_dict, channels_export_file, 
        debug=False):
    """This function writes out a CS800D CPS formatted channels file"""

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
    
    # setup analog channels dataframe
    analog_channels_out_list = []
    cnt = 1
    for ch_name in sorted(channels_dict.keys()):
        ch_type = channels_dict[ch_name]['Ch Type']
        
        # skip non-analog channels
        if ch_type != 'Analog':
            continue

        # get channel attributes dictionary
        attr_dict = channels_dict[ch_name]
        
        # now fill out this row in correct order for cs800d
        row_list = []
        row_list.append(str(cnt))
        cnt = cnt + 1
        row_list.append(ch_name)                    # Channel Alias
        row_list.append("Normal")                   # Squelch level
        row_list.append(attr_dict['Bandwidth'])     # Channel Bandwidth
        row_list.append("Personality 1")            # Personality
        row_list.append("None")                     # scan list
        row_list.append("Off")                      # auto scan start
        row_list.append(attr_dict['RX Only'])       # Rx Only
        row_list.append("Off")                      # Talk around
        row_list.append("Off")                      # Lone Worker
        row_list.append("Off")                      # VOX
        row_list.append("Off")                      # Scrambler
        row_list.append("Off")                      # Emp De-emp
        row_list.append(attr_dict['RX Freq'])       # Receive Frequency
        
        # RX CTCSS/CDCSS Type & set rx_squelch_mode
        ctcss_dcs_decode_val = str(attr_dict['CTCSS Decode'])
        if ctcss_dcs_decode_val == "Off":
            row_list.append("NONE")
            row_list.append("NONE")
            rx_squelch_mode = "CTCSS/DCS and Audio"
        elif ctcss_dcs_decode_val in ctcss_list:
            row_list.append("CTCSS")
            row_list.append(float(ctcss_dcs_decode_val))
            rx_squelch_mode = "CTCSS/DCS and Audio"
        elif ctcss_dcs_decode_val in cdcss_list:
            row_list.append("CDCSS")
            row_list.append(ctcss_dcs_decode_val[1:4])
            rx_squelch_mode = "CTCSS/DCS and Audio"
        else:
            # we should never get here!
            print("ERROR:  Invalid ctcss_dcs_decode_val '{}'".format(
                ctcss_dcs_decode_val))
            sys.exit(-1)
           
        # Compute RX Ref Frequency
        if float(attr_dict['RX Freq']) > 180.0:
            row_list.append("Low")  # RX Ref Frequency (VHF/2 meters)
        else:
            row_list.append("Low")  # RX Ref Frequency (UHF/70cm )

        row_list.append(rx_squelch_mode)    # Rx squelch mode
        row_list.append("Carrier")          # Monitor squelch mode
        row_list.append("RX Squelch Mode")  # Channel switch squelch mode
        
        row_list.append(attr_dict['TX Freq'])       # Transmit Frequency
        
        # TX CTCSS/CDCSS Type
        ctcss_dcs_encode_val = str(attr_dict['CTCSS Encode'])
        if ctcss_dcs_encode_val == "Off":
            row_list.append("NONE")
            row_list.append("NONE")
        elif ctcss_dcs_encode_val in ctcss_list:
            row_list.append("CTCSS")
            row_list.append(float(ctcss_dcs_encode_val))
        elif ctcss_dcs_encode_val in cdcss_list:
            row_list.append("CDCSS")
            row_list.append(ctcss_dcs_encode_val[1:4])
        else:
            # we should never get here!
            print("ERROR:  Invalid ctcss_dcs_encode_val '{}'".format(
                ctcss_dcs_encode_val))
            sys.exit(-1)
        
        # Compute TX Ref Frequency
        if float(attr_dict['TX Freq']) > 180.0:
            row_list.append("Middle")     # TX Ref Frequency (VHF/2 meters)
        else:
            row_list.append("Low")        # TX Ref Frequency (UHF/70cm )
            
        # Power level
        power_level = attr_dict['Power']
        if power_level in ['Turbo','High']:
            row_list.append("High")
        else:
            row_list.append("Low")
        row_list.append("Always Allow")   # TX Admit
        row_list.append("Off")            # Reverse Burst/Turn off code
        row_list.append("180")            # TX Time-out Time[s]
        row_list.append("0")              # TOT Re-key Time[s]
        row_list.append("10")             # TOT Pre-Alert Time[s]
        row_list.append("120")            # CTCSS Tail Revert Option
        
        # now add the row for this channel to our analog channels list
        analog_channels_out_list.append(row_list)
        
    # create the analog channels data frame   
    analog_channels_out_df = pandas.DataFrame(analog_channels_out_list, 
                                              columns=analog_header_row)
    
    # setup digital channels dataframe
    digital_channels_out_list = []
    cnt = 1
    for ch_name in sorted(channels_dict.keys()):
        ch_type = channels_dict[ch_name]['Ch Type']
        
        # skip analog channels
        if ch_type != 'Digital':
            continue

        # get channel attributes dictionary
        attr_dict = channels_dict[ch_name]
        
        # now fill out this row in correct order for cs800d
        row_list = []
        row_list.append(str(cnt))
        cnt = cnt + 1
        row_list.append(ch_name)            # Channel Alias
        row_list.append("0")                # Digital ID
        row_list.append(attr_dict['Color Code'])    # Color Code
        if str(attr_dict['Time Slot']) == '1':      # Time Slot
            row_list.append("Slot 1")
        else:
            row_list.append("Slot 2")
        row_list.append("None")             # Scan List
        row_list.append("Off")              # Auto Scan Start
        row_list.append(attr_dict['RX Only'])       # Rx Only
        row_list.append("Off")              # Talk around
        row_list.append("Off")              # Lone Worker
        row_list.append("Off")              # VOX
        row_list.append(attr_dict['RX Freq'])       # Receive Frequency

        # compute RX Ref Frequency
        if float(attr_dict['RX Freq']) > 180.0:
            row_list.append("Middle")   # RX Ref Frequency (VHF/2 meters)
        else:
            row_list.append("Middle")   # RX Ref Frequency (UHF/70cm )

        row_list.append("None")             # RX Receive Group
        row_list.append("Off")              # Emergency Alarm Indication
        row_list.append("Off")              # Emergency Alarm Ack
        row_list.append("Off")              # Emergency Call Indication
        row_list.append(attr_dict['TX Freq'])       # Transmit Frequency

        # compute TX Ref Frequency
        if float(attr_dict['TX Freq']) > 180.0:
            row_list.append("Middle")   # TX Ref Frequency (VHF/2 meters)
        else:
            row_list.append("Middle")   # TX Ref Frequency (UHF/70cm )

        row_list.append(attr_dict['Talk Group'])  # TX Contact
        row_list.append("None")             # Emergency System
        
        # Power level
        power_level = attr_dict['Power']
        if power_level in ['Turbo','High']:
            row_list.append("High")
        else:
            row_list.append(power_level)
        
        # TX Admit (admit criteria)
        dict_admit_criteria = attr_dict['TX Permit']
        admit_criteria = "ERROR!"  # just in case...
        if dict_admit_criteria == "Always":
            admit_criteria = "Always"
        elif dict_admit_criteria in ['ChannelFree','Different Color Code']:
            admit_criteria = "Channel Idle"
        elif dict_admit_criteria == "Same Color Code":
            admit_criteria = "Color Code Free"
        row_list.append(admit_criteria)     # TX Admit

        row_list.append("180")              # TX Time-out Time[s]
        row_list.append("0")                # TOT Re-key Time[s]
        row_list.append("10")               # TOT Pre-Alert Time[s]
        row_list.append("Off")              # Private Call Confirmed
        row_list.append("Off")              # Data Call Confirmed
        row_list.append("Off")              # Encrypt
        
        # now add the row for this channel to our digital channels list
        digital_channels_out_list.append(row_list)
        
    # create the digital channels data frame   
    digital_channels_out_df = pandas.DataFrame(digital_channels_out_list, 
                                               columns=digital_header_row)
    
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    if debug:
        print("Writing output to: ", channels_export_file)
    writer = pandas.ExcelWriter(channels_export_file, engine='xlsxwriter')
    analog_channels_out_df.to_excel(writer, 
        sheet_name="Analog Channel", index=False)
    digital_channels_out_df.to_excel(writer, 
        sheet_name="Digital Channel", index=False)
    
    writer.save()
    
    return



def cs800d_write_talk_groups_export(talk_groups_dict,talk_groups_export_file, debug=False):
    """This function writes out a Connect Systems CS800D formatted talk groups import file."""

    # Create a dataframe from the talk groups dict and output it...
    header_row = ['No','Call Alias','Call Type','Call ID','Receive Tone']
    talk_groups_out_list = []
    cnt = 1
    for tg_id in sorted(talk_groups_dict.keys()):
        row_list = []
        #row_list.append(str(cnt))
        row_list.append(cnt)
        cnt = cnt + 1
        tg_name = talk_groups_dict[tg_id][0]
        if len(tg_name) > 16:
            print("WARNING:  TG Name '{}' > 16, truncating to '{}'".format(tg_name,tg_name[:16]))
        row_list.append(tg_name[:16])
        tg_call_type = talk_groups_dict[tg_id][1]
        row_list.append(tg_call_type)
        row_list.append(tg_id)
        tg_call_alert = talk_groups_dict[tg_id][2]
        if tg_call_alert == "None":
            tg_call_alert = "No"
        else:
            tg_call_alert = "Yes"
        row_list.append(tg_call_alert)
        talk_groups_out_list.append(row_list)
    talk_groups_out_df = pandas.DataFrame(talk_groups_out_list, columns=header_row)

    if debug:
        print("Writing output to: ", talkgroups_export_file)
        
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pandas.ExcelWriter(talk_groups_export_file, engine='xlsxwriter')
    talk_groups_out_df.to_excel(writer, sheet_name="DMR_Contacts", index=False)
    writer.save()
    
    return



def read_zone_order_file(file_path, debug=False):
    """This function reads the Zone_Order.csv file and builds the zones_order_list."""
   
    # read in the Zone_Order.csv file
    if debug:
        print("Processing: {}".format(file_path))
    zones_order_df = pandas.read_csv(file_path)

    # loop through k7abd file rows
    zones_order_list = []
    for i,row in zones_order_df.iterrows():

        # get zone
        zone_name = row['Zone Name']
        zones_order_list.append(zone_name)
    
    if debug:
        print("   Returning zones_order_list: {}".format(zones_order_list))
        
    return zones_order_list



def add_channel_to_zone(zone_name, channel_name, zones_dict, 
        channels_dict, debug=False):
    """This function adds a channel to our zone dictionary."""   
    
    # get the channel's rx & tx frequencies
    channel_rx_freq = str(channels_dict[channel_name]['RX Freq'])
    channel_tx_freq = str(channels_dict[channel_name]['TX Freq'])
    
    if zone_name in zones_dict.keys():
        # zone already created, just append channel, 
        # rx freq, & tx freq to lists
        zone_member_list = zones_dict[zone_name][0]
        zone_member_list.append(channel_name)
        zone_member_rx_list = zones_dict[zone_name][1]
        zone_member_rx_list.append(channel_rx_freq)
        zone_member_tx_list = zones_dict[zone_name][2]
        zone_member_tx_list.append(channel_tx_freq)
        if debug:
            print("Zone '{}' updated with '{}'.".format(
                zone_name, channel_name))
            print("    zone_dict[{}] = {}".format(
                zone_name, zones_dict[zone_name]))
    else:
        # new zone, so create it
        zones_dict.update({zone_name:
            [[channel_name],[channel_rx_freq],[channel_tx_freq]]})
        
    return



def add_channels_fm_k7abd_analog_file(k7abd_analog_file_name, channels_dict, 
                                      zones_dict, debug=False):
    """This function adds new analog channels from a K7ABD analog file."""
   
    # read in the k7abd analog  file
    k7abd_df = pandas.read_csv(k7abd_analog_file_name)

    # loop through k7abd file rows
    for i,row in k7abd_df.iterrows():

        # get zone
        zone_name = row['Zone']

        # Set channel values 
        ch_type = "Analog"
        ch_name = row['Channel Name']
        ch_rx_freq = row['RX Freq']
        ch_tx_freq = row['TX Freq']
        ch_tx_pwr = row['Power']
        ch_bandwidth = row['Bandwidth']
        ch_ctcss_dcs_decode = row['CTCSS Decode']
        ch_ctcss_dcs_encode = row['CTCSS Encode']
        ch_tx_prohibit = row['TX Prohibit'] 

        if ch_name in channels_dict.keys():
            if debug:
                print("WARNING:  channel {} already defined.".format(
                    ch_name))
        else:
            # Create a new analog channel in our channels_dict
            channels_dict.update({ch_name : {
                 'Ch Type':ch_type, 
                 'RX Freq':ch_rx_freq, 
                 'TX Freq':ch_tx_freq, 
                 'Power':ch_tx_pwr,
                 'Bandwidth':ch_bandwidth,
                 'CTCSS Decode':ch_ctcss_dcs_decode,
                 'CTCSS Encode':ch_ctcss_dcs_encode,
                 'RX Only':ch_tx_prohibit
                 }})

        # add this channel to the specified zone
        add_channel_to_zone(zone_name, ch_name, zones_dict, 
            channels_dict, debug=False)
        
    return



def add_talkgroups_fm_k7abd_talkgroups_file(k7abd_tg_file, tg_by_num_dict, tg_by_name_dict, 
                                            debug=False):
    """This function reads a talk groups file in K7ABD format."""

    # Debug output
    if debug:
        print("Processing: {}".format(k7abd_tg_file))
        
    # Read in the K7ABD talk groups file... 
    tg_df = pandas.read_csv(k7abd_tg_file, header=None) 

    # hack to protect Private Call entries (like Brandmeister Parrot)
    private_call_list = [9990]
    
    # loop through the talk groups building dictionaries
    for i, row in tg_df.iterrows():
        tg_name = row[0]
        tg_number = row[1]
        if tg_number not in private_call_list:
            tg_call_type = "Group Call"
        else:
            tg_call_type = "Private Call"
        tg_call_alert = "None"

        # check the talk group name for valid length...
        if len(tg_name) > 16:
            print("WARNING: ",tg_name,"exceeds 16 characters. Length = ",len(tg_name))
            print("   truncating to: ",str(tg_name[:16]))

        # First definition of a talk group name sets the name that will
        # be used for that talk group number in any channel definitions.
        # We allow multiple names for the same talk group number.  
        # Redefinitions for any talk group name must always equate to
        # the same talk group number.
        if tg_number not in tg_by_num_dict.keys():

            # sanity check: if tg name already exists it appears in this
            # case to have been defined as a different number...
            # That isn't allowed, so ERROR out. 
            if tg_name in tg_by_name_dict.keys():
                print("ERROR:  Talkgroup '{}' already defined as: '{}'".format(
                    tg_name, tg_by_name_dict[tg_name]))
                sys.exit(-1)

            # now safe to add to tg_by_num_dict - becomes default TG name 
            tg_by_num_dict.update({tg_number:
                [str(tg_name[:16]), tg_call_type, tg_call_alert]})
        else:

            # sanity check: if tg_name already exists in this case,
            # we need to make sure this repeat definition equates 
            # to the same talk group number
            if tg_name in tg_by_name_dict.keys():

                if tg_by_name_dict[tg_name] != tg_number:
                    print("ERROR:  Talkgroup '{}' already defined as: '{}'".format(
                        tg_name, tg_by_name_dict[tg_name]))
                    sys.exit(-1)

        # passed sanity checks, safe to add to tg_by_name_dict
        tg_by_name_dict.update({tg_name[:16]:tg_number})
    
    # clean up
    del tg_df

    return         
  

  
    
def add_channels_fm_k7abd_digital_others_file(k7abd_digital_others_file_name, 
        channels_dict, zones_dict, tg_by_num_dict, tg_by_name_dict, 
        debug=False):
    """This function writes out a k7abd formatted Digital-Others__ file"""

    # Reference of file format - column headings in digital-others file:
    # ['Zone','Channel Name','Power','RX Freq','TX Freq','Color Code',
    #  'Talk Group','TimeSlot','Call Type','TX Permit']
    
    # read in the K7ABD digital-others file
    if debug:
        print("Processing: {}".format(k7abd_digital_others_file_name))
    k7abd_df = pandas.read_csv(k7abd_digital_others_file_name)
    
    # loop through k7abd file rows
    for i,row in k7abd_df.iterrows():

        # get "Zone" value
        zone_name = row['Zone']
        
        # channel name
        ch_name = row['Channel Name']
        if len(ch_name) >16:
            print("Warning: '{}' exceeds 16 chars({}).".format(
                ch_name, len(ch_name)))
            ch_name = ch_name[:16]

        # set channel type
        ch_type = "Digital"

        # set bandwidth
        ch_bandwidth = "12.5"

        # get "contact" value (mapped if needed)
        tg_name = row['Talk Group']
        if tg_name in tg_by_name_dict.keys():
            # lookup TG number and remap name to value in tg_by_num_dict
            tg_name = tg_by_num_dict[tg_by_name_dict[tg_name]][0]
        else:
            # Bad day...
            print("ERROR: Undefined talk group: '{}'".format(tg_name))
        ch_contact = tg_name
        
        # get channel attributes 
        ch_tx_power = row['Power']
        ch_rx_freq = row['RX Freq']
        ch_tx_freq = row['TX Freq']
        ch_tx_pwr = row['Power']
        ch_color_code = row['Color Code']
        ch_slot = row['TimeSlot']
        ch_call_type = row['Call Type']
        ch_contact_tg_num = str(tg_by_name_dict[tg_name])
        ch_tx_permit = row['TX Permit']

        # now add this channel to the channel dictionary
        if ch_name in channels_dict.keys():
            if debug:
                print("WARNING:  channel {} already defined.".format(
                    ch_name))
        else:
            # Create a new digital channel in our channels_dict
            channels_dict.update({ch_name : {
                 'Ch Type':ch_type, 
                 'RX Freq':ch_rx_freq, 
                 'TX Freq':ch_tx_freq, 
                 'Power':ch_tx_pwr,
                 'Bandwidth':ch_bandwidth,
                 'Color Code':ch_color_code,
                 'Talk Group':ch_contact,
                 'Time Slot':ch_slot,
                 'Call Type':ch_call_type,
                 'TX Permit':ch_tx_permit,
                 'RX Only':"Off"
                 }})

        # add this channel to the specified zone
        add_channel_to_zone(zone_name, ch_name, zones_dict, 
            channels_dict, debug=False)
     
    # clean-up
    del k7abd_df
    
    return



def add_channels_fm_k7abd_digital_repeaters_file(k7abd_digital_file_name, 
        channels_dict, zones_dict, tg_by_num_dict, tg_by_name_dict, 
        debug=False):

    # read in the k7abd digital repeaters file
    if debug:
        print("Processing: {}".format(k7abd_digital_file_name))
    k7abd_df = pandas.read_csv(k7abd_digital_file_name)
    k7abd_df['Comment'].fillna('none', inplace=True)   

    # loop through k7abd repeaters file rows
    for i,row in k7abd_df.iterrows():

        # pull out channel prefix
        zone_name = row['Zone Name']
        zone_name_list = zone_name.split(';')
        zone_name = zone_name_list[0]
        ch_prefix = zone_name_list[1]
        if debug:
            print("   Working on Zone: ", zone_name)

        # set channel type
        ch_type = "Digital"

        # get "Transmit Power" value
        ch_tx_power = row['Power']

        # get "Receive Frequency" & "Transmit Frequency"
        ch_rx_freq = row['RX Freq']
        ch_tx_freq = row['TX Freq']

        # get "Color Code" value
        ch_color_code = row['Color Code']

        # Now loop through rest of columns in k7abd repeaters file and create
        # a channel for each talk group represented that has a slot specified..
        talk_groups = []
        column_items = k7abd_df.columns
        for item in column_items:
            if item not in ['Zone Name','Comment','Power',
                             'RX Freq','TX Freq','Color Code']:
                talk_groups.append(item)

        for item in talk_groups:

            # Set talk group name to 1st part of column heading 
            # if ';' present in the K7ABD file
            item_list = item.split(';')
            tg_name = item_list[0]

            ch_slot = row[item]
            if ch_slot not in ['1','2']:
               # this talk group not on this repeater, so 
               # don't create a channel for it...
               pass

            # fix tg_name value - map if needed
            if tg_name in tg_by_name_dict.keys():
                # lookup TG number and remap name to first value in 
                # our tg_by_num_dict
                tg_name = tg_by_num_dict[tg_by_name_dict[tg_name]][0]
            else:
                # Bad day...
                print("ERROR: Undefined talk group: '{}'".format(tg_name))
                sys.exit(-1)

            # channel name
            ch_name = ch_prefix + ' ' + tg_name
            if len(ch_name) >16:
                print("Warning: '{}' > 16 chars, changed to '{}'.".format(
                    ch_name, ch_name[:16]))
                ch_name = ch_name[:16]

            # now add this channel to the channel dictionary
            if ch_name in channels_dict.keys():
                if debug:
                    print("WARNING:  channel {} already defined.".format(
                        ch_name))
            else:
                # Create a new digital channel in our channels_dict
                channels_dict.update({ch_name : {
                    'Ch Type':ch_type, 
                    'RX Freq':ch_rx_freq, 
                    'TX Freq':ch_tx_freq, 
                    'Power':ch_tx_power,
                    'Bandwidth':"12.5",
                    'Color Code':ch_color_code,
                    'Talk Group':tg_name,
                    'Time Slot':ch_slot,
                    'Call Type':"Group Call",
                    'TX Permit':"Color Code Free",
                    'RX Only':"Off"
                    }})

            # add this channel to the specified zone
            add_channel_to_zone(zone_name, ch_name, zones_dict, 
                channels_dict, debug=False)
                    
    # clean-up
    del k7abd_df

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
supported_cps_targets = ['878','cs800d']


def main():

    # get today's date to stamp output files with today's iso-date.
    isodate = time.strftime("%Y-%m-%d")

    # Greet the customer
    print("")
    print("CPS Import File Builder")
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
        dest='cps_target_list',
        help='Specify CPS target: 878/cs800d; multiple allowed',
        default=[])
    parser.add_argument('--inputdir', help='Directory containing input files',
        required=False, default='./input_data_files')
    parser.add_argument('--outputdir', help='Target directory for output files',
        required=False, default='./output_files')
    parser.add_argument('--debugmode', 
        help='Set debug flag for troubleshooting', required=False, 
        action='store_true')

    # parse the command line
    args = parser.parse_args()
    debugflg = args.debugmode

    # sanity check --cps target(s)
    for selection in args.cps_target_list:
        # if they specify all we just generate everything we support!
        if selection == 'all':
            args.cps_target_list = supported_cps_targets
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

    # Read in Zone Order file
    zone_order_filespec = os.path.join(inputs_dir, "Zone_Order.csv")
    print("Reading Zone Order file: {}".format( 
        os.path.basename(zone_order_filespec)))
    zones_order_list = read_zone_order_file(zone_order_filespec, debug=debugflg)

    # Add talk groups from K7ABD Talkgroups__ files
    talkgroups_filespec = os.path.join(inputs_dir, 'Talkgroups__*')
    file_list = []
    for match in glob.iglob(talkgroups_filespec, recursive=False):
        file_list.append(match)
    for talkgroups_filename in sorted(file_list):
        print("Adding talkgroups:  {}".format( 
            os.path.basename(talkgroups_filename)))
        add_talkgroups_fm_k7abd_talkgroups_file(talkgroups_filename, 
            tg_by_num_dict, tg_by_name_dict, debug=debugflg)

    # Add channels from K7ABD Analog__ files
    analog_channels_filespec = os.path.join(inputs_dir, 'Analog__*')
    file_list = []
    for match in glob.iglob(analog_channels_filespec, recursive=False):
        file_list.append(match)
    for analog_channels_filename in sorted(file_list):
        print("Adding channels:  {}".format( 
            os.path.basename(analog_channels_filename)))
        add_channels_fm_k7abd_analog_file(analog_channels_filename, 
            channels_dict, zones_dict, debug=debugflg)
    
    # Add channels from K7ABD Digital-Others__ files
    digital_others_filespec = os.path.join(inputs_dir, 'Digital-Others__*')
    file_list = []
    for match in glob.iglob(digital_others_filespec, recursive=False):
        file_list.append(match)
    for digital_others_filename in sorted(file_list):
        print("Adding channels:  {}".format( 
            os.path.basename(digital_others_filename)))
        add_channels_fm_k7abd_digital_others_file(digital_others_filename, 
            channels_dict, zones_dict, tg_by_num_dict, tg_by_name_dict, 
            debug=debugflg)
    
    # Add channels from K7ABD Digital-Repeaters files
    digital_repeaters_filespec = os.path.join(inputs_dir, 
        'Digital-Repeaters__*')
    file_list = []
    for match in glob.iglob(digital_repeaters_filespec, recursive=False):
        file_list.append(match)
    for digital_repeaters_filename in sorted(file_list):
        print("Adding channels:  {}".format(
            os.path.basename(digital_repeaters_filename)))
        add_channels_fm_k7abd_digital_repeaters_file(
            digital_repeaters_filename, channels_dict, zones_dict, 
            tg_by_num_dict, tg_by_name_dict, debug=debugflg)

    # Generate import files for Connect Systems CS800D
    if 'cs800d' in args.cps_target_list:

        print("")
        print("Generating import files for Connect Systems CS800D")

        # define our export file names 
        talk_groups_output_filename = 'cs800d_talk_groups_{}.xlsx'.format(
            isodate)
        talk_groups_output_file = os.path.join(outputs_dir, 
        talk_groups_output_filename)
        channels_output_filename = 'cs800d_channels_{}.xlsx'.format(isodate)
        channels_output_file = os.path.join(outputs_dir, 
            channels_output_filename) 
    
        # Write out a CS800D talk groups import file
        print("   Talk group import file: {}".format(
            os.path.basename(talk_groups_output_file)))
        cs800d_write_talk_groups_export(tg_by_num_dict, 
            talk_groups_output_file, debug=False)
    
        # Write out a CS800D channel import file
        print("   Channels import file: {}".format(
            os.path.basename(channels_output_file)))
        cs800d_write_channels_export(channels_dict, 
            channels_output_file, debug=False)

    if '878' in args.cps_target_list:

        print("")
        print("Generating import files for Anytone D878UV")

        # define our export file names 
        talk_groups_output_filename = 'd878uv_talk_groups_{}.xlsx'.format(
            isodate)
        talk_groups_output_file = os.path.join(outputs_dir, 
        talk_groups_output_filename)
        channels_output_filename = 'd878uv_channels_{}.xlsx'.format(isodate)
        channels_output_file = os.path.join(outputs_dir, 
            channels_output_filename) 

    print("")
    print("All done!")
    print("")



# if this file isn't being imported as a module then call ourselves as the main thing...
if __name__ == "__main__":
   main()

