#!/usr/bin/env python

###############################################
# Crappy GUI Version of the equivalence checker
###############################################

import os
import tkinter as Tk
import tkinter.filedialog
import Pmw
import unicodedata
import copy
import re
from dave.mprobo.simulatorconfig import SimulatorConfig
from dave.mprobo.testconfig import TestConfig
from configobj import ConfigObj

__VERSION__ = 0.5
__COPYRIGHT__ = '''
Copyright (c) 2014-2016 by Stanford University
All rights reserved
'''
__EMAIL__ = 'bclim@stanford.edu'

def check_file(text):
  ''' check if the file exists '''
  if len(text) > 0:
    return os.path.exists(text)
  else:
    return False

def get_screen_size(parent):
  ''' get screen size '''
  return parent.winfo_screenwidth(), parent.winfo_screenheight()

def set_position(parent):
  ''' set window position '''
  w,h = get_screen_size(parent)
  parent.geometry('+%d+%d' % (w/4, h/4))

def packWidget(widget, side='left'):
  ''' packing Widget '''
  widget.pack(fill='both', expand=1, padx=10, pady=10, side=side)

def packWidget_1(widget, side='left'):
  ''' packing Widget '''
  widget.pack(fill='x', expand=0, padx=10, pady=10, side=side)

def unicode2ascii(text):
  ''' text is the content of Tk.Text() widget '''
  _txt = text.get('1.0', 'end')
  if _txt == None:
    return ''
  else:
    return _txt.encode('ascii','ignore')

class LabeledText:
  def __init__(self, parent=None, label_text='', height=1, width=1):
    self._label = Tk.Label(parent, text=label_text)
    self._text = Tk.Text(parent, height=height, width=width, wrap=Tk.CHAR)

  def get_label(self):
    return self._label

  def get_text(self):
    return self._text

  def grid(self, row, column, **kw):
    ''' note that this takes two columns '''
    self._label.grid(row=row, column=column, **kw)
    self._text.grid(row=row, column=column+1, **kw)

  def insert(self, index, text, tags=None):
    self._text.insert(index, text, tags)

  def delete(self, index1, index2=None):
    self._text.delete(index1, index2)

  def get(self, index1, index2=None):
    return self._text.get(index1, index2)


#----------------------------------------------
class LabeledRealCounter(Pmw.Counter):
  def __init__(self, parent=None , validate={}, **kw):
    ''' set min and/or max in validate '''
    # Define the validate option dictionary.
    default_validate = {'validator' : 'real'}
    default_validate.update(validate)
    kw['datatype'] = 'real'
    kw['entryfield_validate'] = default_validate
    kw['entryfield_value'] = 50.0
    kw['labelpos'] = 'w'
    Pmw.Counter.__init__(*(self, parent), **kw)

  def getvalue(self):
    return Pmw.Counter.getvalue(self)

  def setvalue(self, value):
    return Pmw.Counter.setvalue(self, value)


#----------------------------------------------
class LabeledIntCounter(Pmw.Counter):
  def __init__(self, parent=None , validate={}, **kw):
    # Define the validate option dictionary.
    default_validate = {'validator' : 'integer', 'min' : 0, 'max' : 100}
    default_validate.update(validate)
    kw['datatype'] = 'integer'
    kw['entryfield_validate'] = default_validate
    kw['labelpos'] = 'w'
    kw['entry_width'] = 3
    kw['sticky'] = 'e'
    Pmw.Counter.__init__(*(self, parent), **kw)

  def getvalue(self):
    return Pmw.Counter.getvalue(self)

  def setvalue(self, value):
    return Pmw.Counter.setvalue(self, value)

  def disable_arrow(self):
    Pmw.Counter.component(self, 'uparrow').configure(Arrow_state='disabled')

#----------------------------------------------
class FileEntry:
  ''' Entry and a button for broswing a file are combined together.
      If you want to use this for non-file purpose, set "isFile" to false.
  '''
  def __init__(self, parent, messagebar, label_text, file_ext, isFile=False, balloon=None, appendmode=False):
    self._parent = parent
    self._isFile = isFile
    self._appendmode = appendmode
    self._msgbar = messagebar
    self._file_ext = file_ext
    self._createBody(parent, label_text)
    if balloon != None and len(balloon)==1:
      self._createBalloon(balloon)

  def set(self, value):
    ''' set the entry value '''
    self.file_entry.setentry(value)
    self.file_entry.invoke()

  def get(self):
    ''' get the entry value 
        This is very weird way to get a value '''
    x = self.file_entry.getvalue()
    self.file_entry.setvalue(x)
    return x

  def get_entry(self):
    return self.file_entry

  def _createBody(self, parent, label_text):
    ''' create entry & file open button '''
    self.file_entry = Pmw.EntryField(parent,
                      labelpos = 'w',
                      command = self._callback,
                      label_text = label_text)
    self.file_entry.bind('<FocusOut>', self._focusout)
    if self._isFile:
      self.file_btn = Tk.Button(parent, text = 'open', command = self._askFilename)

  def grid(self, row, column, **kw):
    self.file_entry.grid(row=row, column=column, **kw)
    if self._isFile:
      self.file_btn.grid(row=row, column=column+1, **kw)

  def grid_entry(self, row, column, **kw):
    self.file_entry.grid(row=row, column=column, **kw)

  def grid_button(self, row, column, **kw):
    if self._isFile:
      self.file_btn.grid(row=row, column=column, **kw)

  def _createBalloon(self, balloon):
    bl = Pmw.Balloon(self._parent)
    bl.bind(self.file_entry, balloon)

  def _askFilename(self):
    ''' browse a filename '''
    value = self.file_entry.getvalue()
    filename = self._browseFilename()
    if len(filename)>0:
      if self._appendmode:
        old_filenames = value.split(',') if len(value)>0 else []
        flist = [filename] + old_filenames
        filename = ', '.join(flist)
      self.file_entry.setvalue(filename)

  def _focusout(self, text):
    ''' check if the widget is out of focus '''
    self._callback()

  def _callback(self):
    ''' callback when the entry is updated '''
    text = self.file_entry.getvalue()
    if self._isFile and not check_file(text):
      msg_txt = 'Warning: The file does not exist or contains a string interpolation expression.'
      self._msgbar.message('warn', msg_txt)

  def change_state(self, state):
    ''' change the state of entry & button (normal or disabled) '''
    self.file_entry.configure(entry_state = state)
    if self._isFile:
      self.file_btn.configure(state = state)

  def _browseFilename(self):
    ''' browse a filename '''
    return tkinter.filedialog.askopenfilename(filetypes=self._file_ext, parent=self._parent)


#----------------------------------------------
class PortEditor:
  ''' 
  '''
  _encode_items = ['binary', 'thermometer', 'gray', 'onehot']
  def __init__(self, parent, messagebar):
    self._parent = parent
    self._msgbar = messagebar
    self.balloon = Pmw.Balloon(self._parent)
    self._createBody(self._parent)
    self._createBalloon()
    self._type_callback('analoginput')

    self._data = {}

  def set(self, value):
    ''' import data '''
    for k, v in list(value.items()):
      ptype = v['port_type']
      self._data[k] = (v['port_type'], 
                       v['description'],
                       ', '.join(v['regions']) if ptype.startswith('analog') else '', 
                       v['abstol'] if ptype=='analogoutput' else '', 
                       v['gaintol'] if ptype=='analogoutput' else '', 
                       v['bit_width'] if not ptype.startswith('analog') else '',
                       v['encode'] if not ptype.startswith('analog') else '', 
                       ', '.join(v['prohibited']) if not ptype.startswith('analog') else '', 
                       bool(v['pinned']), 
                       v['default_value'])
    keys = sorted(self._data.keys())
    self._name.setlist(keys)
    if len(keys)>0:
      self._name.selectitem(keys[0])
      self._name_callback(keys[0]) # the widget doesn't automatically call this
      self._type_callback(self._data[keys[0]][0]) # the widget doesn't automatically call this

  def get(self):
    ''' export data '''
    data = {}
    for k,v in list(self._data.items()):
      _tmp = { 'port_type': v[0],
               'description': v[1],
               'regions': v[2].split(',') if v[2] != '' else None,
               'abstol': v[3] if v[3] != '' else None,
               'gaintol': v[4] if v[4] != '' else None,
               'bit_width': int(v[5]) if v[5] != '' else None,
               'encode': v[6] if v[6] != '' else None,
               'prohibited': v[7].split(',') if v[7] != '' else [],
               'pinned': v[8],
               'default_value': v[9]
             }
      data[k] = dict([(k1,v1) for k1,v1 in list(_tmp.items()) if v1 != None])

    return data

  def update_display(self):
    pass

  def _createBody(self, parent):
    self._is_pinned = Tk.IntVar()
    self._name = Pmw.ComboBox(parent,
                  label_text = 'Port Name:',
                  labelpos='w',
                  selectioncommand = self._name_callback,
                  scrolledlist_items = [],
                  entry_width=10,
                  dropdown=1
                  )
    self._type = Pmw.OptionMenu(parent,
                  labelpos = 'w',
                  label_text = 'Port Type:',
                  command=self._type_callback,
                  items=['analoginput', 'analogoutput', 'quantizedanalog', 'digitalmode'],
                  menubutton_width = 5
                  )
    self._description = Pmw.EntryField(parent, labelpos = 'w', label_text = 'Description:')
    self._regions = Pmw.EntryField(parent, labelpos = 'w', label_text = 'Regions:')
    self._abstol = Pmw.EntryField(parent, labelpos = 'w', label_text='Abstol:', validate={'validator':'real', 'min':0.0}, value=0.0)
    self._gaintol = Pmw.EntryField(parent, labelpos = 'w', label_text='Gaintol(%):', validate={'validator':'integer', 'min':0}, value=0)
    self._bitw = Pmw.EntryField(parent, labelpos = 'w', label_text='Bit width:', validate={'validator':'integer', 'min':0}, value=0)
    self._encode = Pmw.OptionMenu(parent,
                    labelpos = 'w',
                    label_text = 'Encode:',
                    items = self._encode_items,
                    menubutton_width = 5)
    self._prohibited = Pmw.EntryField(parent, labelpos = 'w', label_text = 'Prohibited\nCodes:')

    self._pinned = Tk.Checkbutton(parent, text='Pinned:', variable=self._is_pinned)
    self._defaultval = Pmw.EntryField(parent, labelpos = 'w', label_text = 'Default\nValue:')

    # buttons for editing
    self._btnbox = Pmw.ButtonBox(parent,
                  labelpos = 'n',
                  label_text = '',
                  orient = 'horizontal')
    self._btnadd = self._btnbox.add('Add/Edit', command = self._addport)
    self._btndel = self._btnbox.add('Delete', command = self._deleteport)
    self._btnclr = self._btnbox.add('Clear', command = self._clearport)
    self._btnbox.alignbuttons()

    self._name.grid(row=0, column=0, sticky='WENS')
    self._type.grid(row=0, column=1, sticky='WENS')
    self._description.grid(row=1, column=0, columnspan=2, sticky='WENS')
    self._regions.grid(row=2, column=0, columnspan=2, sticky='WENS')
    self._abstol.grid(row=3, column=0, sticky='WENS')
    self._gaintol.grid(row=3, column=1, sticky='WENS')
    self._bitw.grid(row=4, column=0, sticky='WENS')
    self._encode.grid(row=4, column=1, sticky='WENS')
    self._prohibited.grid(row=5, column=0, columnspan=2, sticky='WENS')
    self._pinned.grid(row=6, column=0, sticky='WENS')
    self._defaultval.grid(row=6, column=1, sticky='WENS')
    self._btnbox.grid(row=7, column=0, columnspan=2, sticky='WENS')
    labels = (self._name, self._type, self._description, self._regions, self._abstol, self._gaintol, self._bitw, self._encode, self._prohibited, self._pinned, self._defaultval)
    Pmw.alignlabels(labels)

  def _type_callback(self, tag):
    ptype = self._type.getvalue()
    if ptype.startswith('analog'):
      self._bitw.configure(entry_state='disabled')
      self._encode.setitems([''])
      self._encode.setvalue('')
      self._prohibited.configure(entry_state='disabled')
      self._regions.configure(entry_state='normal')
      if ptype == 'analogoutput':
        self._abstol.configure(entry_state='normal')
        self._gaintol.configure(entry_state='normal')
      else:
        self._abstol.configure(entry_state='disabled')
        self._gaintol.configure(entry_state='disabled')
    else:
      self._regions.configure(entry_state='disabled')
      self._abstol.configure(entry_state='disabled')
      self._gaintol.configure(entry_state='disabled')
      self._bitw.configure(entry_state='normal')
      self._encode.setitems(self._encode_items)
      self._prohibited.configure(entry_state='normal')


  def _name_callback(self, text):
    ''' callback routine of combobox '''
    if text in list(self._data.keys()):
      self._type.setvalue(self._data[text][0])
      self._description.setvalue(self._data[text][1])
      self._regions.setvalue(self._data[text][2])
      self._abstol.setvalue(self._data[text][3])
      self._gaintol.setvalue(self._data[text][4])
      self._bitw.setvalue(self._data[text][5])
      self._encode.setvalue(self._data[text][6])
      self._prohibited.setvalue(self._data[text][7])
      if self._data[text][8]:
        self._pinned.select()
      else:
        self._pinned.deselect()
      self._defaultval.setvalue(self._data[text][9])
    self._type_callback(self._data[text][1])
    self.update_display()

  def _addport(self):
    ''' add an item '''
    key = self._name.get()
    ptype = self._type.getcurselection()
    if len(key) == 0:
      self._msgbar.message('error', '[Error] Port name is empty.')
      return

    value = (
            self._type.getvalue(),
            self._description.getvalue(),
            self._regions.getvalue(),
            self._abstol.getvalue(),
            self._gaintol.getvalue(),
            self._bitw.getvalue(),
            self._encode.getvalue(),
            self._prohibited.getvalue(),
            self._is_pinned.get() == 1,
            self._defaultval.getvalue()
            )
    self._data.update({key:value})
    self.update_display()
    self._update_namelist()

  def _deleteport(self):
    key = self._name.get()
    if key in list(self._data.keys()):
      del self._data[key]
      self.update_display()
    else:
      self._msgbar.message('error', '[Error] Delete the port, %s, failed: No such port exists!!!' % key)

    self._update_namelist()

  def _clearport(self):
    self._data = {}
    self.update_display()

  def _update_namelist(self):
    self._name.setlist(sorted(self._data.keys()))

  def _createBalloon(self):
    self.balloon.bind(self._type, 'Select Port Type; Analog (control) input, (Pseudo) Analog output, Quantized (control) analog input, True digital input.')
    self.balloon.bind(self._description, 'Describe the function of the port.')
    self.balloon.bind(self._regions, 'Comma(,) separated list of analog signal range. For e.g, "0.0, 1.0, 2.0".')
    self.balloon.bind(self._abstol, 'Upper limit of residual error of the extracted model to the simulated response.')
    self.balloon.bind(self._gaintol, 'Upper limit of absolute value of relative gain error in percent.')
    self.balloon.bind(self._bitw, 'Bit width of either quantizedanalog or digitalmode input.')
    self.balloon.bind(self._encode, 'Encoding style of either quantizedanalog or digitalmode input.')
    self.balloon.bind(self._prohibited, 'Comma(,) separated list of prohibited code. The tool automatically counts for the prohibited code due to encoding style.')
    self.balloon.bind(self._pinned, 'The signal to this input port is pinned to the default value.')
    self.balloon.bind(self._defaultval, 'Default value when pinned property is True')
    self.balloon.bind(self._btnadd, 'Add or Edit a port')
    self.balloon.bind(self._btndel, 'Delete a port')
    self.balloon.bind(self._btnclr, 'Clear all port data')

#----------------------------------------------
class GridEdit2D:
  ''' Grid edit set of (variable, value) pair
      clabel: list of column labels (len=2)
      isFile: necessary for FileEntry
      self._data: stores the data
  '''
  def __init__(self, parent, messagebar, label_text, clabel, txt_hullheight= 200, isFile=False, balloon=None, default_items=[]):
    self._data = {}
    if default_items != []:
      for i in default_items:
        self._data[i] = ''
    self._isFile = isFile
    self._txt_hullheight = txt_hullheight
    self._parent = parent
    self._msgbar = messagebar
    self.balloon = Pmw.Balloon(self._parent)
    self.label_text = label_text
    self._clabel = clabel
    self._create_ScrolledText()
    self._create_editor()
    self._align_group()
    if balloon != None and len(balloon) == 3:
      self._createBalloon(balloon)
    self.update_display()

  def set(self, value):
    ''' import data '''
    self._data = value
    keys = sorted(self._data.keys())
    self._cbox.setlist(sorted(self._data.keys()))
    if len(keys)>0:
      self._cbox.selectitem(keys[0])
      self._cbox_callback(keys[0]) # the widget doesn't automatically call this

    self.update_display()

  def get(self):
    ''' export data '''
    return self._data

  def update_display(self):
    ''' update display '''
    self._change_sctxt_state('normal')
    self._txt.delete('0.0', 'end')
    self._txt.component('rowheader').delete('0.0', 'end')
    for k in sorted(self._data.keys()):
      self._txt.insert('end', self._data[k]+'\n')
      self._txt.component('rowheader').insert('end', k+'\n')
    self._change_sctxt_state('disabled')

  def change_state(self, state):
    ''' change state of widgets 
        need to disable these widgets depending on some value of another widget
    '''
    no_btn = self.btnbox.numbuttons()
    for i in range(no_btn):
      self.btnbox.button(i).configure(state=state)
    self._cbox.configure(entry_state=state)
    self._entry.change_state(state)

  def _align_group(self):
    self._cbox.grid(row=0, column=0, sticky='WEN')
    self._entry.grid(row=0, column=1, sticky='WEN')
    self.btnbox.grid(row=1, column=0, columnspan=3, sticky='WN')
    self._txt.grid(row=2, column=0, columnspan=3, sticky='WNES')

  def _create_ScrolledText(self):
    ''' create ScrolledText for displaying data '''
    self._txt = Pmw.ScrolledText(self._parent,
      labelpos = 'n',
      label_text = self.label_text, 
      columnheader = 1,
      rowheader = 1,
      rowcolumnheader = 1,
      borderframe = 1,
      usehullsize = 1,
      hull_width = 350,
      hull_height = self._txt_hullheight,
      text_wrap = 'none',
      Header_foreground = 'black',
      hscrollmode = 'none',
      vscrollmode = 'static',
      rowheader_width = 10,
      rowcolumnheader_width = 10,
      text_padx = 4,
      text_pady = 4,
      Header_padx = 4,
      rowheader_pady = 4)
    self._txt.component('rowcolumnheader').insert('end', self._clabel[0])
    self._txt.component('columnheader').insert('0.0', self._clabel[1])
    self._change_sctxt_state('disabled')

  def _create_editor(self):
    ''' create combobox and entry for add/edit, delete an item'''
    #group
    self._edit_grp = Pmw.Group(self._parent, 
               tag_pyclass = None)

    # combobox for variable
    self._cbox = Pmw.ComboBox(self._parent,
                label_text = '%s:' % self._clabel[0],
                labelpos='w',
                selectioncommand = self._cbox_callback,
                scrolledlist_items = sorted(self._data.keys()),
                dropdown = 1)

    # entry for value
    self._entry = FileEntry(self._parent,
                 messagebar = self._msgbar,
                 label_text = '%s:' % self._clabel[1],
                 file_ext  = [('SPICE netlist file', '*.sp'), ('SPECTRE netlist file', '*.scs'), ('All files', '*.*')],
                 isFile=self._isFile)

    # buttons for editing
    self.btnbox = Pmw.ButtonBox(self._parent,
                  labelpos = 'n',
                  label_text = '',
                  orient = 'horizontal')
    self.btnbox.add('Add/Edit', command = self._additem)
    self.btnbox.add('Delete', command = self._deleteitem)
    self.btnbox.add('Clear', command = self._clearitem)
    self.btnbox.alignbuttons()



  def _createBalloon(self, balloon):
    self.balloon.bind(self._cbox, balloon[0])
    self.balloon.bind(self._entry.get_entry(), balloon[1])
    self.balloon.bind(self._txt, balloon[2])

  def _cbox_callback(self, text):
    ''' callback routine of combobox '''
    if text in list(self._data.keys()):
      self._entry.set(self._data[text])

  def _change_sctxt_state(self, state):
    ''' change state of ScrolledText '''
    self._txt.configure(text_state=state, Header_state=state)

  def _additem(self):
    ''' add an item '''
    key = self._cbox.get()
    value = self._entry.get()
    if len(key) > 0:
      self._data.update({key:value})
      self.update_display()
      self._cbox.setlist(sorted(self._data.keys()))
    else:
      self._msgbar.message('error', '[Error] %s field is empty' %(self._clabel[0]))

  def _deleteitem(self):
    ''' delete an item '''
    key = self._cbox.get()
    if key in list(self._data.keys()):
      del self._data[key]
      self.update_display()
    else:
      self._msgbar.message('error', '[Error] Delete %s, %s, failed: No such %s name exists!!!' % (self._clabel[0], key, self._clabel[0]))

    self._cbox.setlist(sorted(self._data.keys()))

  def _clearitem(self):
    ''' clear GridEdit2D data '''
    self._data = {}
    self.update_display()

#----------------------------------------------
class ApplicationAbout:
  ''' for About dialog for all the tools 
      set app_name if necessary
  '''
  def __init__(self, parent, app_name):
    self._define_about(parent, app_name)

  def _define_about(self, parent, app_name):
    Pmw.aboutversion(str(__VERSION__))
    Pmw.aboutcopyright(__COPYRIGHT__)
    Pmw.aboutcontact(
      '''For information about this application, contact:
      email: {email}
      '''.format(email=__EMAIL__))
    self.about = Pmw.AboutDialog(parent, applicationname= 'mProbo%sConfiguration Editor' %app_name)
    self.about.withdraw()

  def show(self):
    self.about.show()

#----------------------------------------------
class Startup:
  ''' Start the top-level application '''
  def __init__(self, parent):
    self._parent = parent
    self.about = ApplicationAbout(parent, ' ')
    self.buttonBox = Pmw.ButtonBox(parent,
      labelpos = 'nw',
      label_text = 'mProbo Configuration Editor',
      orient = 'horizontal',
      frame_borderwidth = 2,
      frame_relief = 'groove')
    packWidget(self.buttonBox, side='top')
    self.buttonBox.add('Test', command = self._start_testcfg)
    self.buttonBox.add('Simulator', command = self._start_simcfg)
    #self.buttonBox.add('Run', command = self._run)
    self.buttonBox.add('About', command = self.about.show)
    self.buttonBox.alignbuttons()

    self.buttonBox.setdefault('About')
    parent.bind('<Return>', self._processReturnKey)
    parent.focus_set()

  def _processReturnKey(self, event):
    self.buttonBox.invoke()

  def _start_testcfg(self):
    print('Starting Test Configuration Editor')
    TestConfigurationEditor(self._parent)

  def _start_simcfg(self):
    print('Starting Simulator Configuration Editor')
    SimulatorConfigurationEditor(self._parent)


#----------------------------------------------
class TestConfigurationEditor:
  ''' Top-level class of test configuration editor
    TODO: _copytest, _renametest are not complete yet
  '''
  def __init__(self, parent):
    self._title = 'mProbo - Test Configuration Editor'
    self._top = Pmw.MegaToplevel(parent).interior()
    set_position(self._top)

    self._set_title(self._title)

    self.about = ApplicationAbout(self._top, ' - Test ')
    self.balloon = Pmw.Balloon(self._top)
    self.menuBar = Pmw.MenuBar(self._top,
      hull_relief = 'raised',
      hull_borderwidth = 2,
      balloon = self.balloon)
    self.menuBar.pack(fill='x')

    self._sectionobj = {}

    self._createMenuBar()
    self._createBody(self._top)
    self._createStatusbar(self._top)
    #self._nb.setnaturalsize()

  def _createMenuBar(self):
    self.menuBar.addmenu('File', 'Load/Save file or exit')
    self.menuBar.addmenuitem('File', 'command', 'Open a configuration file',
                        command = self.askOpen,
                        label = 'Open')
    self.menuBar.addmenuitem('File', 'command', 'Save a configuration file',
                        command = self.askSave,
                        label = 'Save as')
    self.menuBar.addmenuitem('File', 'separator')
    self.menuBar.addmenuitem('File', 'command', 'Exit the editor',
                        command = self._top.destroy,
                        label = 'Exit')
    self.menuBar.addmenu('Help', 'User manuals', side = 'right')
    self.menuBar.addmenuitem('Help', 'command', 'Open user manual',
                        label = 'Manual')
    self.menuBar.addmenuitem('Help', 'command', 'About the tool',
                        command = self.about.show,
                        label = 'About')

  def _set_title(self, title):
    self._top.title(title)

  def _createBalloon(self):
    pass

  def _createBody(self, parent):
    self.grp = Pmw.Group(parent, tag_text='Test Edit')
    packWidget(self.grp, side='top')
    self._nb = Pmw.NoteBook(self.grp.interior(),
               tabpos = None,
               hull_width = 1024,
               hull_height = 700)

    self._btnbox = Pmw.ButtonBox(self.grp.interior(), orient='horizontal')
    self._btnbox.add('Insert Test', command = self._addtest)
    self._btnbox.add('Delete Test', command = self._deletetest)
    self._btnbox.add('Copy Test', command = self._copytest)
    self._btnbox.add('Rename Test', command = self._renametest)
    self._btnbox.alignbuttons()

    self._optmenu = Pmw.OptionMenu(self.grp.interior(),
                   menubutton_width = 10,
                   command = self._nb.selectpage)

    self._btnbox.grid(row=0, column=1, sticky='WENS', columnspan=2)
    self._optmenu.grid(row=0, column=0, sticky='EWNS')
    self._nb.grid(row=1, column=0, columnspan=2, sticky='WENS')

    page = self._nb.add('tmp')
    self._nb.delete('tmp')

  def _get_testnames(self):
    return self._nb.pagenames()

  def _get_len_tests(self):
    return len(self._get_testnames())

  def _get_first_missing_test_index(self):
    regular_testname = [k for k in self._get_testnames() if re.match('test\d*$', k)]
    indices = sorted([int(k.strip('test')) for k in regular_testname])
    missing_indices = list(set(range(1,max(indices)+1))-set(indices))
    if missing_indices == []:
      return None
    else:
      return missing_indices[0]

  def _get_previous_testname(self, testname):
    pass
    tests = self._get_testnames()
    before = self._nb.index(testname) - 1
    if before >= 0:
      return tests[before]
    else:
      return None

  def _addtest(self):
    ''' add a test '''
    no_test = self._get_len_tests()
    if (no_test==0):
      testname = 'test1'
    else:
      missed = self._get_first_missing_test_index()
      idx = missed if missed else no_test + 1
      testname = 'test'+str(idx)
    return self._createtest(testname)
  
  def _createtest(self, testname):
    setattr(self, testname, self._nb.add(testname))
    self._nb.selectpage(testname)
    self._msgbar.message('fine', 'The test, "%s", is created' % testname)
    self._update_optmenu()

    self._sectionobj[testname] = TestConfigurationSection(getattr(self, testname), testname, self._msgbar)

    return testname

  def _deletetest(self):
    ''' delete a test '''
    if len(self._nb.pagenames()) == 0:
      self._msgbar.message('warn', 'Delete a page fails. No test exists')
      self._nb.bell()
      return None
    testname = self._nb.getcurselection()
    self._cleartest(testname)
    self._msgbar.message('fine', 'The test, "%s", is deleted' % testname)
    return testname

  def _cleartest(self, testname):
    self._nb.delete(testname)       # delete a test
    del self._sectionobj[testname]  # delete the corresponding test section object
    self._update_optmenu()

  def _copytest(self):
    ''' it's not simply done by doing deepcopy '''
    src = self._nb.getcurselection()
    if src != None:
      testname = self._addtest()
      data = self._sectionobj[src].get()
      self._sectionobj[testname].set(data)
      self._msgbar.message('fine', 'The test, "%s", is copied to %s' % (src, testname))
      return testname
    else:
      self._msgbar.message('error', 'Copying a test failed. No test exists !!!') 

  def _renametest(self):
    self._msgbar.message('error', 'Sorry. Renaming the test is not implemented yet.') 

  def _update_optmenu(self):
    self._optmenu.setvalue(self._nb.getcurselection())
    self._optmenu.setitems(self._nb.pagenames())

  def _createStatusbar(self, parent):
    self._msgbar = Pmw.MessageBar(parent,
      entry_relief='groove',
      messagetypes = {'warn': (0, 5, 0, 0),
                      'error': (0, 5, 0, 0),
                      'fine': (0, 5, 0, 0)},
      entry_width = 60,
      labelpos = 'w',
      label_text = 'Status:')
    self._msgbar.pack(side='bottom', fill='both', expand=1)

  def askOpen(self):
    filename = self._browseFilename()
    if check_file(filename):
      self._set_title(self._title+' - '+filename)
      self._deleteAlltests() # delete the existing tests first if any
      test_cfg = TestConfig(filename, bypass=True)
      for t in test_cfg.get_all_testnames():
        self._loadTest(t, test_cfg.get_raw_test(t))

  def _loadTest(self, t, test_cfg):
    self._createtest(t) 
    self._sectionobj[t].set(test_cfg)

  def _deleteAlltests(self):
    for t in self._nb.pagenames():
      self._cleartest(t)

  def askSave(self):
    filename = self._browsesaveFilename()
    if len(filename) > 0:
      config = ConfigObj()
      for t in self._get_testnames(): # aggregate tests
        config[t] = self._sectionobj[t].get()
      config.write(open(filename, 'w'))
      self._set_title(self._title+' - '+filename)

  def _browseFilename(self):
    return tkinter.filedialog.askopenfilename(filetypes=[('mchecker configuration file', '*.cfg'),('All files', '*.*')], parent=self._top)

  def _browsesaveFilename(self):
    return tkinter.filedialog.asksaveasfilename(filetypes=[('mchecker configuration file', '*.cfg'),('All files', '*.*')], parent=self._top)


#----------------------------------------------
class TestConfigurationSection:
  def __init__(self, parent, name, messagebar):
    self._nb = Pmw.NoteBook(parent, tabpos='n',
               hull_width = 1000,
               hull_height = 600)
    self._tab_general = self._nb.add('General')
    self._tab_testbench = self._nb.add('testbench')
    self._nb.grid(row=0, column=0)

    dummy_grp1 = Tk.Frame(self._tab_general, borderwidth=0)
    dummy_grp2 = Tk.Frame(self._tab_general, borderwidth=0)

    self._header = TestHeaderTab(dummy_grp1, messagebar)
    self._port = TestPortTab(dummy_grp1, messagebar)
    self._regression = TestRegressionTab(dummy_grp2, messagebar)
    self._testbench = TestTestbenchTab(self._tab_testbench, messagebar)

    self._header.get_group_header().grid(row=0, column=0, sticky='WN')
    self._header.get_group_simtime().grid(row=1, column=0, sticky='WN')
    self._port.get_group().grid(row=2, column=0, sticky='WN')
    reg_grp = self._regression.get_group()
    reg_grp[0].grid(row=0, column=0)
    reg_grp[1].grid(row=1, column=0)
    reg_grp[2].grid(row=2, column=0)

    dummy_grp1.grid(row=0, column=0, sticky='WENS')
    dummy_grp2.grid(row=0, column=1, sticky='WENS')

  def get(self):
    return dict(list(self._header.get().items()) + list({'port':self._port.get()}.items()) + list({'regression':self._regression.get()}.items()) + list({'testbench':self._testbench.get()}.items()))

  def set(self, value):
    self._header.set(
      dict([ (k, value[k]) for k in ['description', 'dut', 'simulation'] ])
    )
    self._port.set(value['port'])
    self._regression.set(value['regression'])
    self._testbench.set(value['testbench'])

#----------------------------------------------
class TestHeaderTab:
  def __init__(self, parent, messagebar):
    self._parent = parent
    self._msgbar = messagebar
    self.balloon = Pmw.Balloon(parent)
    self._createBody(parent)
    self._createBalloon()

  def get(self):
    return {
      'dut': self._dut.getvalue(),
      'description': unicode2ascii(self._description).rstrip('\n'),
      'simulation': {
                      'timeunit': self._timeunit.getvalue(),
                      'timeprec': self._timeprec.getvalue(),
                      'time': self._simtime.getvalue()
                    }
    }

  def set(self, value):
    self._dut.setentry(value['dut'])
    self._description.insert('1.0', value['description'].lstrip('\n'))
    self._timeunit.setentry(value['simulation']['timeunit'])
    self._timeprec.setentry(value['simulation']['timeprec'])
    self._simtime.setentry(value['simulation']['time'])

  def get_group_header(self):
    return self._grp1

  def get_group_simtime(self):
    return self._grp2

  def _createBody(self, parent):
    self._grp1 = Pmw.Group(parent, tag_text='Test Header', hull_relief = 'groove')
    self._grp2 = Pmw.Group(parent, tag_text='Simulation Time', hull_relief = 'groove')
    self._grp1.grid(row=0, column=0, sticky='WENS')
    self._grp2.grid(row=1, column=0, sticky='WENS')

    # group 1: test header
    ldut = Tk.Label(self._grp1.interior(), text='Device-under-Test')
    self._dut = Pmw.EntryField(self._grp1.interior(),
                      command = self._dut_callback)

    self._description = LabeledText(self._grp1.interior(), label_text='Test\ndescription:', height=8, width=50)
    ldut.grid(row=0, column=0, sticky='WENS')
    self._dut.grid(row=0, column=1, sticky='WENS')
    self._description.grid(row=1, column=0, sticky='WENS')

    # group 2: simulation time
    self._timeunit = Pmw.EntryField(self._grp2.interior(), labelpos = 'w', label_text = 'Simulation timeunit')
    self._timeprec = Pmw.EntryField(self._grp2.interior(), labelpos = 'w', label_text = 'Simulation timeprecision')
    self._simtime = Pmw.EntryField(self._grp2.interior(), labelpos = 'w', label_text = 'Transient time')
    self._timeunit.grid(row=0, column=0, sticky='W')
    self._timeprec.grid(row=1, column=0, sticky='W')
    self._simtime.grid(row=2, column=0, sticky='W')
    labels = (self._timeunit, self._timeprec, self._simtime)
    Pmw.alignlabels(labels)

  def _createBalloon(self):
    self.balloon.bind(self._dut, 'Module(Subcircuit) name of device-under-test')
    self.balloon.bind(self._description.get_text(), 'Description of a test')
    self.balloon.bind(self._timeunit, 'Timeunit in Verilog format. For e.g., 1ps')
    self.balloon.bind(self._timeprec, 'Timeunit in Verilog format. For e.g., 1ps')
    self.balloon.bind(self._simtime, 'Simulation time. For e.g., 11.5us')

  def _dut_callback(self):
    pass

#----------------------------------------------
class TestRegressionTab:
  def __init__(self, parent, messagebar):
    self._parent = parent
    self._msgbar = messagebar
    self.balloon = Pmw.Balloon(parent)
    self._createBody(self._parent)
    self._createBalloon()

  def get(self):
    return {
      'min_sample': self._min_sample.getvalue(),
      'no_of_analog_grid': self._no_grid.getvalue(),
      'order': self._order.getvalue(),
      'input_sensitivity_threshold': self._sensitivity.getvalue(),
      'en_interact': self._en_interact.get() == 1,
      'do_not_regress': self._dont_regression.get(),
      'user_model': self._user_model.get()
    }

  def set(self, v):
    self._min_sample.setvalue(v['min_sample'])
    self._no_grid.setvalue(v['no_of_analog_grid'])
    self._order.setvalue(v['order'])
    self._sensitivity.setvalue(v['input_sensitivity_threshold'])
    if v['en_interact']:
      self._interact.select()
    else:
      self._interact.deselect()

    self._dont_regression.set(v['do_not_regress'])
    self._user_model.set(v['user_model'])

  def get_group(self):
    return self._grp1, self._grp2, self._grp3

  def _createBody(self, parent):
    self._grp1 = Pmw.Group(parent, tag_text='Regression Option')
    self._grp2 = Pmw.Group(parent, tag_text='Exlucde Predictors')
    self._grp3 = Pmw.Group(parent, tag_text='User model')

    # group 1:
    self._en_interact = Tk.IntVar()
    self._min_sample = LabeledIntCounter(self._grp1.interior(), {'min': 2}, entryfield_value=2, label_text='Minimum # of test vectors:', labelpos='w')
    self._no_grid = LabeledIntCounter(self._grp1.interior(), {'min': 2}, entryfield_value=2, label_text = '# of analog grid:', labelpos='w')
    self._order = LabeledIntCounter(self._grp1.interior(), {'min': 1}, entryfield_value=1, label_text = 'Polynomial order:', labelpos='w')
    self._sensitivity = LabeledIntCounter(self._grp1.interior(), {'min': 0, 'max':100}, entryfield_value=1, label_text='Sensitivity threshold in [%]:', labelpos='w')
    self._interact = Tk.Checkbutton(self._grp1.interior(), text='Consider 1st order interaction terms:', variable=self._en_interact)

    self._min_sample.grid(row=0, column=0, sticky='W')
    self._no_grid.grid(row=0, column=1, sticky='W')
    self._order.grid(row=1, column=0, sticky='W')
    self._sensitivity.grid(row=1, column=1, sticky='W')
    self._interact.grid(row=2, column=0, columnspan=2, sticky='W')
    labels = (self._min_sample, self._no_grid, self._order, self._sensitivity)
    Pmw.alignlabels(labels)


    # group 2:
    self._dont_regression = GridEdit2D(self._grp2.interior(), self._msgbar, 'Excluded predictors for each repsonse', ['Response', 'Predictor'], txt_hullheight=100, isFile=False, balloon = ['Output port name', 'Comma(,)-separated input port names', 'List predictor variables which should not be presented in the linear model for each response. Leave this blank if not used'])

    # group 3:
    self._user_model = GridEdit2D(self._grp3.interior(), self._msgbar, 'Use user-defined linear model for responses listed', ['Response', 'Model'], txt_hullheight=100, isFile=False, balloon = ["Output port name", "Model expression as a function of input ports in R. For e.g., in1 + in2 + in1:in2 + I('in1^2')", "List user-defined linear model for each response. Leave this blank if not used"])

    self._dont_regression.update_display()
    self._user_model.update_display()

  def _createBalloon(self):
    self.balloon.bind(self._min_sample, 'User defined minimum number of test vectors. Larger number will be selected between this value and the number of test vectors generated by this tool.')
    self.balloon.bind(self._no_grid, 'Number of discretizations for each analog input.')
    self.balloon.bind(self._order, 'Polynomial order in linear models.')
    self.balloon.bind(self._sensitivity, 'Input sensitivity threshold in [%] for suggesting models.')
    self.balloon.bind(self._interact, 'Check if the first-order interaction terms between inputs need to be included.')

  def _dut_callback(self):
    pass

#----------------------------------------------
class TestPortTab:
  def __init__(self, parent, messagebar):
    self._parent = parent
    self._msgbar = messagebar
    self.balloon = Pmw.Balloon(parent)
    self._group = Pmw.Group(self._parent, tag_text = 'Port Editor')
    self._createBody()

  def set(self, value):
    self._port.set(value)

  def get(self):
    return self._port.get()

  def get_group(self):
    return self._group

  def _createBody(self):
    self._port = PortEditor(self._group.interior(), self._msgbar)


#----------------------------------------------
class TestTestbenchTab:
  def __init__(self, parent, messagebar):
    self._parent = parent
    self._msgbar = messagebar
    self.balloon = Pmw.Balloon(parent)
    self._createBody(self._parent)
    self._createBalloon()

  def get(self):
    initgolden = unicode2ascii(self._initgolden).split('\n')
    golden = {}
    for x in [x for x in initgolden if x != '']:
      field = x.split('=')
      golden[field[0]] = field[1]
    initrevised = unicode2ascii(self._initrevised).split('\n')
    revised = {}
    for x in [x for x in initrevised if x != '']:
      field = x.split('=')
      revised[field[0]] = field[1]

    out = {}
    out['temperature'] = self._temperature.getvalue()
    out['pre_module_declaration'] = unicode2ascii(self._premodule).rstrip('\n')
    out['tb_code'] = unicode2ascii(self._customcode).rstrip('\n')
    out['initial_condition']={'golden':golden, 'revised':revised}
    out['wire'] = dict([ (k, v.split(',')) for k,v in list(self._wire.get().items()) if v != ''])
    out['post-processor'] = {
                            'script_files': [x for x in self._scriptfile.get().split(',') if x!=''],
                            'command': self._pp_cmd.getvalue()
                            }

    return out


  def set(self, value):
    initgolden = ['%s=%s' %(k,v) for k,v in list(value['initial_condition']['golden'].items())]
    initrevised = ['%s=%s' %(k,v) for k,v in list(value['initial_condition']['revised'].items())]
    _wire = dict([ (k, ', '.join(v)) for k,v in list(value['wire'].items())])

    self._temperature.setvalue(value['temperature'])
    self._premodule.insert('1.0', value['pre_module_declaration'].lstrip('\n'))
    self._customcode.insert('1.0', value['tb_code'].lstrip('\n'))
    self._initgolden.insert('1.0', '\n'.join(initgolden))
    self._initrevised.insert('1.0', '\n'.join(initgolden))
    self._wire.set(_wire)
    self._scriptfile.set(', '.join(value['post-processor']['script_files']))
    self._pp_cmd.setvalue(value['post-processor']['command'])

  def _createBody(self, parent):
    # group 1
    frame1 = Tk.Frame(parent, borderwidth=0)
    self._premodule = LabeledText(frame1, label_text='Pre-module\ndeclaration:', height=6, width=60)
    self._customcode = LabeledText(frame1, label_text='Custom code:', height=20, width=60)
    #self._temperature = Pmw.EntryField(frame1, labelpos = 'w', label_text = 'Temperature:')
    self._temp = Tk.Label(frame1, text='Temperature:')
    self._temperature = Pmw.EntryField(frame1)
    self._initgolden = LabeledText(frame1, label_text='Initial condition\nof Golden model:', height=2, width=60)
    self._initrevised = LabeledText(frame1, label_text='Initial condition\nof Revised model:', height=2, width=60)
    #self._temperature.grid(row=0, column=0, columnspan=2, sticky='W')
    self._temp.grid(row=0, column=0, sticky='WENS')
    self._temperature.grid(row=0, column=1, sticky='WENS')
    self._premodule.grid(row=1, column=0, sticky='W')
    self._customcode.grid(row=2, column=0, sticky='W')
    self._initgolden.grid(row=3, column=0, sticky='W')
    self._initrevised.grid(row=4, column=0, sticky='W')

    # group 2
    #frame2 = Tk.Frame(parent, borderwidth=0)
    frame2 = Pmw.Group(parent, tag_text = 'Wire Declaration', hull_relief = 'groove')
    self._wire = GridEdit2D(frame2.interior(), self._msgbar, 'Wire decalaration', ['Type', 'Name'], txt_hullheight=100, isFile=False, balloon = ['Wire datatype', 'Comma(,)-separated list of wire names', 'Declaring wires in the testbench. The default datatype supported is "ams_electrical", "ams_wreal", "ams_ground", and "logic"'], default_items=['ams_electrical', 'ams_wreal', 'ams_ground', 'logic'])

    # group 3
    frame3 = Pmw.Group(parent, tag_text = 'Post-Processing', hull_relief = 'groove')
    self._scriptfile = FileEntry(frame3.interior(),
                        messagebar = self._msgbar,
                        label_text = 'Script files:',
                        file_ext  = [('Python file', '*.py'), ('MATLAB file', '*.m'), ('All files', '*.*')],
                        isFile=True,
                        appendmode=True)
    self._pp_cmd = Pmw.EntryField(frame3.interior(), labelpos = 'w', label_text = 'Post-processing\ncommand:')
    self._scriptfile.grid(row=0, column=0, sticky='WE')
    self._pp_cmd.grid(row=1, column=0, sticky='WE')

    frame1.grid(row=0, column=0, rowspan=2, sticky='WN')
    frame2.grid(row=0, column=1, sticky='WN')
    frame3.grid(row=1, column=1, sticky='WN')
  
  def _createBalloon(self):
    self.balloon.bind(self._premodule.get_text(), 'Verilog code before module declaration of a testbench')
    self.balloon.bind(self._customcode.get_text(), 'User Verilog code in a test bench')
    self.balloon.bind(self._temperature, 'Simulation temperature')
    self.balloon.bind(self._initgolden.get_text(), 'Initial condition assignment of golden model. Multilines are for multiple assignments. This is useful for checking a system with states.')
    self.balloon.bind(self._initrevised.get_text(), 'Initial condition assignment of revised model. Multilines are for multiple assignments. This is useful for checking a system with states.')
    self.balloon.bind(self._scriptfile.get_entry(), 'Comma(,)-separated list of post-processing scripts')
    self.balloon.bind(self._pp_cmd, 'Shell command to run post-processing scripts.')

#----------------------------------------------
class SimulatorConfigurationEditor:
  ''' Top-level class of simulator configuration editor
  '''
  def __init__(self, parent):
    self._title = 'mProbo - Simulator Configuration Editor'
    self._top = Pmw.MegaToplevel(parent).interior()
    set_position(self._top)

    self._set_title(self._title)

    self.about = ApplicationAbout(self._top, ' - Simulator ')
    self.balloon = Pmw.Balloon(self._top)
    self.menuBar = Pmw.MenuBar(self._top,
      hull_relief = 'raised',
      hull_borderwidth = 2,
      balloon = self.balloon)
    self.menuBar.pack(fill='x')

    self._createMenuBar()
    self._createBody(self._top)
    self._createStatusbar(self._top)
    self.golden = SimulatorConfigSection(self._nbpg1, self._msgbar)
    self.revised = SimulatorConfigSection(self._nbpg2, self._msgbar)
    self._nb.setnaturalsize()
    self._createBalloon()

  def _createMenuBar(self):
    self.menuBar.addmenu('File', 'Load/Save file or exit')
    self.menuBar.addmenuitem('File', 'command', 'Open a configuration file',
                        command = self.askOpen,
                        label = 'Open')
    self.menuBar.addmenuitem('File', 'command', 'Save a configuration file',
                        command = self.askSave,
                        label = 'Save as')
    self.menuBar.addmenuitem('File', 'separator')
    self.menuBar.addmenuitem('File', 'command', 'Exit the editor',
                        command = self._top.destroy,
                        label = 'Exit')
    self.menuBar.addmenu('Edit', 'Copy/Swap between models')
    self.menuBar.addmenuitem('Edit', 'command', 'Copy golden model to revised model',
                        command = self.copy_golden_to_revised,
                        label = 'Golden->Revised')
    self.menuBar.addmenuitem('Edit', 'command', 'Copy revised model to golden model',
                        command = self.copy_revised_to_golden,
                        label = 'Revised->Golden')
    self.menuBar.addmenuitem('Edit', 'command', 'Swap golden/revised models',
                        command = self.swap_model_cfg,
                        label = 'Golden<->Revised')
    self.menuBar.addmenu('Help', 'User manuals', side = 'right')
    self.menuBar.addmenuitem('Help', 'command', 'Open user manual',
                        label = 'Manual')
    self.menuBar.addmenuitem('Help', 'command', 'About the tool',
                        command = self.about.show,
                        label = 'About')

  def _set_title(self, title):
    self._top.title(title)

  def copy_golden_to_revised(self):
    g = copy.deepcopy(self.golden.get())
    self.revised.set(g)

  def copy_revised_to_golden(self):
    r = copy.deepcopy(self.revised.get())
    self.golden.set(r)

  def swap_model_cfg(self):
    g = copy.deepcopy(self.golden.get())
    r = copy.deepcopy(self.revised.get())
    self.golden.set(r)
    self.revised.set(g)

  def _createBalloon(self):
    pass
    
  def _createBody(self, parent):
    self._nb = Pmw.NoteBook(parent)
    packWidget(self._nb, side='top')
    self._nbpg1 = self._nb.add('GOLDEN')
    self._nbpg2 = self._nb.add('REVISED')

  def _createStatusbar(self, parent):
    self._msgbar = Pmw.MessageBar(parent,
      entry_relief='groove',
      messagetypes = {'warn': (0, 5, 0, 0),
                      'error': (0, 5, 0, 0),
                      'fine': (0, 5, 0, 0)},
      entry_width = 60,
      labelpos = 'w',
      label_text = 'Status:')
    self._msgbar.pack(fill='both', expand=1)

  def askOpen(self):
    filename = self._browseFilename()
    if check_file(filename):
      sim_cfg = SimulatorConfig(filename)
      g = sim_cfg.get_golden().get()
      r = sim_cfg.get_revised().get()
      self.golden.set(g)
      self.revised.set(r)
      self._set_title(self._title+' - '+filename)

  def askSave(self):
    filename = self._browsesaveFilename()
    if len(filename) > 0:
      g = self.golden.get()
      r = self.revised.get()
      out = {'golden':g, 'revised':r}
      config = ConfigObj()
      config['golden'] = g
      config['revised'] = r
      config.write(open(filename, 'w'))
      self._set_title(self._title+' - '+filename)

  def _browseFilename(self):
    return tkinter.filedialog.askopenfilename(filetypes=[('mchecker configuration file', '*.cfg'),('All files', '*.*')], parent=self._top)

  def _browsesaveFilename(self):
    return tkinter.filedialog.asksaveasfilename(filetypes=[('mchecker configuration file', '*.cfg'),('All files', '*.*')], parent=self._top)


#----------------------------------------------
class SimulatorConfigSection:
  ''' Simulator configuration editor class of either golden or revised model
  '''

  def __init__(self, parent, statusbar):
    self._parent = parent
    self._msgbar = statusbar
    self.balloon = Pmw.Balloon(parent)

    self._create_checker_option()
    self._create_ncams_group()
    self._create_simulator_flag_group()
    self._align_to_grid()
    self._createBalloon()
    self.cfg_map = {
      'model': self.mdl_opt,
      'simulator': self.sim_opt,
      'simulator_option': self.sim_flag_opt,
      'hdl_files': self.sim_hdl,
      'hdl_include_files': self.sim_hdl_include,
      'sweep_file': (self.sweepstatus, self.sim_sweep),
      'ams_control_file': self.ncams_control_file_entry,
      'spice_lib': self.ncams_modellib_file_entry,
      'circuit': self.circuit,
      'default_ams_connrules': self._amsconnrules
    }

  def _createBalloon(self):
    self.balloon.bind(self.mdl_ams, 'Model is Circuit and/or Verilog-AMS')
    self.balloon.bind(self.mdl_vlog, 'Model is (System)Verilog')
    self.balloon.bind(self.sim_opt, 'Choose Simulator. For ams/circuit, only "ncsim" is supported')
    self.balloon.bind(self.sim_hdl.get_text(), 'List HDL files separated by comman(,).')
    self.balloon.bind(self.sim_hdl_include.get_text(), 'List HDL files being included by "`include" directive separated by comman(,).')
    self.balloon.bind(self.sim_flag_opt.get_text(), 'Write simulator-specific flags.')
    self.balloon.bind(self.sim_sweep, 'Delete all simulation files/temperary files after running the checker.')
    self.balloon.bind(self.ncams_control_file_entry.get_entry(), 'Select a circuit control file.')
    self.balloon.bind(self.ncams_modellib_file_entry.get_entry(), 'Select a Spice or Spectre model library file for circuit simulation.')
    self.balloon.bind(self._amsconnrules, 'AMS connection rules. You could leave this blank and add the option in "Simulator compile option" field.')

  def set(self, v):
    self.cfg_map['model'].setvalue(v['model'])
    self.cfg_map['simulator'].setvalue(v['simulator'])
    self.cfg_map['simulator_option'].delete('1.0', 'end')
    self.cfg_map['simulator_option'].insert('1.0', v['simulator_option'])
    self.cfg_map['hdl_files'].delete('1.0', 'end')
    self.cfg_map['hdl_files'].insert('1.0', ', '.join(v['hdl_files']))
    self.cfg_map['hdl_include_files'].delete('1.0', 'end')
    self.cfg_map['hdl_include_files'].insert('1.0', ', '.join(v['hdl_include_files']))
    if v['sweep_file']:
      self.cfg_map['sweep_file'][1].select()
    else:
      self.cfg_map['sweep_file'][1].deselect()

    if self._ncams_callback():
      self.cfg_map['ams_control_file'].set(v['ams_control_file'])
      self.cfg_map['spice_lib'].set(v['spice_lib'])
      self.cfg_map['circuit'].set(v['circuit'])
      self.cfg_map['default_ams_connrules'].setvalue(v['default_ams_connrules'])
    else:
      self.cfg_map['ams_control_file'].set('')
      self.cfg_map['spice_lib'].set('')
      self.cfg_map['circuit'].set({})


    self._ncams_callback()

  def get(self):
    out = {}
    out['model'] = self.cfg_map['model'].getvalue()
    out['simulator'] = self.cfg_map['simulator'].getvalue()
    out['simulator_option'] = self.cfg_map['simulator_option'].get('1.0', 'end').encode('ascii','ignore').strip('\n')
    _hdl = self.cfg_map['hdl_files'].get('1.0', 'end').encode('ascii','ignore').strip('\n').split(',')
    _hdl_include = self.cfg_map['hdl_include_files'].get('1.0', 'end').encode('ascii','ignore').strip('\n').split(',')
    out['hdl_files'] = [s.lstrip().rstrip() for s in _hdl] if _hdl != [''] else []
    out['hdl_include_files'] = [s.lstrip().rstrip() for s in _hdl] if _hdl_include != [''] else []
    out['sweep_file'] = self.cfg_map['sweep_file'][0].get() == 1
    if self._ncams_callback():
      out['ams_control_file'] = self.cfg_map['ams_control_file'].get()
      out['spice_lib'] = self.cfg_map['spice_lib'].get()
      out['circuit'] = self.cfg_map['circuit'].get()
      out['default_ams_connrules'] = self.cfg_map['default_ams_connrules'].getvalue()
    return out
  
  def _create_checker_option(self):
    self.checker_option = Pmw.Group(self._parent, 
      tag_text = 'Checker Option',
      hull_relief = 'groove')

    self.mdl_opt = Pmw.RadioSelect(self.checker_option.interior(),
      buttontype = 'radiobutton',
      orient = 'horizontal',
      command = self._mdl_opt_callback,
      labelpos = 'w',
      label_text = 'Model:',
      hull_borderwidth = 0,
      hull_relief = 'sunken')
    self.mdl_ams  = self.mdl_opt.add('ams', text='ams/circuit')
    self.mdl_vlog = self.mdl_opt.add('verilog', text='(system)Verilog')

    self.sim_opt = Pmw.OptionMenu(self.checker_option.interior(),
      labelpos = 'w',
      label_text = 'Simulator:',
      command = self._sim_opt_callback,
      items = ['ncsim', 'vcs', 'modelsim'],
      menubutton_width = 10)

    self.sweepstatus = Tk.IntVar()
    self.sim_sweep = Tk.Checkbutton(self.checker_option.interior(), text='Sweep simulation file', variable=self.sweepstatus)


    self.mdl_opt.grid(row=0, column=0, sticky='WE', pady=2)
    self.sim_opt.grid(row=1, column=0, sticky='W', pady=2)
    self.sim_sweep.grid(row=2, column=0, sticky='W', pady=2)

    self.mdl_opt.invoke('ams')
    self.sim_opt.invoke('ncsim')

  def _create_ncams_group(self):
    self.ncams_group = Pmw.Group(self._parent, tag_text = 'NCSIM-AMS Option')
    self.ncams_control_file_entry = FileEntry(self.ncams_group.interior(),
      messagebar = self._msgbar,
      label_text = 'AMS control file:',
      file_ext  = [('NCVLOG-AMS circuit control file', '*.scs'), ('All files', '*.*')],
      isFile=True)
    self.ncams_modellib_file_entry = FileEntry(self.ncams_group.interior(),
      messagebar = self._msgbar,
      label_text = 'Spice/Spectre model library:',
      file_ext  = [('SPICE model library file', '*.sp'), ('SPECTRE model library file', '*.scs'), ('All files', '*.*')],
      isFile=True)
    self._amsconnrules = Pmw.EntryField(self.ncams_group.interior(), labelpos = 'w', label_text = 'AMS Connect rules:')
    self.ncams_control_file_entry.grid_entry(row=0, column=0, sticky='WE')
    self.ncams_control_file_entry.grid_button(row=0, column=1, sticky='E')
    self.ncams_modellib_file_entry.grid_entry(row=1, column=0, sticky='WE')
    self.ncams_modellib_file_entry.grid_button(row=1, column=1, sticky='E')
    self._amsconnrules.grid(row=2, column=0, columnspan=2, sticky='WE')
    self.circuit_subgrp = Pmw.Group(self.ncams_group.interior(), tag_text = 'Import Circuit Netlist', hull_relief='flat')
    self.circuit_subgrp.grid(row=3, column=0, columnspan=2, sticky='NW')
    self.circuit = GridEdit2D(self.circuit_subgrp.interior(), self._msgbar, '', ['Subcircuit', 'Netlist'], isFile=True, balloon=['Subcircuit name', 'Netlist file name', 'List of subcircuits and where they are.'])
    self.circuit.update_display()

  def _create_simulator_flag_group(self):
    self.sim_flag_group = Pmw.Group(self._parent, tag_text = 'Simulator Flag/HDL files')

    self.sim_flag_opt = LabeledText(self.sim_flag_group.interior(), label_text='Simulator\ncompile option', height=10, width=60)
    self.sim_hdl = LabeledText(self.sim_flag_group.interior(), label_text='HDL files', height=3, width=60)
    self.sim_hdl_include = LabeledText(self.sim_flag_group.interior(), label_text='HDL include files', height=3, width=60)

    self.sim_flag_opt.grid(row=0, column=0, sticky='W')
    self.sim_hdl.grid(row=1, column=0, sticky='W')
    self.sim_hdl_include.grid(row=2, column=0, sticky='W')
  
  def _align_to_grid(self):
    self.checker_option.grid(row=0, column=0, sticky='NWES')
    self.sim_flag_group.grid(row=1, column=0, sticky='WES')
    self.ncams_group.grid(row=0, column=1, rowspan=2, sticky='NWE')

  def _mdl_opt_callback(self, tag):
    #print 'Model (%s) is selected' % tag
    self._ncams_callback()

  def _sim_opt_callback(self, tag):
    #print 'Simulator (%s) is selected' % tag
    self._ncams_callback()
  
  def _ncams_callback(self):
    if self.mdl_opt.getvalue() == 'ams':
      self.sim_opt.setitems(['ncsim'])
      self._msgbar.message('warn', 'Only NCsimulator is supported for AMS')
    else:
      self.sim_opt.setitems(['ncsim', 'vcs', 'modelsim'])
    try:
      if self.mdl_opt.getvalue() == 'verilog' or self.sim_opt.getvalue() != 'ncsim':
        self.ncams_control_file_entry.change_state('disabled')
        self.ncams_modellib_file_entry.change_state('disabled')
        self._amsconnrules.configure(entry_state='disabled')
        self.circuit.change_state('disabled')
        return False
      else:
        self.ncams_control_file_entry.change_state('normal')
        self.ncams_modellib_file_entry.change_state('normal')
        self._amsconnrules.configure(entry_state='normal')
        self.circuit.change_state('normal')
        return True
    except Exception as e:
      print(e)
      return False
    


def run_mProbo_GUI():
  root = Tk.Tk()

  Pmw.initialise(root)
  root.title('mProbo - Configuration Editor')
  widget = Startup(root)
  widget.buttonBox.add('Exit', command = root.destroy)
  root.focus_force()
  root.mainloop()

def main():
  run_mProbo_GUI()

if __name__ == '__main__':
  main()

