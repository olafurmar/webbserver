# -*- coding: utf-8 -*-
"""
Created on Wed Feb 07 10:37:02 2018

@author: fkln
"""

from arena.psr2arena.utils import utf8_write, utf8_read
from inspect import currentframe, getfile
from lxml import etree
from os import mkdir, remove
from os.path import abspath, isfile, isdir, dirname, join, splitext
from shlex import split
from shutil import rmtree
from subprocess import check_call, CalledProcessError
from xml.etree.ElementTree import ElementTree, parse, tostring, fromstring, XMLParser
from xmltools.treetools import filter_xml
from zipfile import ZipFile

import sys

def get_script_folder():
    '''Returns the path to the folder containing this module.
    '''
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = abspath(dirname(getfile(currentframe())))
    
    return base_path

# Some constants
pdx_repr_filename = u'pdx.xml'
xml_header = u'''<?xml version="1.0" encoding="UTF-8" ?>
				 <?pdx_version "1.0"?>
				 <?generated_by Arena Solutions/Arena Solutions/ver 1.0/1?>\n
                 '''
dtd_start_str = u'<!DOCTYPE ProductDataeXchangePackage [\n'
dtd_end_str = u']>\n'
pdx_DTD_filename = u'2571_mod.dtd'
dtd_path = join(get_script_folder(), pdx_DTD_filename)

def dtd_validate_str(filename):
    parser = etree.XMLParser(dtd_validation=True)
    try:
        etree.parse(filename)
    except etree.XMLSyntaxError as e:
        # File did not validate
        return str(e)
    return None

def pdx_validate_str(filename):
    with ZipFile(filename) as zf:
        with zf.open('pdx.xml','r') as pdxf:
            return dtd_validate_str(pdxf)
    
class Package(object):
    '''Implements a pdx package object.
    '''
    def __init__(self, input_data):
        '''Initializes the pdx Package object by reading the pdx file data.
        '''
        self._original_pdx_file = input_data
        with ZipFile(input_data) as zf:
            # Read xml
            self._files = zf.namelist()
            try:
                xml_file = [fn for fn in self._files
                            if pdx_repr_filename in fn][0]
            except IndexError:
                # No pdx representation file found
                raise ValueError('%s not found in pdx-package' % pdx_repr_filename)
            # Now open and parse the XML file
            with zf.open(xml_file) as xml_f:
                # Get xml as string
                self._tree = parse(xml_f)
#                self._tree = ElementTree(fromstring(xml_f.read()))
    
    def filter(self, filter_list):
        '''Filters xml by removing the elements identified by each (XPath) filter.
        Files are removed if possible.
        '''
        if isinstance(filter_list, basestring):
            # Should be a string of some kind
            filter_list = (filter_list,)
        # Apply each filter once to the xml
        root = self._tree.getroot()
        fn = join(dirname(self._original_pdx_file),'temp.xml')
        # Write the xml temporarily to disk in same folder as the pdx file
        with open(fn, 'w') as temp_f:
            temp_f.write(tostring(root))
        # Filter the xml - receiving the result as a string
        filtered_xml = filter_xml(fn, filter_list)
        # Remove the temporary file
        remove(fn)
        # Update the DOM
        root = fromstring(filtered_xml)
        self._tree = ElementTree(root)
        # Now rebuild the file list based on the remaining xml
        new_file_list = []
        for node in root.findall(r'.//Attachment'):
            fn = node.attrib.get('universalResourceIdentifier')
            file_included = node.attrib.get('isFileIn').lower() == 'yes'
            if file_included and fn and fn not in new_file_list:
                new_file_list.append(fn)
        self._files = new_file_list
        
    def get_attachment_names(self):
        '''Returns a list of the filenames of files included in the PDX package.
        The pdx-xml file is not listed.
        '''
        return [fn for fn in self._files if fn != pdx_repr_filename]
    
    def get_element(self, xpath_filter):
        '''Returns a list of ElementTree Element objects matching the
        XPath expression.
        '''
        return list(self._tree.getroot().findall(xpath_filter))
    
    def xml_str(self):
        '''Returns the package xml as a string.
        '''
        with open(dtd_path, 'r') as dtd_file:
             s = (xml_header +
             dtd_start_str +
             utf8_read(dtd_file.read()) +
             dtd_end_str +
             tostring(self._tree.getroot()).decode())
        return s

    def save(self, path):
        '''Saves Package object as a pdx file, inlcuding attached files.
        Attached files are included if the original package file is still
        available at the same path.
        '''
        path = unicode(path)
        if isfile(self._original_pdx_file):
            if isdir(dirname(path)):
                arc_path = splitext(path)[0] + u'_'
                mkdir(arc_path)
                # Write the pdx-xml file
                with open(join(arc_path, pdx_repr_filename), 'w') as xml_f:
                    xml_f.write(self.xml_str())
                # Extract attachments
                with ZipFile(self._original_pdx_file, 'r') as zf0:
                    for fn in self.get_attachment_names():
                        try:
                            zf0.extract(fn, arc_path)
                        except KeyError:
                            # Sometimes (at least) Arena does not include the file
                            # Just skip it
                            pass
                # now zip up the directory
                cmd = [join(get_script_folder(),u'7z.exe'), 'a', '-tzip', path, join(arc_path, u'*.*')]
#                cmd = split('7z a -tzip %s %s' %
#                            (path, join(arc_path, u'*.*')))
                try:
                    check_call(cmd, shell=True)
                except CalledProcessError as e:
                    # Call failed - we still want to clean up
                    print '7-zip failed with return code: %s' % e.returncode
                    print 'Command run: \n%s\n' % ' '.join(cmd)
                rmtree(arc_path)
            else:
                raise IOError('Folder %s does not exist.' % dirname(path))
        else:
            raise IOError('Original pdx file, %s, does not exist.' % self._original_pdx_file)

if __name__=='__main__':
    pass
