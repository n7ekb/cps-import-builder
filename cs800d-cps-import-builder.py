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
 


# global lists of all CTCSS values
ctcss_list = ['67','69.4','71.9','74.4','77','79.7','82.5','85.4','88.5','91.5',
              '94.8','97.4','100','103.5','107.2','110.9','114.8','118.8','123',
              '127.3','131.8','136.5','141.3','146.2','150']

cdcss_list = ['D023N','D025N','D026N','D031N','D032N','D043N','D047N','D051N','D054N',
              'D065N','D071N','D072N','D073N','D074N','D114N','D115N','D116N','D125N',
              'D131N','D132N','D134N','D143N','D152N','D155N','D156N','D162N','D165N',
              'D172N','D174N','D205N','D223N','D226N','D243N','D244N','D245N','D251N',
              'D261N','D263N','D265N','D271N','D306N','D311N','D315N','D331N','D343N',
              'D346N','D351N','D364N','D365N','D371N','D411N','D412N','D413N','D423N',
              'D431N','D432N','D445N','D464N','D465N','D466N','D503N','D506N','D516N',
              'D532N','D546N','D565N','D606N','D612N','D624N','D627N','D631N','D632N',
              'D654N','D662N','D664N','D703N','D712N','D723N','D731N','D732N','D734N',
              'D743N','D754N']



def cs800d_write_channels_export(channels_dict, channels_export_file, debug=False):
    """This function writes out a CS800D CPS formatted channels file"""

    analog_header_row = ['No','Channel Alias','Squelch Level', 'Channel Band[KHz]',
                         'Personality List','Scan List','Auto Scan Start','Rx Only',
                         'Talk Around', 'Lone Worker', 'VOX', 'Scrambler', 'Emp De-emp',
                         'Receive Frequency', 'RX CTCSS/CDCSS Type', 'CTCSS/CDCSS', 
                         'RX Ref Frequency', 'Rx Group List', 'Rx Squelch Mode', 
                         'Monitor Squelch Mode',
                         'Channel Switch Squelch Mode',
                         'Transmit Frequency', 'TX CTCSS/CDCSS Type', 'CTCSS/CDCSS',
                         'TX Ref Frequency', 'Power Level', 'Tx Admit', 
                         'Reverse Burst/Turn off code',
                         'TX Time-out Time[s]', 'TOT Re-key Time[s]', 'TOT Pre-Alert Time[s]',
                         'CTCSS Tail Revert Option']
    digital_header_row = ['No','Channel Alias','Digital Id', 'Color Code',
                         'Time Slot','Scan List','Auto Scan Start','Rx Only',
                         'Talk Around', 'Lone Worker', 'VOX',
                         'Receive Frequency',
                         'RX Ref Frequency', 'RX Group List', 'Emergency Alarm Indication',
                         'Emergency Alarm Ack', 'Emergency Call Indication', 
                         'Transmit Frequency', 'TX Ref Frequency', 'TX Contact', 
                         'Emergency System',
                         'Power Level', 'Tx Admit',
                         'TX Time-out Time[s]', 'TOT Re-key Time[s]', 'TOT Pre-Alert Time[s]',
                         'Private Call Confirmed', 'Data Call Confirmed', 'Encrypt']
    
    # setup analog channels dataframe
    analog_channels_out_list = []
    cnt = 1
    for channel_alias in channels_dict.keys():
        channel_data = channels_dict[channel_alias]
        channel_type = channel_data[2]
        
        # skip non-analog channels
        if channel_type != 'A-Analog':
            continue
        # now fill out this row in correct order for cs800d
        row_list = []
        row_list.append(str(cnt))
        cnt = cnt + 1
        row_list.append(channel_alias)
        row_list.append("Normal")         # Squelch level
        row_list.append(channel_data[4])  # Channel Bandwidth
        row_list.append("Personality 1")  # Personality
        row_list.append(channel_data[19]) # scan list
        row_list.append("Off")            # auto scan start
        row_list.append(channel_data[21]) # Rx Only
        row_list.append(channel_data[28]) # Talk around
        row_list.append(channel_data[29]) # Lone Worker
        row_list.append("Off")            # VOX
        row_list.append("Off")            # Scrambler
        row_list.append("Off")            # Emp De-emp
        row_list.append(channel_data[0])  # Receive Frequency
        
        # RX CTCSS/CDCSS Type
        ctcss_dcs_decode_val = channel_data[5]
        if ctcss_dcs_decode_val == "Off":
            row_list.append("NONE")
            row_list.append("NONE")
            rx_squelch_mode = "CTCSS/DCS and Audio"
        elif ctcss_dcs_decode_val in ctcss_list:
            row_list.append("CTCSS")
            row_list.append(ctcss_dcs_decode_val)
            rx_squelch_mode = "CTCSS/DCS and Audio"
        elif ctcss_dcs_decode_val in cdcss_list:
            row_list.append("CDCSS")
            row_list.append(ctcss_dcs_decode_val[1:4])
            rx_squelch_mode = "CTCSS/DCS and Audio"
            
        if float(channel_data[0]) > 180.0:
            row_list.append("Low")        # RX Ref Frequency (VHF/2 meters)
        else:
            row_list.append("Low")        # RX Ref Frequency (UHF/70cm )
        row_list.append(rx_squelch_mode)  # Rx squelch mode
        row_list.append("Carrier")        # Monitor squelch mode
        row_list.append("RX Squelch Mode")  # Channel switch squelch mode
        
        row_list.append(channel_data[1])  # Transmit Frequency
        
        # TX CTCSS/CDCSS Type
        ctcss_dcs_encode_val = channel_data[6]
        if ctcss_dcs_encode_val == "Off":
            row_list.append("NONE")
            row_list.append("NONE")
        elif ctcss_dcs_encode_val in ctcss_list:
            row_list.append("CTCSS")
            row_list.append(ctcss_dcs_encode_val)
        elif ctcss_dcs_encode_val in cdcss_list:
            row_list.append("CDCSS")
            row_list.append(ctcss_dcs_encode_val[1:4])
            
        row_list.append(channel_data[1])  # Transmit Frequency
        if float(channel_data[1]) > 180.0:
            row_list.append("Middle")     # TX Ref Frequency (VHF/2 meters)
        else:
            row_list.append("Low")        # TX Ref Frequency (UHF/70cm )
            
        # Power level
        power_level = channel_data[3]
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
    for channel_alias in channels_dict.keys():
        channel_data = channels_dict[channel_alias]
        channel_type = channel_data[2]
        
        # skip non-analog channels
        if channel_type != 'D-Digital':
            continue
        # now fill out this row in correct order for cs800d
        row_list = []
        row_list.append(str(cnt))
        cnt = cnt + 1
        row_list.append(channel_alias)
        row_list.append("0")              # Digital ID
        row_list.append(channel_data[17]) # Color Code
        row_list.append(channel_data[18]) # Time Slot
        row_list.append(channel_data[19]) # Scan List
        row_list.append("Off")            # Auto Scan Start
        row_list.append(channel_data[21]) # Rx Only
        row_list.append(channel_data[28]) # Talk around
        row_list.append(channel_data[29]) # Lone Worker
        row_list.append("Off")            # VOX
        row_list.append(channel_data[0])  # Receive Frequency
        if float(channel_data[0]) > 180.0:
            row_list.append("Middle")     # RX Ref Frequency (VHF/2 meters)
        else:
            row_list.append("Middle")     # RX Ref Frequency (UHF/70cm )
        row_list.append(channel_data[20]) # RX Receive Group
        row_list.append("Off")            # Emergency Alarm Indication
        row_list.append("Off")            # Emergency Alarm Ack
        row_list.append("Off")            # Emergency Call Indication
        row_list.append(channel_data[1])  # Transmit Frequency
        if float(channel_data[1]) > 180.0:
            row_list.append("Middle")     # TX Ref Frequency (VHF/2 meters)
        else:
            row_list.append("Middle")     # TX Ref Frequency (UHF/70cm )
        row_list.append(channel_data[7])  # TX Contact
        row_list.append("None")           # Emergency System
        
        # Power level
        power_level = channel_data[3]
        if power_level in ['Turbo','High']:
            row_list.append("High")
        else:
            row_list.append("Low")
        
        # TX Admit (admit criteria)
        admit_criteria = channel_data[20]
        if admit_criteria == "Always":
            row_list.append("Always")
        elif admit_criteria in ['ChannelFree','Different Color Code']:
            row_list.append("Channel Idle")
        elif admit_criteria == "Same Color Code":
            row_list.append("Color Code Free")
        row_list.append(channel_data[20]) # TX Admit

        row_list.append("180")            # TX Time-out Time[s]
        row_list.append("0")              # TOT Re-key Time[s]
        row_list.append("10")             # TOT Pre-Alert Time[s]
        row_list.append("Off")            # Private Call Confirmed
        row_list.append("Off")            # Data Call Confirmed
        row_list.append("Off")            # Encrypt
        
        # now add the row for this channel to our digital channels list
        digital_channels_out_list.append(row_list)
        
    # create the analog channels data frame   
    digital_channels_out_df = pandas.DataFrame(digital_channels_out_list, 
                                               columns=digital_header_row)
    

    if debug:
        print("Writing output to: ", channels_export_file)
        
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pandas.ExcelWriter(channels_export_file, engine='xlsxwriter')
    analog_channels_out_df.to_excel(writer, sheet_name="Analog Channel", index=False)
    digital_channels_out_df.to_excel(writer, sheet_name="Digital Channel", index=False)
    
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
                           revert_ch, loop_back_time_a, loop_back_time_b, drop_out_delay, 
                           dwell_time]
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
                           revert_ch, loop_back_time_a, loop_back_time_b, drop_out_delay, 
                           dwell_time]})
        
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
                                        ch_contact, ch_contact_call_type, ch_contact_tg_num, 
                                        ch_radio_id, ch_tx_permit, ch_squelch_mode, 
                                        ch_optional_sig, ch_dtmf_id, ch_2tone_id,
                                        ch_5tone_id, ch_ptt_id, ch_color_code, ch_slot, 
                                        ch_scan_list,
                                        ch_rx_group, ch_ptt_prohibit, ch_reverse, 
                                        ch_simplex_tdma,
                                        ch_tdma_adaptive, ch_aes_encrypt, ch_digital_encrypt, 
                                        ch_call_confirm, ch_talk_around, ch_work_alone, 
                                        ch_custom_ctcss,
                                        ch_2tone_decode, ch_ranging, ch_through_mode, 
                                        ch_digi_aprs_rx,
                                        ch_analog_aprs_ptt, ch_digital_aprs_ptt, 
                                        ch_aprs_rpt_type,
                                        ch_digi_aprs_rpt_ch, ch_correct_freq, ch_sms_confirm,
                                        ch_exclude_fm_roaming,
                                        ch_dmr_mode,ch_dataack_disable,ch_r5tone_bot,
                                        ch_r5tone_eot]})

        # add this channel to the specified zone
        add_channel_to_zone(zone_name, ch_name, zones_dict, channels_dict, debug=False)
        
        # add this channel to the scanlist for specified zone
        add_channel_to_zone_scanlist(zone_name, ch_name, zones_dict, channels_dict, 
                                    scan_lists_dict, debug=False)
        

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

   # get today's date to stamp output files with today's iso-date.
   isodate = time.strftime("%Y-%m-%d")

  # Greet the customer
   print("")
   print("Import File Builder for Connect Systems CS800D CPS")
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
   talk_groups_output_filename = 'talk_groups_{}.xlsx'.format(isodate)
   talk_groups_output_file = os.path.join(outputs_dir, 
                                          talk_groups_output_filename)
   channels_output_filename = 'channels_{}.xlsx'.format(isodate)
   channels_output_file = os.path.join(outputs_dir, channels_output_filename) 



   # Read in Zone Order file
   zone_order_filespec = os.path.join(inputs_dir, "Zone_Order.csv")
   zones_order_list = read_zone_order_file(zone_order_filespec, debug=debugflg)



   # Add channels from K7ABD Analog__ files
   analog_channels_filespec = os.path.join(inputs_dir, 'Analog__*')
   file_list = []
   for match in glob.iglob(analog_channels_filespec, recursive=False):
       file_list.append(match)
   for analog_channels_filename in sorted(file_list):
       print("Adding analog channels from K7ABD file: ", 
               analog_channels_filename)
       add_channels_fm_k7abd_analog_file(analog_channels_filename, 
               channels_dict, zones_dict, debug=debugflg)
    
    
    
   # Add talk groups from K7ABD Talkgroups__ files
   talkgroups_filespec = os.path.join(inputs_dir, 'Talkgroups__*')
   file_list = []
   for match in glob.iglob(talkgroups_filespec, recursive=False):
       file_list.append(match)
   for talkgroups_filename in sorted(file_list):
       print("Adding talkgroups from K7ABD file: ", talkgroups_filename)
       add_talkgroups_fm_k7abd_talkgroups_file(talkgroups_filename, tg_by_num_dict, tg_by_name_dict, debug=debugflg)

    
    
   # Add channels from K7ABD Digital-Others__ files
   digital_others_filespec = os.path.join(inputs_dir, 'Digital-Others__*')
   file_list = []
   for match in glob.iglob(digital_others_filespec, recursive=False):
       file_list.append(match)
   for digital_others_filename in sorted(file_list):
       print("Adding digital-other channels from K7ABD file: ", digital_others_filename)
       add_channels_fm_k7abd_digital_others_file(digital_others_filename, 
               channels_dict, zones_dict, tg_by_num_dict, tg_by_name_dict, 
               debug=debugflg)


    
   # Add channels from K7ABD Digital-Repeaters files
   digital_repeaters_filespec = os.path.join(inputs_dir, 'Digital-Repeaters__*')
   file_list = []
   for match in glob.iglob(digital_repeaters_filespec, recursive=False):
       file_list.append(match)
   for digital_repeaters_filename in sorted(file_list):
       print("Adding digital-repeater channels from k7abd file: ", digital_repeaters_filename)
       add_channels_fm_k7abd_digital_repeaters_file(digital_repeaters_filename, 
               channels_dict, zones_dict, tg_by_num_dict, tg_by_name_dict, 
               debug=debugflg)



   # write our in-memory representation to Anytone 878 export files for import back into CPS...
   cs800d_write_talk_groups_export(tg_by_num_dict, talk_groups_output_file, debug=False)
   cs800d_write_channels_export(channels_dict, channels_output_file, debug=False)


   print("")
   print("All done!")
   print("")



# if this file isn't being imported as a module then call ourselves as the main thing...
if __name__ == "__main__":
   main()



