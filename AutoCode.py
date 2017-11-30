# Packages for GUI
from Tkinter import *
import Tkinter
from tkFileDialog import askopenfilename, asksaveasfilename
import tkMessageBox
import ttk
import sys

# Packages for working with SPEL output CSV
import csv

# Packages for working with XML/XEF
import xml.etree.ElementTree as ET
import os
import shutil
import configparser

# Packages for working with unallocated tags
import numpy as np

class MainApplication(Tkinter.Frame):
    def __init__(self, parent, *args, **kwargs):

        Tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.title("AutoCode")

        self.SPEL_output_csv_filename = None
        self.standard_template_xef_filename = None
        self.plc_skeleton_xef_filename = None
        
        # Define section name in the file exported from Unity
        self.program_section_name = 'program'
        self.identProgram_section_name = 'identProgram'
        self.dataBlock_section_name = 'dataBlock'
        self.DDTSource_section_name = 'DDTSource'
        
        self.FBIfinalmatchingList = []
        
        # Configuration Page
        self.configuration_page_canvas = Canvas(self, width=600, height=680)
        self.configuration_page = Frame(self.configuration_page_canvas, padx = 50, pady = 10)
        self.vsb = Scrollbar(self, orient="vertical", command=self.configuration_page_canvas.yview)
        self.configuration_page_canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.configuration_page_canvas.pack(fill="both", expand=True)
        self.configuration_page_canvas.create_window((4,4), window=self.configuration_page)

        self.configuration_page.bind("<Configure>", self.onFrameConfigure)
        self.configuration_page_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        configuration_title_label = Label(self.configuration_page, text = "Configuration Settings")

        file_selection_label = Label(self.configuration_page, text = "\nSelect the SPEL output and standard template files to use.")
        
        self.SPEL_csv_file_label = Label(self.configuration_page, text = "No file selected")
        select_SPEL_csv_file_button = Button(self.configuration_page, text = "Select SPEL Output CSV file (Required)", command = self.select_SPEL_output_csv_file)

        self.standard_template_xef_file_label = Label(self.configuration_page, text = "No file selected")
        select_standard_template_xef_file_button = Button(self.configuration_page, text = "Select Standard Template XEF file (Required)", command = self.select_standard_template_xef_file)
        
        self.plc_skeleton_xef_file_label = Label(self.configuration_page, text = "No file selected")
        select_plc_skeleton_xef_file_button = Button(self.configuration_page, text = "Select PLC Skeleton XEF file (Required)", command = self.select_plc_skeleton_xef_file)

        SPEL_output_settings_label = Label(self.configuration_page, text = "\n\nSPEL Output CSV Settings")

        SPEL_output_area_code_label = Label(self.configuration_page, text = "Enter the Area Code used in your SPEL output CSV file. Leave blank if no area code.")
        self.SPEL_output_area_code_entry = Entry(self.configuration_page)
        self.SPEL_output_area_code_entry.insert(0, "TLO")

        SPEL_output_delimiter_structure_label = Label(self.configuration_page, text = "Enter the Delimiter structure used in your SPEL output CSV file (Required)")
        self.SPEL_output_delimiter_structure_entry = Entry(self.configuration_page)
        self.SPEL_output_delimiter_structure_entry.insert(0, "_")

        standard_template_convention_structure_label = Label(self.configuration_page, text = "\n\nStandard Template Naming Convention Settings \n\n Example of naming convention \n XXX_YYYY \n XXX -> Area Code \n YYYY -> Drive Code \n _ -> Delimiter \n\n Example Tag: XXX_YYYY_RUN_I")
        
        area_code_structure_label = Label(self.configuration_page, text = "Enter the Area Code structure used in your standard template. Leave blank if no area code.")
        self.area_code_structure_entry = Entry(self.configuration_page)
        self.area_code_structure_entry.insert(0, "XXX")

        drive_code_structure_label = Label(self.configuration_page, text = "Enter the Drive Code structure used in your standard template (Required).")
        self.drive_code_structure_entry = Entry(self.configuration_page)
        self.drive_code_structure_entry.insert(0, "YYYY")

        standard_template_delimiter_structure_label = Label(self.configuration_page, text = "Enter the Delimiter structure used in your standard template (Required).")
        self.standard_template_delimiter_structure_entry = Entry(self.configuration_page)
        self.standard_template_delimiter_structure_entry.insert(0, "_")

        configure_standard_template_convention = Button(self.configuration_page, text = "Update naming convention", command = self.update_naming_convention)

        self.configured_standard_template_convention_label = Label(self.configuration_page, text = "Current configured naming convention: \n" + self.area_code_structure_entry.get() + self.standard_template_delimiter_structure_entry.get() + self.drive_code_structure_entry.get() + self.standard_template_delimiter_structure_entry.get())

        submit_configuration_button = Button(self.configuration_page, text = "Confirm Configuration Settings and Generate Configuration File", command = self.confirm_configuration_settings)
        
        # Configuration Page Widget Positioning
        configuration_title_label.grid(row = 0, column = 0, columnspan = 2)

        file_selection_label.grid(row = 1, column = 0, columnspan = 2)

        self.SPEL_csv_file_label.grid(row = 2, column = 0, columnspan = 2)
        select_SPEL_csv_file_button.grid(row = 3, column = 0, columnspan = 2)

        self.standard_template_xef_file_label.grid(row = 4, column = 0, columnspan = 2)
        select_standard_template_xef_file_button.grid(row = 5, column = 0, columnspan = 2)

        self.plc_skeleton_xef_file_label.grid(row = 6, column = 0, columnspan = 2)
        select_plc_skeleton_xef_file_button.grid(row = 7, column = 0, columnspan = 2)

        SPEL_output_settings_label.grid(row = 8, column = 0, columnspan = 2)

        SPEL_output_area_code_label.grid(row = 9, column = 0, columnspan = 2, pady = 8)
        self.SPEL_output_area_code_entry.grid(row = 10, column = 0, columnspan = 2)

        SPEL_output_delimiter_structure_label.grid(row = 11, column = 0, columnspan = 2, pady = 8)
        self.SPEL_output_delimiter_structure_entry.grid(row = 12, column = 0, columnspan = 2)

        standard_template_convention_structure_label.grid(row = 13, column = 0, columnspan = 2)

        area_code_structure_label.grid(row = 14, column = 0, columnspan = 2, pady = 8)
        self.area_code_structure_entry.grid(row = 15, column = 0, columnspan = 2)

        drive_code_structure_label.grid(row = 16, column = 0, columnspan = 2, pady = 8)
        self.drive_code_structure_entry.grid(row = 17, column = 0, columnspan = 2)

        standard_template_delimiter_structure_label.grid(row = 18, column = 0, columnspan = 2, pady = 8)
        self.standard_template_delimiter_structure_entry.grid(row = 19, column = 0, columnspan = 2)

        configure_standard_template_convention.grid(row = 20, column = 0, columnspan = 2, pady = 8)
        self.configured_standard_template_convention_label.grid(row = 21, column = 0, columnspan = 2)

        submit_configuration_button.grid(row = 22, column = 0, columnspan = 2)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.configuration_page_canvas.configure(scrollregion=self.configuration_page_canvas.bbox("all"))

    def _on_mousewheel(self, event):
        self.configuration_page_canvas.yview_scroll(-1*(event.delta/120), "units")

    def select_SPEL_output_csv_file(self):
        self.SPEL_output_csv_filename = askopenfilename()
        if self.SPEL_output_csv_filename.split(".")[-1] != "csv":
            self.create_error_message("Invalid File Type!", "Please ensure the SPEL output file is a .csv file.")
            return
        # Check 
        if os.stat(self.SPEL_output_csv_filename).st_size == 0:
            self.create_error_message("Empty File Selected!","Selected SPEL out file is empty.")
            return
        self.SPEL_csv_file_label.config(text = self.SPEL_output_csv_filename)

    def select_standard_template_xef_file(self):
        self.standard_template_xef_filename = askopenfilename()
        if self.standard_template_xef_filename.split(".")[-1] != "xef":
            self.create_error_message("Invalid File Type!", "Please ensure the standard template file is a .xef file.")
            return
        if os.stat(self.standard_template_xef_filename).st_size == 0:
            self.create_error_message("Empty File Selected!","Selected standard template file is empty.")
            return
        self.standard_template_xef_file_label.config(text = self.standard_template_xef_filename)



    def select_plc_skeleton_xef_file(self):
        self.plc_skeleton_xef_filename = askopenfilename()
        if self.plc_skeleton_xef_filename.split(".")[-1] != "xef":
            self.create_error_message("Invalid File Type!", "Please ensure the PLC skeleton file is a .xef file.")
            return
        if os.stat(self.plc_skeleton_xef_filename).st_size == 0:
            self.create_error_message("Empty File Selected!","Selected plc skeleton file is empty.")
            return
        

        self.plc_skeleton_xef_file_label.config(text = self.plc_skeleton_xef_filename)   

    def update_naming_convention(self):
        if len(self.drive_code_structure_entry.get().replace(" ","")) <= 0:
            self.create_error_message("Required Field Empty!", "Please enter the Drive Code structure used in your standard template")
            return

        if len(self.standard_template_delimiter_structure_entry.get().replace(" ","")) <= 0:
            self.create_error_message("Required Field Empty!", "Please enter the Delimiter structure used in your standard template")
            return

        if len(self.area_code_structure_entry.get().replace(" ","")) > 0:
            configured_standard_template_convention_label_text = "Current configured naming convention: \n" + self.area_code_structure_entry.get() + self.standard_template_delimiter_structure_entry.get() + self.drive_code_structure_entry.get() + self.standard_template_delimiter_structure_entry.get()
        else:
            configured_standard_template_convention_label_text = "Current configured naming convention: \n" + self.drive_code_structure_entry.get() + self.standard_template_delimiter_structure_entry.get()
        self.configured_standard_template_convention_label.config(text = configured_standard_template_convention_label_text)

    def confirm_configuration_settings(self):
        if self.SPEL_output_csv_filename == None:
            self.create_error_message("Required File Missing!", "Please select a SPEL Output CSV file to use")
            return

        if self.standard_template_xef_filename == None:
            self.create_error_message("Required File Missing!", "Please select a Standard Template XEF file to use")
            return

        if self.plc_skeleton_xef_filename == None:
            self.create_error_message("Required File Missing!", "Please select a PLC Skeleton XEF file to use")
            return

        if self.SPEL_output_area_code_entry.get() == '' and self.standard_template_delimiter_structure_entry.get() != '.':
            self.create_error_message("Invalid Area Code!", "Please fill up the missing area code for the flat stucture standard template.")
            return

        datablock_section_found = False

        self.plc_tree = ET.parse(self.plc_skeleton_xef_filename)
        self.plc_root = self.plc_tree.getroot()
        for element in self.plc_root.iter():
            if self.dataBlock_section_name == element.tag:
                datablock_section_found = True
        
        if datablock_section_found == False:
            self.create_error_message("Invalid PLC Skeleton File", "Datablock section not found in selected PLC skeleton file!")
            return

        if len(self.area_code_structure_entry.get().replace(" ","")) > 0:
            self.naming_convention = self.area_code_structure_entry.get() + self.standard_template_delimiter_structure_entry.get() + self.drive_code_structure_entry.get() + self.standard_template_delimiter_structure_entry.get()
        else:
            self.naming_convention = self.drive_code_structure_entry.get() + self.standard_template_delimiter_structure_entry.get()

        self.area_code = self.SPEL_output_area_code_entry.get().replace(" ","")

        self.processed_spel_output, is_csv_valid, is_row_valid = self.process_SPEL_output(self.SPEL_output_csv_filename)


        if not is_csv_valid:
            return
        if (len(self.processed_spel_output) == 0):
            self.create_error_message("Invalid SPEL CSV File!","Signal ID column is empty")
            return
        
        try:
            self.drives, self.drives_dict, self.uncategorized_tags = self.extract_drives_from_SPEL_output(self.processed_spel_output)
        except:
            return
        else:
            pass

        self.create_copy_of_standard_template_xef_file_and_open_access_to_copied_file(self.standard_template_xef_filename)

        datablock_section_found = False
        for element in self.root.iter():
            if self.dataBlock_section_name == element.tag:
                datablock_section_found = True
        
        if datablock_section_found == False:
            self.create_error_message("Invalid Standard Templates File", "Datablock section not found in selected standard template!")
            return

        self.standard_template_names = self.extract_plc_standard_templates_from_copy_of_standard_template_xef_file()
        self.separate_plc_standard_templates_from_standard_template_xef_file_into_different_xbd_files()

        has_configuration_file = tkMessageBox.askyesno('Configuration File', "Do you have an existing .ini configuration file you wish to use?")

        if has_configuration_file == True:
            self.config_filename = askopenfilename()
            if self.config_filename.split(".")[-1] != "ini":
                self.create_error_message("Invalid Configuration File", "Please ensure your configuration file is a .ini file.")
                return

            configDict, stdTempTypeNameList = self.read_config_file(self.config_filename)
            matchingList = self.get_matching_list(configDict)
            k = 0
            for match in matchingList:
                if match[1] == '':
                    k += 1
            if (k != 0):
                self.create_error_message("Unfilled Configuration File!", "Please fill in all required fields in the configuration file.")
                return
            else:
                self.load_matcher_page()
        else:
            standard_template_IO_tags_dict = {}

            for standard_template_name in self.standard_template_names:
                unknownTagsList = self.extract_unknown_tags_from_a_standard_template(standard_template_name.lower()+"_template.xbd")
                if len(unknownTagsList) != 0:
                    standard_template_IO_tags_dict[standard_template_name] = unknownTagsList

            if (len(standard_template_IO_tags_dict) == 0):
                self.create_error_message("Invalid Standard Template Naming Convention", "The specified naming convention does not match the convention used in the standard template file supplied.")
                return
            else:
                tkMessageBox.showinfo("Generating New Configuration File", "A new configuration file will be generated for you, please select where you would like it generated. Note that it must be a .ini file.")
                self.write_config_file(standard_template_IO_tags_dict)
            
            tkMessageBox.showinfo("Configuration File Generated", "A configuration file called " + self.config_filename.split("/")[-1] +" has been generated. Please fill it in and try again.")
            
            return

    def load_matcher_page(self):
        # Drive to Standard Template Matcher Page
        self.matcher_page = Frame(self, padx = 50, pady = 30)
        matcher_title_label = Label(self.matcher_page, text = "Drive to Standard Template Matcher")

        self.drive_dropdown_options = self.drives[:]
        self.drive_selected = StringVar(self.matcher_page)
        self.drive_selected.set(self.drive_dropdown_options[0])
        self.drive_dropdown = Tkinter.OptionMenu(self.matcher_page, self.drive_selected, *self.drive_dropdown_options)

        self.standard_template_dropdown_options = self.standard_template_names[:]
        self.standard_template_selected = StringVar(self.matcher_page)
        self.standard_template_selected.set(self.standard_template_dropdown_options[0])
        self.standard_template_dropdown = Tkinter.OptionMenu(self.matcher_page, self.standard_template_selected, *self.standard_template_dropdown_options)

        self.matched_drive_standard_template_pairs = []
        self.match_button = Button(self.matcher_page, text = "Match", command = self.match_drive_to_standard_template)
        self.matched_list = Label(self.matcher_page, text = "No matches yet")
        self.reset_matches_button = Button(self.matcher_page, text = "Reset Matches", command = self.reset_matches)
        self.confirm_matches_button = Button(self.matcher_page, text = "Confirm Matches", command = self.confirm_matches)
        self.progress_label = Label(self.matcher_page, text = "Click 'Confirm Matches' to begin generating PLC code.")
        self.exit_program_button = Button(self.matcher_page, text = "Exit", command = self.exit_program)
        
        self.matcher_page_vertical_padding_between_widgets = 5
        matcher_title_label.grid(row = 0, column = 0, columnspan = 2)
        self.drive_dropdown.grid(row = 1, column = 0, pady = self.matcher_page_vertical_padding_between_widgets)
        self.standard_template_dropdown.grid(row = 1, column = 1, pady = self.matcher_page_vertical_padding_between_widgets)
        self.match_button.grid(row = 2, column = 0, columnspan = 2, pady = self.matcher_page_vertical_padding_between_widgets)
        self.matched_list.grid(row = 3, column = 0, columnspan = 2, pady = self.matcher_page_vertical_padding_between_widgets)
        self.reset_matches_button.grid(row = 4, column = 0, columnspan = 2, pady = self.matcher_page_vertical_padding_between_widgets)
        self.confirm_matches_button.grid(row = 5, column = 0, columnspan = 2, pady = self.matcher_page_vertical_padding_between_widgets)
        self.progress_label.grid(row = 6, column = 0, columnspan = 2, pady = self.matcher_page_vertical_padding_between_widgets)
        self.exit_program_button.grid(row = 7, column = 0, columnspan = 2, pady = self.matcher_page_vertical_padding_between_widgets)

        self.reset_matches_button.configure(state="disabled")

        self.vsb.pack_forget()
        self.configuration_page_canvas.pack_forget()
        self.configuration_page.pack_forget()
        self.matcher_page.pack()
    
    # Extract the attribute of SPEL tags from Excel file
    # Attribute include address, name and comment
    def process_SPEL_output(self, spel_output_csv_filename):
        
        k = 0
        addressNum = 0
        signalNum = 0
        commentNum = 0
        numOfCol = 0
        is_csv_valid = True
        is_row_valid = False
        spel_tag_list = []
        with open(spel_output_csv_filename) as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                if k == 0:
                    is_row_valid = True
                    for i in range(len(row)):
                        if (row[i] == 'Address'):
                            addressNum = i
                            numOfCol += 1
                        elif (row[i] == 'Signal ID'):
                            signalNum = i
                            numOfCol += 1
                        elif (row[i] == 'Signal comment'):
                            commentNum = i
                            numOfCol += 1
                    k = 1
                else:
                    if (numOfCol != 3):
                        self.create_error_message("Invalid SPEL CSV File!","The SPEL output file does not have the correct column headers.")
                        is_csv_valid = False
                        return spel_tag_list, is_csv_valid, is_row_valid
                    if (row[signalNum] != ''):
                        spel_tag_list.append([row[addressNum],row[signalNum],row[commentNum]])
                    
            
        return spel_tag_list, is_csv_valid, is_row_valid

    def extract_drives_from_SPEL_output(self, processed_spel_output):
        
        # Categorizes the processed signals into different drives eg. PS01, HP01.
        signal_ids = []
        for signal in processed_spel_output:
            signal_ids.append(signal[1])

        # Creates a dictionary containing the drives and their related signals
        drives_dict = {}
        k = 0
        uncategorized_tags = []
        for signal_id in signal_ids:
            drive = self.extract_drive_from_signal_ID(signal_id, self.area_code)
            if drive == "Error":
                return
            # Handle uncategorised TAGS HARDCODED
            if drive != 0:
                k += 1
                drives_dict[drive] = [signal_id for signal_id in signal_ids if drive in signal_id]
            else:
                uncategorized_tags.append(signal_id)

        if k == 0:
            self.create_error_message("Invalid Area Code!","Area Code specified does not match with SPEL output file.")
            return

        # Create a list of drives
        drives = []
        for drive in drives_dict.keys():
            drives.append(drive)

        # Returns a list of drives and a dictionary containing the drives and their related signals
        return drives, drives_dict, uncategorized_tags

    def extract_drive_from_signal_ID (self, signalID, signal_area_code):
        
        # Extracts the drive from a signal ID e.g. PS01 from TL0_PS01_RUN_I
        # HARDCODED UNDERSCORE
        symbol = self.SPEL_output_delimiter_structure_entry.get()
        if len(signalID.split(symbol)) == 1:
            self.create_error_message("Invalid SPEL Delimiter!", "The SPEL output CSV file supplied is not using the specified Delimiter.")
            return "Error"
        else:
            if signal_area_code == '':
                drive = signalID.split(symbol)[0]
                return drive
            elif signalID.split(symbol)[0] == signal_area_code:
                drive = signalID.split(symbol)[1]
                return drive
            else:
                drive = 0
                return drive


    def create_copy_of_standard_template_xef_file_and_open_access_to_copied_file(self, standard_template_filename):
        shutil.copy(standard_template_filename, os.path.join(os.getcwd(), standard_template_filename.split(".")[0] + "-copy.xef")) 
        tree = ET.parse(standard_template_filename.split(".")[0] + "-copy.xef")
        self.root = tree.getroot()

    def extract_plc_standard_templates_from_copy_of_standard_template_xef_file(self):
        standard_template_names = []
        for standard_template in self.root.iter(self.identProgram_section_name):
            standard_template_names.append(standard_template.get('name'))
        return standard_template_names

    def separate_plc_standard_templates_from_standard_template_xef_file_into_different_xbd_files(self):
        
        # Convert the standard template PLC code into string and stored in a list
        standard_programs = []
        for standard_program_element in self.root.iter(self.program_section_name):
            standard_programs.append("\t<program>"+str(self.convert_xef_element_to_string(standard_program_element)+"</program>"))
        
        # Store the standard template PLC code and standard template name in the inner list
        identified_standard_templates = []
        for i in range(len(self.standard_template_names)):
            identified_standard_templates.append([self.standard_template_names[i], standard_programs[i]])
        
        # Write each standard template PLC code into different XBD files
        for identified_standard_template in identified_standard_templates:
            file = open(identified_standard_template[0].lower()+"_template.xbd", 'w')
            file.write(identified_standard_template[1])
            file.close()

    def convert_xef_element_to_string(self, element):
        s = element.text or ""
        for sub_element in element:
            s += ET.tostring(sub_element)
        s += element.tail
        return s

    def extract_unknown_tags_from_a_standard_template(self, standard_template_filename):
        
        # Intialise the empty lists and extract the file into element tree format
        all_tags = []
        tree = ET.parse(standard_template_filename)
        xml_elements_and_attribute_pairs = []
        
        # Extract the attribute of each element into dictionary format
        # Then store the dictionary values in a inner list
        for element in tree.iter():
            # Hardcoded it seems like you are not using the element.tag  
            xml_elements_and_attribute_pairs.append([element.tag, element.attrib.values()])
        
        # Check whether each of the dictionary values contain the standard template prefix, Eg: XXX_YYYY_
        for xml_elements_and_attribute_values_pair in xml_elements_and_attribute_pairs:
            for attribute_value in xml_elements_and_attribute_values_pair[1]:
                if self.naming_convention in attribute_value:
                    if attribute_value not in all_tags:
                        # Stored the unknown tags with standard template prefix in a list 
                        all_tags.append(attribute_value)

        return all_tags

    def read_current_project_plc_code_file(self,filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        generatedCodeList = []
        DDTSourcefileList = []
        FBIMaxNum = 0
        for child in root:
            if (child.tag == 'tempRoot'):
                for element in child:
                    if element.tag == 'DDTSource':
                        DDTSourcefileList.append(element.attrib['DDTName'])
                    
                    for subElement in element:
                        if element.tag == 'program':
                            if 'name' in subElement.attrib.keys():
                                generatedCodeList.append(subElement.attrib['name'])
            if (child.tag == self.dataBlock_section_name):
                for element in child:
                    FBIName = element.attrib['name']
                    if FBIName.find('FBI') != -1:
                        FBINum = int(FBIName.split('_')[1])
                        if FBINum > FBIMaxNum:
                            FBIMaxNum = FBINum
        FBIMaxNum += 1
        
        return generatedCodeList, DDTSourcefileList, FBIMaxNum

    def write_config_file(self, driveDict):
        config = configparser.ConfigParser()
        # Set the parser to be case sensitive
        config.optionxform = str
        
        # Section for users to define project specific information
        config.add_section('Project Specific Information')
        config.set('Project Specific Information','Standard Template Naming Convention', self.naming_convention)
        config.set('Project Specific Information','Area Naming Convention', self.SPEL_output_area_code_entry.get())
        config.set('Project Specific Information','Standard Template Symbol Convention', self.standard_template_delimiter_structure_entry.get())
        config.set('Project Specific Information','SPEL Output Symbol Convention', self.SPEL_output_delimiter_structure_entry.get())
        
        # Section to give users instruction on how to use the configuration file
        config.add_section('Instruction')
        config.set('Instruction','a','Users are require to fill up the relevant information for all the tags in standard template.')
        config.set('Instruction','i','Insert the SPEL signal ID without the prefix that matches to the I/O tags, Eg: TLO_PS01_RUN_O => RUN_O')
        config.set('Instruction','ii','Insert \'CBT\' for the unmatched I/O tags')
        config.set('Instruction','iii','Insert \'nil\' for the non-I/O tags, Eg: alarm, command tags')
        config.set('Instruction','iv','Insert the standard template typeName defined in the datablock section for hierarchy structure standard template, Eg: Fan1DDT')
          
        
        for drive in driveDict.keys():
            # Create a section for each of the standard template
            config.add_section(drive)
            
            # Allow user to define the typeName for the variables of hierarchy structure standard template
            if(self.standard_template_delimiter_structure_entry.get() == '.'):
                config.set(drive, 'Standard Template TypeName', '')
                
            for signal in driveDict[drive]:
                # List all the tags in standard template under their relevant sections 
                config.set(drive,signal,'')
        
        self.config_filename = asksaveasfilename(defaultextension=".ini")
        if self.config_filename == None:
            return
        file = open(self.config_filename,'w')
        # Write the configuration to the file
        config.write(file)
        file.close()

    def match_drive_to_standard_template(self):
        if self.drive_dropdown_options or self.standard_template_dropdown_options:
            currentDrive = self.drive_selected.get()
            driveInUsedList, ddtSourceFileCopiedList, self.FBIMaxNumber = self.read_current_project_plc_code_file(self.plc_skeleton_xef_filename)
            if currentDrive in driveInUsedList:
                self.create_error_message("Invalid Drive!", "Drive already exists in PLC skeleton file!")
            else:
                self.matched_drive_standard_template_pairs.append([currentDrive, self.standard_template_selected.get()])
            self.drive_dropdown_options.remove(self.drive_selected.get())
            self.repopulate_dropdown(self.drive_dropdown, self.drive_dropdown_options, self.drive_selected)

            matched_list_text = ""
            for matched_drive_standard_template_pair in self.matched_drive_standard_template_pairs:
                matched_list_text += (matched_drive_standard_template_pair[0] + " - " + matched_drive_standard_template_pair[1] + "\n")
            self.matched_list.config(text = matched_list_text)

            self.reset_matches_button.configure(state="active")

            # Move Reset and Exit buttons down to make space to illustrate matches
            self.reset_matches_button.grid(row = len(self.matched_drive_standard_template_pairs)+3, column = 0, columnspan = 2, pady = self.matcher_page_vertical_padding_between_widgets)
            self.confirm_matches_button.grid(row = len(self.matched_drive_standard_template_pairs)+4, column = 0, columnspan = 2, pady = self.matcher_page_vertical_padding_between_widgets)
            self.progress_label.grid(row = len(self.matched_drive_standard_template_pairs)+5, column = 0, columnspan = 2, pady = self.matcher_page_vertical_padding_between_widgets)
            self.exit_program_button.grid(row = len(self.matched_drive_standard_template_pairs)+6, column = 0, columnspan = 2, pady = self.matcher_page_vertical_padding_between_widgets)

        if len(self.drive_dropdown_options) <= 0 or len(self.standard_template_dropdown_options) <= 0:
            self.drive_dropdown.configure(state="disabled")
            self.standard_template_dropdown.configure(state="disabled")
            self.match_button.configure(state="disabled")

    def repopulate_dropdown(self, dropdown, dropdown_options, selection_variable):
        if dropdown_options:
            dropdown['menu'].delete(0, "end")
            for option in dropdown_options:
                dropdown['menu'].add_command(label=option, command=lambda option=option: selection_variable.set(option))

                selection_variable.set(dropdown_options[0])

    def confirm_matches(self):
        self.toplevel = Toplevel(self)
        self.progressbar = ttk.Progressbar(self.toplevel, orient = HORIZONTAL, mode = 'indeterminate')
        self.progressbar.pack()
        self.progressbar.start()
        
        self.drive_dropdown.configure(state="disabled")
        self.standard_template_dropdown.configure(state="disabled")
        self.reset_matches_button.configure(state="disabled")
        self.match_button.configure(state="disabled")
        self.confirm_matches_button.configure(state="disabled")
        self.exit_program_button.configure(state="disabled")

        self.progress_label.config(text = "Generating PLC code...")
        self.after(850*len(self.matched_drive_standard_template_pairs), self.update_progress_label)
        self.after(850*len(self.matched_drive_standard_template_pairs)+100, self.generate_plc_code)

    def update_progress_label(self):
        self.progress_label.config(text = "Saving code... Please wait..")

    def generate_plc_code(self):
        # Generate the PLC logic code and copy to the project skeleton file under the 'Program' section
        self.unallocated_tags = []
        standard_templates_processed = []
        for matched_drive_standard_template_pair in self.matched_drive_standard_template_pairs:
            self.replace_unidentified_tags_in_standard_template_with_processed_tags(matched_drive_standard_template_pair[1].lower() + "_template.xbd", matched_drive_standard_template_pair[0], matched_drive_standard_template_pair[1])
            standard_templates_processed.append(matched_drive_standard_template_pair[0].lower() + "_processed.xbd")
        
        self.combine_processed_standard_templates(standard_templates_processed)
        self.copy_xml_child_to_parent("combined_processed_standard_templates.xef", self.plc_skeleton_xef_filename,self.program_section_name)

        FBIvariableList = self.extract_FBI_type(self.standard_template_xef_filename,self.FBIfinalmatchingList)
        self.create_ele_var(self.generated_plc_code_filename, FBIvariableList,False)

        # Define all the variables used in the Elementary Variable under the 'Datablock' section
        # Hierarchy structure standard template
        if (self.standard_template_delimiter_structure_entry.get() == '.'):   
            self.copy_variable_from_hierarchy_standard_template(self.generated_plc_code_filename,self.standard_template_xef_filename,self.drive_code_structure_entry.get())
        else:
            # Flat structure standard template
            for matched_drive_standard_template_pair in self.matched_drive_standard_template_pairs:
                all_tags = self.extract_unknown_tags_from_a_standard_template(matched_drive_standard_template_pair[1].lower() + "_template.xbd")
                indexList = []
                self.drives, self.drives_dict, self.uncategorized_tags = self.extract_drives_from_SPEL_output(self.processed_spel_output)
                std_template_signals = self.drives_dict[matched_drive_standard_template_pair[0]]

                TAGinfo = self.find_tag_char_info_from_stand_template(self.standard_template_xef_filename,all_tags,matched_drive_standard_template_pair[0],matched_drive_standard_template_pair[1],std_template_signals,indexList)

                changed_tag_info = self.change_std_tag_name_to_SPEL_tag_name(TAGinfo,matched_drive_standard_template_pair[0],matched_drive_standard_template_pair[1],std_template_signals,indexList)

                self.create_ele_var(self.generated_plc_code_filename,changed_tag_info,True)
                
        # Match the signal tags to the correct input and output addresses under the 'I/O Remapping' section
        # Copy ALL the SPEL output from excel file to I/O remapping HARDCODED
        self.remap_IO_in_plc_program_skeleton(self.processed_spel_output, self.generated_plc_code_filename)
        
        # Initialise the name of the program generated under 'logicConf' section
        for matched_drive_standard_template_pair in self.matched_drive_standard_template_pairs:
            self.add_sectionDesc(self.generated_plc_code_filename, matched_drive_standard_template_pair[0])

        self.progress_label.config(text = "PLC code generated. Handling unallocated tags...")
        self.toplevel.destroy()

        # Obtain the unallocated tags and stored them in a CSV file
        uncategorized_and_unallocated_tags = []

        if len(self.unallocated_tags[0]) != 0:
            for unallocated_tag in self.unallocated_tags[0]:
                uncategorized_and_unallocated_tags.append(unallocated_tag)

        if len(self.uncategorized_tags) != 0:
            for uncategorized_tag in self.uncategorized_tags:
                uncategorized_and_unallocated_tags.append(uncategorized_tag) 

        if len(uncategorized_and_unallocated_tags) != 0:
            uncategorized_and_unallocated_tags_saved = False
            while uncategorized_and_unallocated_tags_saved is False:
                tkMessageBox.showinfo("Saving Unallocated Tags...", "Please select where you'd like to save the unallocated tags. Please ensure it is a .csv file.")
                self.uncategorized_and_unallocated_tags_filename = asksaveasfilename(defaultextension=".csv")
                if self.uncategorized_and_unallocated_tags_filename != None and self.uncategorized_and_unallocated_tags_filename.split(".")[-1] == "csv":
                    uncategorized_and_unallocated_tags_saved = True
                else:
                    uncategorized_and_unallocated_tags_saved = False
            uncategorized_and_unallocated_tags = np.array(uncategorized_and_unallocated_tags)
            self.write_unallocated_and_uncategorised_tags_to_csv(self.uncategorized_and_unallocated_tags_filename,uncategorized_and_unallocated_tags)
            # uncategorized_and_unallocated_tags_dataframe = pandas.DataFrame(uncategorized_and_unallocated_tags)
            # uncategorized_and_unallocated_tags_dataframe.to_csv(self.uncategorized_and_unallocated_tags_filename, index=False)  
        
        if len(uncategorized_and_unallocated_tags) == 0:
            self.progress_label.config(text = "No unallocated tags. PLC code generated")
        else:
            self.progress_label.config(text = "PLC code generated and unallocated tags handled.")

        self.reset_matches_button.configure(state="active")
        self.exit_program_button.configure(state="active")

        self.remove_placeholder_files()
    
    def write_unallocated_and_uncategorised_tags_to_csv(self,filename,unallocateTagList):

        with open(filename, 'w') as csvfile:
            fieldnames = ['Unallocated tags']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for tag in unallocateTagList:
                writer.writerow({'Unallocated tags':tag})
                
    def replace_unidentified_tags_in_standard_template_with_processed_tags(self, standard_template_filename, standard_template_drive, standard_template):
        
        # Initialise empty lists and parameters required
        index_list = []
        # HARDCODED is thi used?
        xml_element_and_attribute_value_pairs = []
        self.drives, self.drives_dict, self.uncategorized_tags = self.extract_drives_from_SPEL_output(self.processed_spel_output)
        std_template_signals = self.drives_dict[standard_template_drive]
        tree = ET.parse(standard_template_filename)

        for element in tree.iter():
            # Change the name of the identProgram to the drive name
            if element.tag == "identProgram":
                element.set("name", standard_template_drive)
            # Loop through the file and process each of the standard template tag
            for attribute, attribute_value in element.attrib.iteritems():
                if self.naming_convention in attribute_value:
                    processed_tag, index_list = self.manipulate_standard_template_tag(attribute_value, standard_template_drive, standard_template, std_template_signals, index_list)
                    element.set(attribute, processed_tag)
        
        # Replaced the FBI instances variable with a news instance
        root = tree.getroot()
        FBImatchingList = []
        FBINames = []
        for child in root.iter('FFBBlock'):
            FBIName = child.attrib['instanceName']
            if FBIName.find('FBI')!= -1:
                if (FBIName not in FBINames):
                    FBINames.append(FBIName)
                FBInewInstance = 'FBI_' + str(self.FBIMaxNumber)
                child.set('instanceName',FBInewInstance)
                FBImatchingList.append([FBIName,FBInewInstance])
                self.FBIfinalmatchingList.append([FBIName,FBInewInstance])
                self.FBIMaxNumber += 1
                
        for child in root.iter('linkFB'):
            for element in child:
                elementDict = element.attrib
                if 'parentObjectName' in elementDict.keys():
                    parentObjectName = element.attrib['parentObjectName']
                    if parentObjectName.find('FBI_') != -1:
                        FBIcurrentInstance = parentObjectName
                        for match in FBImatchingList:
                            if (match[0] == FBIcurrentInstance):
                                element.set('parentObjectName',match[1])
        
        # Write processed PLC logic code into file
        tree.write(open(standard_template_drive.lower()+"_processed.xbd", 'w'))

        index_list = self.remove_duplicate(index_list)
        self.unallocated_tags.append(self.get_unallocated_tag(std_template_signals, index_list))
        
        
    def extract_FBI_type(self,filename,FBImatchingList):
        tree = ET.parse(filename)
        root = tree.getroot()
        FBIvariableList = []
        for child in root.iter(self.dataBlock_section_name):
            for element in child:
                variableDict = element.attrib
                FBIName = variableDict['name']
                for  match in FBImatchingList:
                    if (match[0] == FBIName):
                        FBIvariableList.append([match[1],variableDict['typeName']])
                        
        return FBIvariableList
        
    def change_prefix_of_tag(self,areaNaming,drive_tag,symbol,standard_template_tag,stdTempPrefix):
        
        # Replace the prefix of standard template tag with correct area naming and drive name
        # XXX_YYYY_RUN_O  =>  TLO_PS01_RUN_O
        manipulatedTAG = ''
        filteredTAG = standard_template_tag.replace(stdTempPrefix,'')
        manipulatedTAG = areaNaming + drive_tag + symbol + filteredTAG
       
        return manipulatedTAG
    
    def manipulate_SPEL_output_tag(self,SPEL_output_tag, driveList):
        
        # Extract the user defined information from the configuration file

        configDict, stdTempTypeNameList = self.read_config_file(self.config_filename)
        stdTempPrefix = self.naming_convention
        areaNaming = self.SPEL_output_area_code_entry.get()
        symbolStdTemp = self.standard_template_delimiter_structure_entry.get()
        symbolSPEL = self.SPEL_output_delimiter_structure_entry.get()
        
        # Append different symbol convention to the area naming, given that the SPEL tags have an area name
        if (areaNaming != ''):
            areaNamingSPEL = areaNaming + symbolSPEL
            areaNamingStdTemp = areaNaming + symbolStdTemp
        else:
            areaNamingSPEL = ''
            areaNamingStdTemp = ''
        
        # Identify the drive name from the SPEL tags
        drive_tag = ''
        for drive in driveList:
            if (SPEL_output_tag.find(drive) != -1):
                drive_tag = drive
                break
        
        # Identify the name of the standard template which the drive is matched to
        standard_template = ''  
        manipulatedTAG = ''
        for matched_drive_standard_template_pair in self.matched_drive_standard_template_pairs:
            if matched_drive_standard_template_pair[0] == drive_tag:
                standard_template = matched_drive_standard_template_pair[1]
                break  

        # Extract the matching list of a standard template from a dictionary
        if standard_template != '':
            matchingList = self.get_matching_list(configDict, standard_template)
            
            # If the SPEL tags have a match, change the prefix of the item that the tags are matched to
            # Otherwise append CBT to the SPEL tags
            for match in matchingList:
                matchSignal = areaNamingSPEL + drive_tag + symbolSPEL + match[1]
                # Check if the suffix of SPEL tags found in the matching list
                if (SPEL_output_tag == matchSignal):
                    standard_template_tag = match[0]
                    manipulatedTAG = self.change_prefix_of_tag(areaNamingStdTemp,drive_tag,symbolStdTemp,standard_template_tag,stdTempPrefix)
                    break
                else:
                    manipulatedTAG = self.append_cbt_to_unallocated_IO_standard_template_tag(SPEL_output_tag,symbolSPEL)
                
        return manipulatedTAG
    
    def manipulate_standard_template_tag(self, standard_template_tag,drive_tag,standard_template,signal_list,index_list):
        
        # Extract the user defined information from the configuration file
        configDict, stdTempTypeNameList = self.read_config_file(self.config_filename)
        stdTempPrefix = self.naming_convention
        areaNaming = self.SPEL_output_area_code_entry.get()
        symbolStdTemp = self.standard_template_delimiter_structure_entry.get()
        symbolSPEL = self.SPEL_output_delimiter_structure_entry.get()
        
        # Append different symbol convention to the area naming, given that the SPEL tags have an area name
        if (areaNaming != ''):
            areaNamingSPEL = areaNaming + symbolSPEL
            areaNamingStdTemp = areaNaming + symbolStdTemp
        else:
            areaNamingSPEL = ''
            areaNamingStdTemp = ''

        # Extract the matching list of a standard template from a dictionary
        matchingList = self.get_matching_list(configDict,standard_template)
        
        manipulatedTAG = ''
        for match in matchingList:
            if (standard_template_tag == match[0]):
                if (match[1] == 'CBT'):
                    # Append 'CBT' to the tag if the tag is matched to 'CBT'
                    manipulatedTAG = self.append_cbt_to_unallocated_IO_standard_template_tag(standard_template_tag,symbolStdTemp)
                elif(match[1] == 'nil'):
                    # Change the prefix of the tag if the tag is matched to 'nil'
                    manipulatedTAG = self.change_prefix_of_tag(areaNamingStdTemp,drive_tag,symbolStdTemp,standard_template_tag,stdTempPrefix)
                else:
                    # Change the prefix of the item that the tag is matched to
                    
                    matchSignal = areaNamingSPEL + drive_tag + symbolSPEL + match[1]
                    # Check if the signal list contains this particular signal
                    for j, signal in enumerate(signal_list):
                        if(signal == matchSignal):
                            manipulatedTAG = self.change_prefix_of_tag(areaNamingStdTemp,drive_tag,symbolStdTemp,standard_template_tag,stdTempPrefix)
                            # Stored the index of the matched signal in a list
                            index_list.append(j)

                break
        
        # Append 'CBT' to the tag, if the tag has not been manipulated 
        if manipulatedTAG == '':
            manipulatedTAG = self.append_cbt_to_unallocated_IO_standard_template_tag(standard_template_tag,symbolStdTemp)
            
        return manipulatedTAG, index_list

    def read_config_file(self, filename):
        config = configparser.ConfigParser()
        # Set the parser to be case sensitive
        config.optionxform = str
        config.read(filename)
        # Extract a list of sections from the configuration file
        sections = config.sections()
        
        # Initialise new variables
        configDict = {}
        stdTempPrefix = ''
        areaNaming = ''
        symbolStdTemp = '_'
        stdTempTypeNameList = []
        
        for section in sections:
            matchingList = []
            # Extract a list of options from each section
            options = config.options(section)
            
            # Extract project specific information
            if (section == 'Project Specific Information'):
                continue
                """
                for option in options:
                    value = config.get(section,option)
                    # Obtain the standard template naming convention
                    if (option == 'Standard Template Naming Convention'):
                        stdTempPrefix = value
                    # Obtain the area naming convention
                    elif (option == 'Area Naming Convention'):
                        areaNaming = value
                    # Obtain the symbol convention for standard template and SPEL output
                    # '.' symbol convention represents hierarchy structure
                    elif (option == 'Standard Template Symbol Convention'):
                        symbolStdTemp = value
                    elif (option == 'SPEL Output Symbol Convention'):
                        symbolSPEL = value
                """
                
            # Skip the Instruction section
            elif (section == 'Instruction'):
                continue
            
            # Create list of matching pairs
            else:
                for option in options:  
                    # Store the information in a list of lists only for hierarchy structure
                    # Where the inner list contain the standard template name and its variable typeName 
                    # Eg: Std_Fan1, Fan1DDT
                    if option == 'Standard Template TypeName':
                        value = config.get(section,option)
                        stdTempTypeNameList.append([section,value])
                    else:
                        # Store the standard template tags & its corresponding pair in a list
                        pairList = []
                        value = config.get(section,option)
                        pairList.append(option)
                        pairList.append(value)
                        
                        #Store all the pairs in a larger list
                        matchingList.append(pairList)
                        
                # Store the matching list in a dictionary under its relevant standard template
                configDict[section] = matchingList 
        return configDict, stdTempTypeNameList
    
    def remove_duplicate(self, index_list):
        # Remove the repeated numbers stored in a list 
        new_index_list = []
        for i in index_list:
            # Only append the item into the new list, if it is not found in the list
            if i not in new_index_list:
                new_index_list.append(i)
        return new_index_list

    def get_unallocated_tag(self, signal_list,index_list):
        # Obtain the unallocated tags from the signal list
        new_signal_list = []
        
        # Set the signal to empty string, if its index number is found in the list
        for index in index_list:
            signal_list [int(index)] = ''
        
        # Only append the item into the new list, if it is not an empty string
        for signal in signal_list:
            if signal != '':
                new_signal_list.append(signal)
            
        return new_signal_list  

    def get_matching_list(self,templateDict,stdTemp = 'all'):
        # Extract all the matching pairs for different standard templates and store them in a list
        # Not USED HARDCODED
        if (stdTemp == 'all'):
            matchingList = []
            keyList = templateDict.keys()
            for key in keyList:
                matchList = templateDict[key]
                matchingList = matchingList + matchList
        else:
            # Extract the matching pair list for the associated standard template
            matchingList = templateDict[stdTemp]
        
        return matchingList   

    def append_cbt_to_unallocated_IO_standard_template_tag(self, standard_template_tag,symbol):
        # XXX_YYYY_RUN_O  => CBT_XXX_YYYY_RUN_O
        appended_cbt_tag = "CBT"+ symbol + standard_template_tag      
        return appended_cbt_tag

    def combine_processed_standard_templates(self, standard_template_filename_array):
        file_contents = ""
        for standard_template_filename in standard_template_filename_array:
            file_content = open(standard_template_filename, "r")
            file_contents += file_content.read() + "\n"

        file_contents = "<tempRoot>\n" + file_contents + "</tempRoot>"
        combined = open("combined_processed_standard_templates.xef", "w")
        combined.write(file_contents)
        combined.close()

    def copy_xml_child_to_parent(self, child_xml, parent_xml,sectionName):
        
        tree_parent = ET.parse(parent_xml)
        root_parent = tree_parent.getroot()
        
        file_to_copy = open(child_xml, "r")
        file_content = file_to_copy.read()
        file_to_copy.close()
        content_to_copy = ET.fromstring(file_content)

        index = self.index_for_inserting_child(root_parent,sectionName)
        
        root_parent.insert(index*-1,content_to_copy)
        
        generated_plc_code_saved = False
        while generated_plc_code_saved is False:
            tkMessageBox.showinfo("Saving Generated PLC Code...", "Please select where you'd like to save the generated PLC code. Please ensure it is a .xef file.")
            self.generated_plc_code_filename = asksaveasfilename(defaultextension=".xef")
            if self.generated_plc_code_filename != "" and self.generated_plc_code_filename.split(".")[-1] == "xef":
                generated_plc_code_saved = True
            else:
                generated_plc_code_saved = False
        
        tree_parent.write(self.generated_plc_code_filename)

    def index_for_inserting_child(self, parentRoot,sectionName):
        
        childList = []
        # Obtain a list which contains the section name
        for child in parentRoot:
            childList.append(child.tag)
            
        # Reverse the list such that the index for adding a new section after the section with the same name can be obtained
        childList.reverse()
        index = 0
        for i in range(len(childList)):
            if childList[i] == sectionName: 
                index = i
                break
            
        return index

    def remap_IO_in_plc_program_skeleton(self, spel_output_list, plc_filename):

        # Read the xml file and find the element of descriptionFFB
        tree = ET.parse(plc_filename)
        foundDFFB = tree.findall('.//descriptionFFB')
        root=tree.getroot()

        pairlist=[]
        for child in foundDFFB:
            for element in child: # for the element under descriptionFFB
                foundEP = element.get('effectiveParameter')
                # find the element that contains effectiveParameter
                if foundEP is not None: 
                    # read the data from the list
                    for  row in spel_output_list: 
                        # if the effectiveParameter is same as the address from the list
                        if (row[0] == foundEP): 
                            standard_template_tag = self.manipulate_SPEL_output_tag(row[1], self.drives)
                            if standard_template_tag != '':
                                row[1] = standard_template_tag

                                if (row[1].find('CBT')!= -1):
                                    pair = [row[1], 'EBOOL', row[2]]
                                    pairlist.append(pair)
                                # if the matched adress is input
                                if element.get('formalParameter') == 'IN': 
                                    # for the element under the same description FFB
                                    for element in child: 
                                        # find the element with formalParameter is OUT
                                        if element.get('formalParameter') == 'OUT': 
                                            # add signal id as effectiveParameter
                                            element.set('effectiveParameter', row[1]) 
                                # if the matched address is output
                                elif element.get('formalParameter') == 'OUT': 
                                    # for the element under the same description FFB
                                    for element in child: 
                                        # find the element with formalParameter is IN
                                        if element.get('formalParameter') == 'IN': 
                                            # add signal id as effectiveParameter
                                            element.set('effectiveParameter', row[1]) 
        
        # Only write the SPEL tags into the 'datablock' section for non-Hierarchy structure standard template
        if (self.standard_template_delimiter_structure_entry.get() != '.'):   
            for child in root:
                if child.tag == self.dataBlock_section_name:
    
                    for pair in pairlist:
                        new_sig = ET.SubElement(child, "variables", attrib={"name": pair[0],"typeName": pair[1]})
                        new_sig_comm = ET.SubElement(new_sig,"comment")
                        new_sig_comm.text = pair[2]
    
                        self.indent(new_sig,level=4)
                        self.indent(new_sig_comm,level=4)

        # write back to the original file
        tree.write(plc_filename) 
        
        return

    def add_sectionDesc(self, plc_filename, name):
        # Read the plc file
        tree = ET.parse(plc_filename) 
        # locate the element called taskDesc
        foundTD = tree.find('.//taskDesc') 
        # zcreate a new sectionDEsc element
        sectionDesc = ET.Element("sectionDesc", {"name": name}) 
        # for new sectionDesc to line up with others
        sectionDesc.tail = '\n\t\t\t\t' 
        # insert the new element on top
        foundTD.insert(0,sectionDesc) 
        
        # this will append all the new elements to a single line.
        # foundTD.append(sectionDesc) # append the sectionDesc element under taskDesc
        
        # write the created sessionDesc to the plc file
        tree.write(plc_filename) 

        return

    def indent(self, elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def find_tag_char_info_from_stand_template(self, standard_template_filename, tag_list, drive_name,standard_template,signal_list,index_list):

        element_name = ''
        element_type = ''
        element_comment = ''
        final_list = []
        # Initiliase pair_list to store tag information

        tree = ET.parse(standard_template_filename)
        root = tree.getroot()
        
        # Loop over tree root for each tag
        for tag in tag_list:
            pair_list = []
            for child in root:
                if child.tag == self.dataBlock_section_name:
                    for variable_element in child:
                        elementDict = variable_element.attrib
                        variableName = elementDict['name']
                        variableTypeName = elementDict['typeName']
                        if tag == variableName:
                            # Check if tag name is the same as specifed in the variable tree
                            element_name = variableName
                        
                            #element_name_new = self.manipulate_standard_template_tag(element_name,drive_name,standard_template,signal_list,index_list)[0]
                            
                            element_type = variableTypeName

                            for comment_element in variable_element:
                                if comment_element.text == None:
                                    break
                                element_comment = comment_element.text.replace(self.drive_code_structure_entry.get(),drive_name)
                                # Replace (YYYY) with drive name in comment
                            pair_list = [element_name,element_type,element_comment]
        
            if len(pair_list)!=0:
                final_list.append(pair_list)

            # Each list in pair_list contains tag information for each tag
        
        return final_list
    
    def copy_variable_from_hierarchy_standard_template(self,project_output_file,standard_template_file,stdTempPrefix):
        
        # Initialise variables and empty lists
        tree = ET.parse(standard_template_file)
        root = tree.getroot()
        standard_template_typeNames = []
        variableList = []
        
        # Extract the user defined information from the configuration file
        configDict, stdTempTypeNameList = self.read_config_file(self.config_filename)
        stdTempFullPrefix = self.naming_convention
        areaNaming = self.SPEL_output_area_code_entry.get()
        symbolStdTemp = self.standard_template_delimiter_structure_entry.get()
        symbolSPEL = self.SPEL_output_delimiter_structure_entry.get()
        
        # Extract the standard template variable typeName using the standard template name
        for matched_drive_standard_template_pair in self.matched_drive_standard_template_pairs:
            stdTempTypeName = ''
            for stdTempTypeNamePair in stdTempTypeNameList:
                if (matched_drive_standard_template_pair[1] == stdTempTypeNamePair[0]):
                    stdTempTypeName = stdTempTypeNamePair[1]
                    break
            
            # Extract the comment of the variable using the drive name structure and variable typeName, Eg: YYYYY, Fan1DDT
            for child in root.iter(self.dataBlock_section_name):
                for element in child:
                    elementDict = element.attrib            
                    variableName = elementDict['name']
                    variableTypeName = elementDict['typeName']
                    if(variableName == stdTempPrefix and variableTypeName == stdTempTypeName):
                        if variableTypeName not in standard_template_typeNames:
                            standard_template_typeNames.append(variableTypeName)
                        for subElement in element:
                            if subElement.tag == 'comment':
                                variableComment = subElement.text
                                
                        # Store the drive name, variable typeName and variable comment in the inner list
                        variableList.append([matched_drive_standard_template_pair[0],variableTypeName,variableComment])
        
        # Write the variables into the 'datablock' section
        self.create_ele_var(self.generated_plc_code_filename, variableList,True)
        
        # Obtain the name of relevant DDTSource file using the variable typeName Fan1DDT, Eg: Fan1InDDT
        standard_template_structure_typeNames = []
        for standard_template_typeName in standard_template_typeNames:
            for child in root.iter(self.DDTSource_section_name):
                childAttrib = child.attrib

                if (childAttrib['DDTName'] == standard_template_typeName):
                    standard_template_structure_typeNames.append(standard_template_typeName)
                    for element in child:
                        for subElement in element:
                            attribute = subElement.attrib
                            standard_template_structure_typeNames.append(attribute['typeName'])

        # Remove the DDTSource file if they are found to be in the current project PLC code file
        driveInUsedList, ddtSourceFileCopiedList,NumNotUsed = self.read_current_project_plc_code_file(self.plc_skeleton_xef_filename)
        filtered_standard_template_structure_typeNames = []
        for standard_template_structure_typeName in standard_template_structure_typeNames:
            if standard_template_structure_typeName not in ddtSourceFileCopiedList:
                filtered_standard_template_structure_typeNames.append(standard_template_structure_typeName)
        
        # Store each of the DDTSource file required as a string in a list
        DDTSourceList = []
        DDTSourceList.append('<tempRoot>\n')
        for standard_template_structure_typeName in filtered_standard_template_structure_typeNames:
            for child in root.iter(self.DDTSource_section_name):
                childAttrib = child.attrib
                
                if (childAttrib['DDTName'] == standard_template_structure_typeName):
                    childAttribKey = child.attrib.keys()
                    childAttribValue = child.attrib.values()
                    attribString = ''
                    for i ,key in enumerate(childAttribKey):
                        attribString += ' ' + key + '="' + childAttribValue[i] + '"'

                    DDTSourceList.append('\t<DDTSource' + attribString + '>'+ str(self.convert_xef_element_to_string(child))+'</DDTSource>\n')

        DDTSourceList.append('</tempRoot>\n')
        
        # Combine all the DDTSource file together by using string concatenation
        DDTSourceTotal = ''
        for DDTSource in DDTSourceList:
            DDTSourceTotal += DDTSource
          
        # Copy the DDT Source files to the correct position in the final generated output file
        tree_parent = ET.parse(project_output_file)
        root_parent = tree_parent.getroot()
        content_to_copy = ET.fromstring(DDTSourceTotal)
        index = self.index_for_inserting_child(root_parent,self.DDTSource_section_name)
        root_parent.insert(index*-1,content_to_copy)
        tree_parent.write(self.generated_plc_code_filename)
            
    def change_std_tag_name_to_SPEL_tag_name(self, std_tag_info_list, drive_tag, standard_template, signal_list, index_list):
        # can define index inside the function (check with Brendan)

        std_tag_name_list = []
        name_changed_std_tag = []

        for pair in std_tag_info_list:
            std_tag_name_list.append(pair[0])
            

        for tag in std_tag_name_list:
            name_changed_std_tag.append(self.manipulate_standard_template_tag(tag,drive_tag,standard_template,signal_list,index_list)[0])
        # Changed tag name stored in name_changed_std_tag

        for ii, pair in enumerate(std_tag_info_list):
            pair[0] = name_changed_std_tag[ii]

        # Replace tag name in std tag info with changed tag name

        return std_tag_info_list

    def create_ele_var(self, file_to_write_ele_var_to, pair_list, commentBool):
        tree = ET.parse(file_to_write_ele_var_to)
        root = tree.getroot()

        for child in root:
            if child.tag == self.dataBlock_section_name:

                for pair in pair_list:
                    new_sig = ET.SubElement(child, "variables", attrib={"name": pair[0],"typeName": pair[1]})
                    
                    # Only insert comment if commentBool set to TRUE
                    if(commentBool):
                        new_sig_comm = ET.SubElement(new_sig,"comment")
                        new_sig_comm.text = pair[2]
                        self.indent(new_sig_comm,level=4)
                        
                    self.indent(new_sig,level=4)
                    # Indent created variable tree - not perfect

        tree.write(self.generated_plc_code_filename)

    def remove_placeholder_files(self):
        self.remove_file_list = []
        self.remove_file_list.append('combined_processed_standard_templates.xef')
        
        self.remove_file_list.append(self.standard_template_xef_filename.split(".")[0] + "-copy.xef".split("/")[-1])

        for standard_template_name in self.standard_template_names:
            template_name = standard_template_name.lower() + "_template.xbd" 
            if (template_name not in self.remove_file_list):
                self.remove_file_list.append(template_name)
            
        for matched_drive_standard_template_pair in self.matched_drive_standard_template_pairs:
            processed_template_name = matched_drive_standard_template_pair[0].lower() + "_processed.xbd"
            if (processed_template_name not in self.remove_file_list):
                self.remove_file_list.append(processed_template_name)

        for f in self.remove_file_list:
            os.remove(f)

    def create_error_message(self, error_title, error_message):
        tkMessageBox.showerror(error_title, error_message)

    def reset_matches(self):
        self.matcher_page.pack_forget()
        self.load_matcher_page()

    def exit_program(self):
        sys.exit(0)

if __name__ == "__main__":
    root = Tkinter.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
