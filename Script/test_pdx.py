# -*- coding: utf-8 -*-
"""
Created on Wed Feb 07 11:37:26 2018

@author: fkln
"""

from arena.psr2arena.utils import add_before_file_ext, utf8_read
from ffpdx import pdx
from lxml.etree import XMLParser, parse, XMLSyntaxError
from zipfile import ZipFile

import os
import pytest
import shutil

@pytest.fixture(scope='module')
def pdx_file(tmpdir_factory):
    filename = u'test_resources\\ECO-000028.pdx'
    dest_file = os.path.join(unicode(tmpdir_factory.getbasetemp()),
                             os.path.basename(filename))
    shutil.copy(os.path.abspath(filename), dest_file)
    return dest_file

@pytest.fixture(scope='module')
def pdx_change(tmpdir_factory):
    filename = u'test_resources\\ECO-000042.pdx'
    dest_file = os.path.join(unicode(tmpdir_factory.getbasetemp()),
                             os.path.basename(filename))
    shutil.copy(os.path.abspath(filename), dest_file)
    return dest_file

def test_pdx(pdx_file):
    '''Test that a pdx package can be read.
    '''
    pkg = pdx.Package(pdx_file)
    assert len(pkg.get_attachment_names()) == 5
    
def test_filter_files_from_package(pdx_file):
    '''Test that it is possible to filter a pdx package.
    '''
    pkg = pdx.Package(pdx_file)
    fn = "Sunix Pilot Build Report 20171216.pptx"
    pkg.filter(r".//Attachment[@universalResourceIdentifier='%s']" % fn)
    assert fn not in pkg.get_attachment_names()
    assert pkg.get_element(r".//*[@value='FILE-000206']") == []

def test_keep_only_included_files(pdx_change):
    '''Test that it is possible to keep only included files.
    '''
    expected_files = ('FF16_0024 0 Sealing Window Packaging Specification[1].pdf',
                      'pdx.xml')
    pkg = pdx.Package(pdx_change)
    pkg.filter(r"//@isFileIn[not(ancestor::AttachmentMarkupRowNew)];No")
    dest_file = add_before_file_ext(pdx_change, 'koi')
    pkg.save(dest_file)
    with ZipFile(dest_file) as zf:
        fl = zf.namelist()
    assert set(fl) == set(expected_files)

def test_save_pdx_package(pdx_file):
    '''Test that a filter package is saved correctly and validates.
    '''
    
    dest_file = add_before_file_ext(pdx_file, u'new')
    
    pkg = pdx.Package(pdx_file)
    pkg.save(add_before_file_ext(pdx_file, 'nochange'))
    pkg.filter(r'.//History')
    pkg.save(dest_file)
    
    e_msg = pdx.pdx_validate_str(pdx_file)
    assert e_msg == None
    print 'Original file tested OK'
    
    # then parse the resulting file
    e_msg = pdx.pdx_validate_str(dest_file)
    assert e_msg == None
        

    # Now check that the history element is gone
    with ZipFile(dest_file) as pdx_file:
        with pdx_file.open('pdx.xml','r') as xml_file:
            assert "<History>" not in xml_file.read()
    
if __name__=='__main__':
    pytest.main([r'--basetemp=c:\pytest_temp\test_pdx'])
#    pytest.main([r'--basetemp=c:\test_proddata', '-k','test_save_package'])
