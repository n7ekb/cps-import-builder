#!/usr/bin/env python
# coding: utf-8

# In[2]:


# This notebook contains code that reads in K7ABD formatted Anytone Config
# Builder files into a generic in-memory set of python DMR codeplug structures 
# and then generates files suitable for import into the Anytone CPS.
# 



import pandas 
import csv
import sys
import os 
import time
import glob
import argparse

   
    
def anytone_write_zones_export(zones_dict, zones_order_list, zones_export_file, channels_dict, debug=False):
    """This function writes out an Anytone D878 CPS formatted zones import/export file"""

    if debug:
            print("Preparing Zones Export File...")
            
    # Create a dataframe from the zones dict 
    header_row = ['No.','Zone Name','Zone Channel Member','Zone Channel Member RX Frequency',
                  'Zone Channel Member TX Frequency','A Channel','A Channel RX Frequency',
                  'A Channel TX Frequency','B Channel','B Channel RX Frequency','B Channel TX Frequency']
    zones_out_dict = {}
    zones_not_ordered_list = []
    cnt = 1
    for zone_name in zones_dict.keys():
        if debug:
            print("   Adding zone {} with following members:".format(zone_name))
            print("   ", zones_dict[zone_name])
        row_list = []
        row_list.append(str(cnt))
        cnt = cnt + 1
        row_list.append(zone_name)
        
        # build Zone Channel Member string from list
        member_str = '|'.join(zones_dict[zone_name][0])
        if debug:
            print("   Member string: '{}'".format(member_str))
        row_list.append(member_str)
        
        # build Zone Channel Rx Freq string
        rx_freq_str = '|'.join(zones_dict[zone_name][1])
        row_list.append(rx_freq_str)
        
        # build Zone Channel Tx Freq string
        tx_freq_str = '|'.join(zones_dict[zone_name][2])
        row_list.append(tx_freq_str)
        
        # now use first member channel info as the "A" & "B" VFO default
        first_member_name = zones_dict[zone_name][0][0]
        row_list.append(first_member_name)
        row_list.append(channels_dict[first_member_name][0])
        row_list.append(channels_dict[first_member_name][1])
        row_list.append(first_member_name)
        row_list.append(channels_dict[first_member_name][0])
        row_list.append(channels_dict[first_member_name][1])
        zones_out_dict.update({zone_name:row_list})
        if zone_name not in zones_order_list:
            zones_not_ordered_list.append(row_list)
        
    # Build zones_out_list to match zones_order_list; all the rest of the zones
    # go to bottom of list in the order they were processed
    zones_out_list = []
    for zone_name in zones_order_list:
        if zone_name in zones_out_dict.keys():
            if debug:
                print("   Adding zone to zones_out_list: {}".format(zone_name))
            zones_out_list.append(zones_out_dict[zone_name])
        else:
            print("Warning:  Zone '{}' specified in Zones_Order.csv file not used!".format(zone_name))
    for i in range(len(zones_not_ordered_list)):
        if debug:
            print("   Adding zone to zones_out_list: {}".format(zones_not_ordered_list[i][1]))
        zones_out_list.append(zones_not_ordered_list[i])
    
    # Output our Zones dataframe
    zones_out_df = pandas.DataFrame(zones_out_list, columns=header_row)
    
    # renumber the "No." column to match new order
    for i in range(len(zones_out_df.index)):
        zones_out_df.at[i, 'No.'] = i+1
    
    if debug:
        print("Writing output to: ", zones_export_file)
    zones_out_df.to_csv(zones_export_file, index=False, header=True, quoting=csv.QUOTE_ALL,
                   line_terminator='\r\n')

    # clean up... 
    del zones_out_list
    del zones_out_df

    return

 
    
def anytone_write_rx_groups_export(rx_groups_dict, rx_groups_export_file, debug=False):
    """This function writes out an Anytone D878 CPS formatted rx groups import/export file"""

    # Create a dataframe from the rx groups dict and output it...
    header_row = ['No.','Group Name','Contact']
    rx_groups_out_list = []
    cnt = 1
    for group_name in rx_groups_dict.keys():
        row_list = []
        row_list.append(str(cnt))
        cnt = cnt + 1
        row_list.append(group_name)
        member_str = '|'.join(rx_groups_dict[group_name])
        row_list.append(member_str)
        rx_groups_out_list.append(row_list)
    rx_groups_out_df = pandas.DataFrame(rx_groups_out_list, columns=header_row)
    if debug:
        print("Writing output to: ", rx_groups_export_file)
    rx_groups_out_df.to_csv(rx_groups_export_file, index=False, header=True, quoting=csv.QUOTE_ALL,
                   line_terminator='\r\n')

    # clean up... 
    del rx_groups_out_list
    del rx_groups_out_df
    # write the file out

    return 



def anytone_write_scan_lists_export(scan_lists_dict, scan_lists_export_file, debug=False):
    """This function writes out an Anytone D878 CPS formatted scan lists import/export file"""

    # These are scan list column headings for CPS 1.21:
    #
    # "No.","Scan List Name", "Scan Channel Member","Scan Channel Member RX Frequency",
    # "Scan Channel Member TX Frequency","Scan Mode","Priority Channel Select",
    # "Priority Channel 1","Priority Channel 1 RX Frequency","Priority Channel 1 TX Frequency",
    # "Priority Channel 2","Priority Channel 2 RX Frequency","Priority Channel 2 TX Frequency",
    # "Revert Channel","Look Back Time A[s]","Look Back Time B[s]","Dropout Delay Time[s]",
    # "Dwell Time[s]"
    
    # Create a dataframe from the scan lists dict and output it...
    header_row = ['No.','Scan List Name','Scan Channel Member','Scan Channel Member RX Frequency',
                  'Scan Channel Member TX Frequency','Scan Mode','Priority Channel Select',
                  'Priority Channel 1','Priority Channel 1 RX Frequency','Priority Channel 1 TX Frequency',
                  'Priority Channel 2','Priority Channel 2 RX Frequency','Prioirty Channel 2 TX Frequency',
                  'Revert Channel','Look Back Time A[s]','Look Back Time B[s]','Dropout Delay Time[s]',
                  'Dwell Time[s]']
    scan_lists_out_list = []
    cnt = 1
    for list_name in scan_lists_dict.keys():
        row_list = []
        row_list.append(str(cnt))
        cnt = cnt + 1
        row_list.append(list_name)
        
        # build and append channel members
        member_str = '|'.join(scan_lists_dict[list_name][0])
        row_list.append(member_str)
        
        # build and append channel member rx freqs
        rx_freq_str = '|'.join(scan_lists_dict[list_name][1])
        row_list.append(rx_freq_str)
        
        # build and append channel member tx freqs
        tx_freq_str = '|'.join(scan_lists_dict[list_name][2])
        row_list.append(tx_freq_str)
        
        # append the rest of the items from the dictionary value list...
        for i in range(len(scan_lists_dict[list_name]) - 3):
            row_list.append(scan_lists_dict[list_name][i+3])
        scan_lists_out_list.append(row_list)

    scan_lists_out_df = pandas.DataFrame(scan_lists_out_list, columns=header_row)
    if debug:
        print("Writing output to: ", scan_lists_export_file)
    scan_lists_out_df.to_csv(scan_lists_export_file, index=False, header=True, quoting=csv.QUOTE_ALL,
                   line_terminator='\r\n')

    # clean up... 
    del scan_lists_out_list
    del scan_lists_out_df

    return

      
    
    
def anytone_write_talk_groups_export(talk_groups_dict, talk_groups_export_file, debug=False):
    """This function writes out an Anytone D878 CPS formatted talk groups import/export file"""

    # Create a dataframe from the talk groups dict and output it...
    header_row = ['No.','Radio ID','Name','Call Type','Call Alert']
    talk_groups_out_list = []
    cnt = 1
    for tg_id in sorted(talk_groups_dict.keys()):
        row_list = []
        row_list.append(str(cnt))
        cnt = cnt + 1
        row_list.append(tg_id)
        tg_name = talk_groups_dict[tg_id][0]
        if len(tg_name) > 16:
            print("WARNING:  TG Name '{}' > 16, truncating to '{}'".format(tg_name,tg_name[:16]))
        row_list.append(tg_name[:16])
        tg_call_type = talk_groups_dict[tg_id][1]
        row_list.append(tg_call_type)
        tg_call_alert = talk_groups_dict[tg_id][2]
        row_list.append(tg_call_alert)
        talk_groups_out_list.append(row_list)
    talk_groups_out_df = pandas.DataFrame(talk_groups_out_list, columns=header_row)
    #talk_groups_out_df.sort_values(by='Radio ID', inplace=True)
    if debug:
        print("Writing output to: ", talk_groups_export_file)
    talk_groups_out_df.to_csv(talk_groups_export_file, index=False, header=True, quoting=csv.QUOTE_ALL,
                   line_terminator='\r\n')

    # clean up... 
    del talk_groups_out_list
    del talk_groups_out_df

    return

    
    

def anytone_write_radio_id_list_export(radio_ids_dict, radio_id_list_export_file, debug=False):
    """This function writes out an Anytone D878 CPS formatted radio ID list import/export file"""

    # Create a dataframe from the radio id dict and output it...
    header_row = ['No.','Radio ID','Name']
    radio_id_out_list = []
    cnt = 1
    for radio_id in radio_ids_dict.keys():
        row_list = []
        row_list.append(str(cnt))
        cnt = cnt + 1
        row_list.append(radio_ids_dict[radio_id])
        row_list.append(radio_id)
        radio_id_out_list.append(row_list)
    radio_id_out_df = pandas.DataFrame(radio_id_out_list, columns=header_row)
    if debug:
        print("Writing output to: ", radio_id_list_export_file)
    radio_id_out_df.to_csv(radio_id_list_export_file, index=False, header=True, quoting=csv.QUOTE_ALL,
                   line_terminator='\r\n')

    # clean up... 
    del radio_id_out_list
    del radio_id_out_df

    return
  

    
def anytone_write_channels_export(channels_dict, channels_export_file, debug=False):
    """This function writes out an Anytone D878 CPS formatted channels import/export file"""
    
    # Create a dataframe from the channels dict and output it...
    header_row = ['No.','Channel Name','Receive Frequency','Transmit Frequency',
                  'Channel Type','Transmit Power','Band Width','CTCSS/DCS Decode',
                  'CTCSS/DCS Encode','Contact','Contact Call Type','Contact TG/DMR ID','Radio ID',
                  'Busy Lock/TX Permit','Squelch Mode','Optional Signal',"DTMF ID",
                  '2Tone ID','5Tone ID','PTT ID','Color Code','Slot','Scan List',
                  'Receive Group List','PTT Prohibit','Reverse','Simplex TDMA',
                  'Slot Suit','AES Digital Encryption','Digital Encryption',
                  'Call Confirmation','Talk Around(Simplex)','Work Alone','Custom CTCSS',
                  '2TONE Decode','Ranging','Through Mode','Digi APRS RX',
                  'Analog APRS PTT Mode','Digital APRS PTT Mode','APRS Report Type',
                  'Digital APRS Report Channel','Correct Frequency[Hz]',
                  'SMS Confirmation','Exclude channel from roaming',
                  'DMR MODE','DataACK Disable','R5toneBot','R5ToneEot'] 
    channels_out_list = []
    cnt = 1
    for channel in channels_dict.keys():
        row_list = []
        row_list.append(str(cnt))
        cnt = cnt + 1
        row_list.append(channel)
        for attr in channels_dict[channel]:
            row_list.append(attr)
        channels_out_list.append(row_list)
    channels_out_df = pandas.DataFrame(channels_out_list, columns=header_row)

    # Group channels by Channel Type (analog then digital)
    channels_out_df.sort_values(by=['Channel Type','Channel Name'], inplace=True)
    channels_out_df.reset_index(drop=True, inplace=True)

    # renumber the "No." column to match new order
    for i in range(len(channels_out_df.index)):
        channels_out_df.at[i, 'No.'] = i+1


    if debug:
        print("Writing output to: ", channels_export_file)
    channels_out_df.to_csv(channels_export_file, index=False, header=True, quoting=csv.QUOTE_ALL,
                   line_terminator='\r\n')

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



def add_channel_to_zone(zone_name, channel_name, zones_dict, channels_dict, debug=False):
    """This function adds a channel to our zone dictionary."""   
    
    # get the channel's rx & tx frequencies
    channel_rx_freq = str(channels_dict[channel_name][0])
    channel_tx_freq = str(channels_dict[channel_name][1])
    
    if zone_name in zones_dict.keys():
        # zone already created, just append channel, rx freq, & tx freq to lists
        zone_member_list = zones_dict[zone_name][0]
        zone_member_list.append(channel_name)
        zone_member_rx_list = zones_dict[zone_name][1]
        zone_member_rx_list.append(channel_rx_freq)
        zone_member_tx_list = zones_dict[zone_name][2]
        zone_member_tx_list.append(channel_tx_freq)
        if debug:
            print("Zone '{}' updated with '{}'.".format(zone_name, channel_name))
            print("    zone_dict[{}] = {}".format(zone_name, zones_dict[zone_name]))
    else:
        # new zone, so create it
        zones_dict.update({zone_name:[[channel_name],[channel_rx_freq],[channel_tx_freq]]})
        
    return



def add_channel_to_zone_scanlist(zone_name, channel_name, zones_dict, channels_dict, 
                                 scan_lists_dict, debug=False):
    """This function adds a channel to a scanlist for the zone."""   
    
    # These are scan list column headings for CPS 1.21:
    #
    # "No.","Scan List Name","Scan Channel Member","Scan Channel Member RX Frequency",
    # "Scan Channel Member TX Frequency","Scan Mode","Priority Channel Select",
    # "Priority Channel 1","Priority Channel 1 RX Frequency","Priority Channel 1 TX Frequency",
    # "Priority Channel 2","Priority Channel 2 RX Frequency","Priority Channel 2 TX Frequency",
    # "Revert Channel","Look Back Time A[s]","Look Back Time B[s]","Dropout Delay Time[s]",
    # "Dwell Time[s]"
    
    # get the channel's rx & tx frequencies
    channel_rx_freq = str(channels_dict[channel_name][0])
    channel_tx_freq = str(channels_dict[channel_name][1])
    
    # set fixed item values
    scan_mode = "Off"
    priority_ch_select = "Off"
    priority_ch_1 = "Off"
    priority_ch_1_rx_freq = ""
    priority_ch_1_tx_freq = ""
    priority_ch_2 = "Off"
    priority_ch_2_rx_freq = ""
    priority_ch_2_tx_freq = ""
    revert_ch = "Selected"
    loop_back_time_a = "2.0"
    loop_back_time_b = "3.0"
    drop_out_delay = "3.1"
    dwell_time = "3.1"
    
    if zone_name in scan_lists_dict.keys():
        # scan list for this zone already created, so we append new channel
        # after building up list of lists/items
        scan_member_list = scan_lists_dict[zone_name][0]
        scan_member_list.append(channel_name)
        scan_member_rx_list = scan_lists_dict[zone_name][1]
        scan_member_rx_list.append(channel_rx_freq)
        scan_member_tx_list = scan_lists_dict[zone_name][2]
        scan_member_tx_list.append(channel_tx_freq)   
        scan_list_entry = [scan_member_list, scan_member_rx_list, scan_member_tx_list,
                           scan_mode, priority_ch_select, 
                           priority_ch_1, priority_ch_1_rx_freq, priority_ch_1_rx_freq,
                           priority_ch_2, priority_ch_2_rx_freq, priority_ch_2_tx_freq, 
                           revert_ch, loop_back_time_a, loop_back_time_b, drop_out_delay, dwell_time]
        scan_lists_dict[zone_name] = scan_list_entry
        if debug:
            print("Scan list '{}' updated with '{}'.".format(zone_name, channel_name))
            print("    scan_lists_dict[{}] = {}".format(zone_name, zones_dict[zone_name]))
    else:
        # new zone, so create it
        scan_lists_dict.update({zone_name:[[channel_name], [channel_rx_freq], [channel_tx_freq],
                           scan_mode, priority_ch_select, 
                           priority_ch_1, priority_ch_1_rx_freq, priority_ch_1_rx_freq,
                           priority_ch_2, priority_ch_2_rx_freq, priority_ch_2_tx_freq, 
                           revert_ch, loop_back_time_a, loop_back_time_b, drop_out_delay, dwell_time]})
        
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
        ch_name = row['Channel Name']
        ch_rx_freq = row['RX Freq']
        ch_tx_freq = row['TX Freq']
        ch_type = "A-Analog"
        ch_tx_pwr = row['Power']
        ch_bandwidth = row['Bandwidth']
        ch_ctcss_dcs_decode = row['CTCSS Decode']
        ch_ctcss_dcs_encode = row['CTCSS Encode']
        ch_contact = "0_Analog"
        ch_contact_call_type = "Group Call"
        ch_contact_tg_num = 0
        ch_radio_id = "none" 
        ch_tx_permit = "Off" 
        if ch_ctcss_dcs_decode == "Off":
            ch_squelch_mode = "Carrier"
        else:
            ch_squelch_mode = "CTCSS/DCS"
        ch_optional_sig = "Off" 
        ch_dtmf_id = "1"
        ch_2tone_id = "1"
        ch_5tone_id = "1" 
        ch_ptt_id = "Off"
        ch_color_code = "1"
        ch_slot = "1"
        ch_scan_list = zone_name
        ch_rx_group = "None"
        ch_ptt_prohibit = row['TX Prohibit']
        ch_reverse = "Off"
        ch_simplex_tdma = "Off"
        ch_tdma_adaptive = "Off"
        ch_aes_encrypt = "Normal Encryption"
        ch_digital_encrypt = "Off"
        ch_call_confirm = "Off"
        ch_talk_around = "Off"
        ch_work_alone = "Off"
        ch_custom_ctcss = "251.1"
        ch_2tone_decode = "1"
        ch_ranging = "Off"
        ch_through_mode = "Off"
        ch_digi_aprs_rx = "Off"
        ch_analog_aprs_ptt = "Off"
        ch_digital_aprs_ptt = "Off"
        ch_aprs_rpt_type = "Off"
        ch_digi_aprs_rpt_ch = "1"
        ch_correct_freq = "0"
        ch_sms_confirm = "Off"
        ch_exclude_fm_roaming = "0"
        ch_dmr_mode = "0"
        ch_dataack_disable = "0"
        ch_r5tone_bot = "0"
        ch_r5tone_eot = "0"
        if ch_name in channels_dict.keys():
            if debug:
                print("WARNING:  channel already exists: ", ch_name, "... Not overwriting.")
        channels_dict.update({ch_name : [ch_rx_freq, ch_tx_freq, ch_type, ch_tx_pwr,
                                        ch_bandwidth, ch_ctcss_dcs_decode, ch_ctcss_dcs_encode,
                                        ch_contact, ch_contact_call_type, ch_contact_tg_num, ch_radio_id, 
                                        ch_tx_permit,
                                        ch_squelch_mode, ch_optional_sig, ch_dtmf_id, ch_2tone_id,
                                        ch_5tone_id, ch_ptt_id, ch_color_code, ch_slot, ch_scan_list,
                                        ch_rx_group, ch_ptt_prohibit, ch_reverse, ch_simplex_tdma,
                                        ch_tdma_adaptive, ch_aes_encrypt, ch_digital_encrypt, 
                                        ch_call_confirm, ch_talk_around, ch_work_alone, ch_custom_ctcss,
                                        ch_2tone_decode, ch_ranging, ch_through_mode, ch_digi_aprs_rx,
                                        ch_analog_aprs_ptt, ch_digital_aprs_ptt, ch_aprs_rpt_type,
                                        ch_digi_aprs_rpt_ch, ch_correct_freq, ch_sms_confirm,
                                        ch_exclude_fm_roaming,
                                        ch_dmr_mode,ch_dataack_disable,ch_r5tone_bot,ch_r5tone_eot]})

        # add this channel to the specified zone
        add_channel_to_zone(zone_name, ch_name, zones_dict, channels_dict, debug=False)
        
        # add this channel to the scanlist for specified zone
        add_channel_to_zone_scanlist(zone_name, ch_name, zones_dict, channels_dict, 
                                    scan_lists_dict, debug=False)
        

    return



def add_talkgroups_fm_k7abd_talkgroups_file(k7abd_tg_file, tg_by_num_dict, tg_by_name_dict, debug=False):
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

        # add tg_number/tg_name to dictionaries.  First definition of talk group overrides
        # subsequent definitions, allowing multiple names for the same talk group number.
        # Duplicate talk group names must all equate to the same talk group number.
        if tg_number not in tg_by_num_dict.keys():
            tg_by_num_dict.update({tg_number:[str(tg_name[:16]), tg_call_type, tg_call_alert]})
            if tg_name not in tg_by_name_dict.keys():
                tg_by_name_dict.update({tg_name[:16]:tg_number})
            else:
                # Error if attempting to redefine talk group number
                if tg_by_name_dict[tg_name] != tg_number:
                    print("ERROR:  Talkgroup '{}' already has different number: '{}'".format(tg_name,
                          tg_by_name_dict[tg_name]))
                else:
                    print("WARNING:  Talkgroup '{}' is being mapped to '{}'".format(tg_name,
                          tg_by_num_dict[tg_number][0]))
        else:
            #print("   Talkgroup '{}' will be mapped to '{}' (TG # {}).".format(tg_name, 
            #   tg_by_num_dict[tg_number][0], tg_number))
            if tg_name not in tg_by_name_dict.keys():
                tg_by_name_dict.update({tg_name[:16]:tg_number})
            else:
                # Error if attempting to redefine talk group number
                if tg_by_name_dict[tg_name] != tg_number:
                    print("ERROR:  Talkgroup '{}' already has different number: '{}'".format(tg_name,
                          tg_by_name_dict[tg_name]))
    
    # clean up
    del tg_df

    return         
  

  
    
def add_channels_fm_k7abd_digital_others_file(k7abd_digital_others_file_name, channels_dict, zones_dict,
                                              tg_by_num_dict, tg_by_name_dict, debug=False):
    """This function writes out a k7abd formatted Digital-Others__ file"""

    # Reference of file format - column headings in digital-others file:
    # ['Zone','Channel Name','Power','RX Freq','TX Freq','Color Code',
    #  'Talk Group','TimeSlot','Call Type','TX Permit']
    
    # read in the K7ABD digital-others file
    print("Processing: {}".format(k7abd_digital_others_file_name))
    k7abd_df = pandas.read_csv(k7abd_digital_others_file_name)
    
    # Old CPS v1.18 column headers:
    #
    #       'No.','Channel Name','Receive Frequency','Transmit Frequency',
    #       'Channel Type','Transmit Power','Band Width','CTCSS/DCS Decode',
    #       'CTCSS/DCS Encode','Contact','Contact Call Type',                    'Radio ID',
    #       'Busy Lock/TX Permit','Squelch Mode','Optional Signal',"DTMF ID",
    #       '2Tone ID','5Tone ID','PTT ID','Color Code','Slot','Scan List',
    #       'Receive Group List','TX Prohibit','Reverse','Simplex TDMA',
    #       'TDMA Adaptive','AES Digital Encryption','Digital Encryption',
    #       'Call Confirmation','Talk Around','Work Alone','Custom CTCSS',
    #       '2TONE Decode','Ranging','Through Mode','Digi APRS RX',
    #       'Analog APRS PTT Mode','Digital APRS PTT Mode','APRS Report Type',
    #       'Digital APRS Report Channel','Correct Frequency[Hz]',
    #       'SMS Confirmation','Exclude channel from roaming'
    #
    # Current CPS v1.21 column headers  (additions/changes in [[]]'s):
    #
    #       "No.","Channel Name","Receive Frequency","Transmit Frequency",
    #       "Channel Type","Transmit Power","Band Width","CTCSS/DCS Decode",
    #       "CTCSS/DCS Encode","Contact","Contact Call Type", [["Contact TG/DMR ID"]],"Radio ID",
    #       "Busy Lock/TX Permit","Squelch Mode","Optional Signal","DTMF ID",
    #       "2Tone ID","5Tone ID","PTT ID","Color Code","Slot","Scan List",
    #       "Receive Group List",[["PTT Prohibit"]],"Reverse","Simplex TDMA",
    #       [["Slot Suit"]],"AES Digital Encryption","Digital Encryption",
    #       "Call Confirmation",[["Talk Around(Simplex)"]],"Work Alone","Custom CTCSS",
    #       "2TONE Decode","Ranging","Through Mode","Digi APRS RX",
    #       "Analog APRS PTT Mode","Digital APRS PTT Mode","APRS Report Type",
    #       "Digital APRS Report Channel","Correct Frequency[Hz]",
    #       "SMS Confirmation","Exclude channel from roaming",
    #       [["DMR MODE","DataACK Disable","R5toneBot","R5ToneEot"]]

    # loop through k7abd file rows
    for i,row in k7abd_df.iterrows():

        # get "Zone" value
        zone_name = row['Zone']
        
        # channel name
        channel_name = row['Channel Name']
        if len(channel_name) >16:
            print("Warning: ",channel_name,"exceeds 16 chars, ", len(channel_name))
            channel_name = channel_name[:16]

        # get "Transmit Power" value
        channel_tx_power = row['Power']

        # get "Receive Frequency" & "Transmit Frequency"
        channel_rx_freq = row['RX Freq']
        channel_tx_freq = row['TX Freq']

        # get "contact" value (mapped if needed)
        tg_name = row['Talk Group']
        if tg_name in tg_by_name_dict.keys():
            # lookup TG number and remap name to value in tg_by_num_dict
            tg_name = tg_by_num_dict[tg_by_name_dict[tg_name]][0]
        else:
            # Bad day...
            print("ERROR: Undefined talk group: '{}'".format(tg_name))
        channel_contact = tg_name
        
        channel_color_code = row['Color Code']
        channel_slot = row['TimeSlot']
        channel_call_type = row['Call Type']
        channel_contact_tg_num = str(tg_by_name_dict[tg_name])
        channel_ptt_permit = row['TX Permit']

       
        # create a channel for this talk group
        channel = []

        # channel rx/tx frequencies and channel type
        channel.append(channel_rx_freq)
        channel.append(channel_tx_freq)
        channel.append('D-Digital')

        # channel tx power
        channel.append(channel_tx_power)

        # fixed items:  Band Width, CTCSS encode/decode
        channel.append('12.5K')
        channel.append('Off')
        channel.append('Off')

        # channel contact
        channel.append(channel_contact)

        # fixed items: Contact Call Type, Contact TG/DMR ID, Radio ID, Busy Lock/Tx Permit
        channel.append(channel_call_type)
        channel.append(channel_contact_tg_num)
        channel.append('My_DMR_ID')
        channel.append('Same Color Code')

        # fixed items: Squelch Mode, Optional Signal, DTMF ID, 2Tone ID, 5Tone ID,PTT ID
        channel.append('Carrier')
        channel.append('Off')
        channel.append('1')
        channel.append('1')
        channel.append('1')
        channel.append('Off')

        # channel Color Code and Slot
        channel.append(channel_color_code)
        channel.append(channel_slot)

        # fixed items: Scan List, Receive Group List, PTT Prohibit, Reverse
        channel.append(zone_name)
        channel.append("None")
        channel.append(channel_ptt_permit)
        channel.append('Off')

        # fixed items: Simplex TDMA, TDMA Adaptive, AES Digital Encryption, Digital Encryption
        channel.append('Off')
        channel.append('Off')
        channel.append('Normal Encryption')
        channel.append('Off')

        # fixed items: Call Confirmation,Talk Around, Work Alone, Custom CTCSS 
        channel.append('Off')
        channel.append('Off')
        channel.append('Off')
        channel.append('251.1')

        # fixed items: 2TONE Decode, Ranging, Through Mode, Digi APRS RX,
        channel.append('1')
        channel.append('Off')
        channel.append('Off')
        channel.append('Off')

        # fixed items: Analog APRS PTT Mode, Digital APRS PTT Mode, APRS Report Type
        channel.append('Off')
        channel.append('Off')
        channel.append('Off')

        # fixed items: Digital APRS Report Channel, Correct Frequency[Hz]
        channel.append('1')
        channel.append('0')

        # fixed items: SMS Confirmation, Exclude channel from roaming 
        channel.append('Off')
        channel.append('0')
        
        # calculate DMR MODE
        if channel_rx_freq == channel_tx_freq:
            # assume simplex mode
            dmr_mode = 0
        else:
            # assume repeater mode (we ignore dual slot simplex possibility)
            dmr_mode = 1
        channel.append(dmr_mode)
        
        # fixed items: DataACK Disable, R5toneBot, R5ToneEot
        channel.append('0')
        channel.append('0')
        channel.append('0')

        # now add this channel to the channel dictionary
        #print("Adding channel_name = ", channel_name)
        if channel_name in channels_dict.keys():
            #print("Adding channel_name = ", channel_name)
            print("WARNING:  channel '{}' already exists. Keeping first definition".format(channel_name))
            #print("   old value of channel = ", channels_dict[channel_name])
            #channels_dict[channel_name] = channel
            #print("   new value of channel = ", channels_dict[channel_name])
        else:
            #print("Adding channel: ", channel_name)
            channels_dict.update({channel_name:channel})

        # add this channel to the specified zone
        add_channel_to_zone(zone_name, channel_name, zones_dict, channels_dict, debug=False)
     
        # add this channel to the scanlist for specified zone
        add_channel_to_zone_scanlist(zone_name, channel_name, zones_dict, channels_dict, 
                                    scan_lists_dict, debug=False)
        
    # clean-up
    del k7abd_df
    
    return



def add_channels_fm_k7abd_digital_repeaters_file(k7abd_digital_file_name, channels_dict, zones_dict, 
                                                 tg_by_num_dict, tg_by_name_dict, debug=False):

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
        channel_prefix = zone_name_list[1]
        if debug:
            print("   Working on Zone: ", zone_name)

        # get "Transmit Power" value
        channel_tx_power = row['Power']

        # get "Receive Frequency" & "Transmit Frequency"
        channel_rx_freq = row['RX Freq']
        channel_tx_freq = row['TX Freq']

        # get "Color Code" value
        channel_color_code = row['Color Code']

        # Now loop through rest of columns in k7abd digital file and create
        # a channel for each talk group represented that has a slot specified..
        talk_groups = k7abd_df.columns
        for item in talk_groups:

            # Set talk group name to 1st part of column heading if ';' present in the K7ABD file
            item_list = item.split(';')
            tg_name = item_list[0]

            if item in ['Zone Name','Comment','Power','RX Freq','TX Freq','Color Code']:
                # ignore these columns - already have these processed
                pass
            else:
                channel_slot = row[item]
                if (channel_slot == '1') or (channel_slot == '2'):
                    # create a channel for this talk group
                    #print("   working on talk group",tg_name,"  slot =", channel_slot)
                    channel = []

                    # fix tg_name value - map if needed
                    if tg_name in tg_by_name_dict.keys():
                        # lookup TG number and remap name to value in tg_by_num_dict
                        tg_name = tg_by_num_dict[tg_by_name_dict[tg_name]][0]
                    else:
                        # Bad day...
                        print("ERROR: Undefined talk group: '{}'".format(tg_name))

                    # channel name
                    channel_name = channel_prefix + ' ' + tg_name
                    if len(channel_name) >16:
                        print("Warning: '{}' > 16 chars, truncating to '{}'.".format(channel_name,
                                                                                    channel_name[:16]))
                        channel_name = channel_name[:16]

                    # channel rx/tx frequencies and channel type
                    channel.append(channel_rx_freq)
                    channel.append(channel_tx_freq)
                    channel.append('D-Digital')

                    # channel tx power
                    channel.append(channel_tx_power)

                    # fixed items:  Band Width, CTCSS encode/decode
                    channel.append('12.5K')
                    channel.append('Off')
                    channel.append('Off')

                    # channel contact
                    channel.append(tg_name)

                    # fixed items: Contact Call Type, Contact TG/DMR ID, Radio ID, Busy Lock/Tx Permit
                    channel.append('Group Call')
                    channel.append(str(tg_by_name_dict[tg_name]))
                    channel.append('My_DMR_ID')
                    channel.append('Same Color Code')

                    # fixed items: Squelch Mode, Optional Signal, DTMF ID, 2Tone ID, 5Tone ID,PTT ID
                    channel.append('Carrier')
                    channel.append('Off')
                    channel.append('1')
                    channel.append('1')
                    channel.append('1')
                    channel.append('Off')

                    # channel Color Code and Slot
                    channel.append(channel_color_code)
                    channel.append(channel_slot)

                    # fixed items: Scan List, Receive Group List, PTT Prohibit, Reverse
                    channel.append("None")
                    channel.append("None")
                    channel.append('Off')
                    channel.append('Off')

                    # fixed items: Simplex TDMA, TDMA Adaptive, AES Digital Encryption, Digital Encryption
                    channel.append('Off')
                    channel.append('Off')
                    channel.append('Normal Encryption')
                    channel.append('Off')

                    # fixed items: Call Confirmation,Talk Around, Work Alone, Custom CTCSS 
                    channel.append('Off')
                    channel.append('Off')
                    channel.append('Off')
                    channel.append('251.1')

                    # fixed items: 2TONE Decode, Ranging, Through Mode, Digi APRS RX,
                    channel.append('1')
                    channel.append('Off')
                    channel.append('Off')
                    channel.append('Off')

                    # fixed items: Analog APRS PTT Mode, Digital APRS PTT Mode, APRS Report Type
                    channel.append('Off')
                    channel.append('Off')
                    channel.append('Off')

                    # fixed items: Digital APRS Report Channel, Correct Frequency[Hz]
                    channel.append('1')
                    channel.append('0')

                    # fixed items: SMS Confirmation, Exclude channel from roaming 
                    channel.append('Off')
                    channel.append('0')
                    
                     # fixed items: DMR MODE, DataACK Disable, R5toneBot, R5ToneEot
                    channel.append('1')
                    channel.append('0')
                    channel.append('0')
                    channel.append('0')

                    # now add this channel to the channel dictionary
                    if debug:
                            print("   Adding channel {}".format(channel_name))
                    if channel_name in channels_dict.keys():
                        print("WARNING:  channel already exists: ", channel_name)
                        if debug:
                            print("      Existing channel = ", channels_dict[channel_name])
                            print("      Ignored new value = ", channel)
                    else:
                        channels_dict.update({channel_name:channel})

                    # add this channel to the specified zone
                    add_channel_to_zone(zone_name, channel_name, zones_dict, channels_dict, debug=False)
                    
                    # add this channel to the scanlist for specified zone
                    add_channel_to_zone_scanlist(zone_name, channel_name, zones_dict, channels_dict, 
                                                scan_lists_dict, debug=False)
                    
                else:
                    # this talk group not on this repeater, so no channel for it...
                    #print("Skipping... slot =", row[item])
                    pass

    # clean-up
    del k7abd_df

    return
    
    

    

    

##################################################################################################
#
# Main program...
#  
##################################################################################################

# Global dictionary/list structures
tg_by_num_dict = {}
tg_by_name_dict = {}
tg_name_to_id_dict = {}
zones_dict = {}
channels_dict = {}
rx_groups_dict = {}
scan_lists_dict = {}
zones_order_list = []

def main():

   # Greet the customer
   print("")
   print("Anytone CPS Import File Builder")
   print("Source: https://github.com/n7ekb/cps-import-builder")
   print("")

   # get today's date to stamp output files with today's iso-date.
   isodate = time.strftime("%Y-%m-%d")
   
   # Setup our command line handler
   debugmode = False
   script_name = sys.argv[0]
   parser = argparse.ArgumentParser()
   parser.add_argument('--inputdir', help='Directory containing input files',
                       required=False, default='./input_data_files')
   parser.add_argument('--outputdir', help='Target directory for output files',
                       required=False, default='./output_files')
   parser.add_argument('--debugmode', help='Set debug flag for troubleshooting',
                       required=False, action='store_true') 
     
   # parse the command line
   args = parser.parse_args()
   debugflg = args.debugmode

   # set working directories from command line values
   inputs_dir = args.inputdir
   print("Looking in '{}' for input files.".format(inputs_dir))
   outputs_dir = args.outputdir   
   print("Putting output files in: '{}'.".format(outputs_dir))
   
   # define our export files 
   zones_output_filename = 'zones_{}.csv'.format(isodate) 
   zones_output_file = os.path.join(outputs_dir, zones_output_filename)
   rx_groups_output_filename = 'receive_groups_{}.csv'.format(isodate) 
   rx_groups_output_file = os.path.join(outputs_dir, rx_groups_output_filename)
   scan_lists_output_filename = 'scan_lists_{}.csv'.format(isodate)  
   scan_lists_output_file = os.path.join(outputs_dir, scan_lists_output_filename)
   talk_groups_output_filename = 'talk_groups_{}.csv'.format(isodate)
   talk_groups_output_file = os.path.join(outputs_dir, talk_groups_output_filename)
   channels_output_filename = 'channels_{}.csv'.format(isodate)
   channels_output_file = os.path.join(outputs_dir, channels_output_filename) 
   file_list_output_filename = 'file_list_{}.LST'.format(isodate)
   file_list_output_file = os.path.join(outputs_dir, file_list_output_filename)
   


   # Read in Zone Order file
   zone_order_filespec = os.path.join(inputs_dir, "Zone_Order.csv")
   zones_order_list = read_zone_order_file(zone_order_filespec, debug=debugflg)
   
   
   
   # Add channels from K7ABD Analog__ files
   analog_channels_filespec = os.path.join(inputs_dir, 'Analog__*')
   file_list = []
   for match in glob.iglob(analog_channels_filespec, recursive=False):
       file_list.append(match)
   for analog_channels_filename in sorted(file_list):
       print("Adding analog channels from K7ABD file: ", analog_channels_filename)
       add_channels_fm_k7abd_analog_file(analog_channels_filename, channels_dict, 
                                         zones_dict, debug=debugflg)
       
       
       
   # Add talk groups from K7ABD Talkgroups__ files
   talkgroups_filespec = os.path.join(inputs_dir, 'Talkgroups__*')
   file_list = []
   for match in glob.iglob(talkgroups_filespec, recursive=False):
       file_list.append(match)
   for talkgroups_filename in sorted(file_list):
       print("Adding talkgroups from K7ABD file: ", talkgroups_filename)
       add_talkgroups_fm_k7abd_talkgroups_file(talkgroups_filename, tg_by_num_dict, 
                                               tg_by_name_dict, debug=debugflg)
   
       
       
   # Add channels from K7ABD Digital-Others__ files
   digital_others_filespec = os.path.join(inputs_dir, 'Digital-Others__*')
   file_list = []
   for match in glob.iglob(digital_others_filespec, recursive=False):
       file_list.append(match)
   for digital_others_filename in sorted(file_list):
       print("Adding digital-other channels from K7ABD file: ", digital_others_filename)
       add_channels_fm_k7abd_digital_others_file(digital_others_filename, channels_dict, 
                                                 zones_dict, tg_by_num_dict, tg_by_name_dict, 
                                                 debug=debugflg)
   
   
       
   # Add channels from K7ABD Digital-Repeaters files
   digital_repeaters_filespec = os.path.join(inputs_dir, 'Digital-Repeaters__*')
   file_list = []
   for match in glob.iglob(digital_repeaters_filespec, recursive=False):
       file_list.append(match)
   for digital_repeaters_filename in sorted(file_list):
       print("Adding digital-repeater channels from k7abd file: ", digital_repeaters_filename)
       add_channels_fm_k7abd_digital_repeaters_file(digital_repeaters_filename, 
               channels_dict, zones_dict, tg_by_num_dict, tg_by_name_dict, debug=debugflg)
   
   
   
   # write our in-memory representation to Anytone 878 export files for import back into CPS...
   anytone_write_zones_export(zones_dict, zones_order_list, zones_output_file, 
                              channels_dict, debug=False)
   #anytone_write_rx_groups_export(rx_groups_dict, rx_groups_output_file, debug=False)
   #anytone_write_scan_lists_export(scan_lists_dict, scan_lists_output_file, debug=False)
   anytone_write_talk_groups_export(tg_by_num_dict, talk_groups_output_file, debug=False)
   anytone_write_channels_export(channels_dict, channels_output_file, debug=debugflg)
   
   
   # Write a list of the files to import from...
   with open(file_list_output_file,'w') as output_file:
       output_file.write('20\r\n')
       linenum = 0
       for line in [channels_output_filename, '',zones_output_filename,
                   scan_lists_output_filename, '', talk_groups_output_filename, '', '',
                    '','', '', '','','','','','','','','',''
                   ]:
           output_file.write('{},\"{}\"\r\n'.format(linenum, line))
           linenum += 1
       
   output_file.close()  
   
   print("")
   print("All done!")
   print("")
   


# if this file isn't being imported as a module then call ourselves as the main thing...
if __name__ == "__main__":
   main()
