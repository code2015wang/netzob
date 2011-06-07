#!/usr/bin/python
# coding: utf8

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import gtk
import pango
import gobject
import re
import pygtk
pygtk.require('2.0')

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
import MessageGroup
import TracesExtractor

#+---------------------------------------------- 
#| UIseqMessage :
#|     GUI for message sequencing
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class UIseqMessage:
    TARGET_TYPE_TEXT = 80
    TARGETS = [('text/plain', 0, TARGET_TYPE_TEXT)]
    
    #+---------------------------------------------- 
    #| Called when user select a new trace
    #+----------------------------------------------
    def new(self):
        # Parse the traces and store the results
        tracesExtractor = TracesExtractor.TracesExtractor(self.zob.tracePath, self.uizob)
        self.selectedGroup = ""
        task = tracesExtractor.parse(self.groups, self)
        gobject.idle_add(task.next)

    def update(self):
        self.updateTreeStoreGroup()
        self.updateTreeStoreMessage()

    def clear(self):
        pass

    def kill(self):
        pass
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param groups: list of all groups 
    #+----------------------------------------------   
    def __init__(self, uizob):
        self.uizob = uizob
        self.zob = self.uizob.zob
        self.groups = []
        self.selectedGroup = ""

        self.panel = gtk.HBox(False, spacing=10)
        self.vb_sortie = gtk.VBox(False, spacing=0)
        self.vb_filter = gtk.VBox(False, spacing=0)

        self.panel.pack_start(self.vb_filter, False, False, 0)
        self.panel.pack_start(self.vb_sortie, False, False, 0)

        self.vb_sortie.set_size_request(-1, -1)
        self.vb_filter.set_size_request(-1, -1)

        self.vb_sortie.show()
        self.vb_filter.show()
        self.panel.show()
        
        #+---------------------------------------------- 
        #| LEFT PART OF THE GUI : TREEVIEW
        #+----------------------------------------------        
        
        # Tree store contains :
        # str : type {"group" or "message"}
        # str : text
        # str : color foreground
        # str : color background
        self.treestoreGroup = gtk.TreeStore(str, str, str, str)
       
        self.treeViewGroups = gtk.TreeView(self.treestoreGroup)
        # enable dropping data in a group
        self.treeViewGroups.enable_model_drag_dest(self.TARGETS, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.treeViewGroups.connect("drag_data_received", self.drop_fromDND)

        # messages list
        scroll_lib = gtk.ScrolledWindow()
        scroll_lib.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll_lib.show()
        scroll_lib.set_size_request(300, 700)
        scroll_lib.add(self.treeViewGroups)
        
        self.vb_filter.pack_start(scroll_lib, False, False, 0)
        

        self.treeViewGroups.connect("cursor-changed", self.messageChanged)
        self.treeViewGroups.connect('button-press-event',self.button_press_on_treeview_groups)

        lvcolumn = gtk.TreeViewColumn('Messages')
        lvcolumn.set_sort_column_id(1)
        cell = gtk.CellRendererText()
        lvcolumn.pack_start(cell, True)
        cell.set_property('background-set' , True)
        cell.set_property('foreground-set' , True)
        lvcolumn.set_attributes(cell, text=1, foreground=2, background=3)
        self.treeViewGroups.append_column(lvcolumn)
        self.treeViewGroups.show()


        #+---------------------------------------------- 
        #| RIGHT PART OF THE GUI : TREEVIEW
        #+----------------------------------------------      

        # messages output
        sortie_frame = gtk.Frame()
        sortie_frame.set_label("Message output")
        sortie_frame.show()
        
        # Tree store contains :
        # str : text
        self.treestoreMessage = gtk.TreeStore(str, str, str)
        
        self.treeViewDetail = gtk.TreeView(self.treestoreMessage)
        self.treeViewDetail.set_reorderable(True)
        # enable dragging message out of current group
        self.treeViewDetail.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,self.TARGETS,
                  gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.treeViewDetail.connect("drag-data-get", self.drag_fromDND)      
        
        
        
        cellDetail2 = gtk.CellRendererText()
        lvcolumnDetail2 = gtk.TreeViewColumn('Messages')
        
        lvcolumnDetail2.pack_start(cellDetail2, True)
        lvcolumnDetail2.set_attributes(cellDetail2, text=0)
        lvcolumnDetail2.set_attributes(cellDetail2, markup=0)
        
        self.treeViewDetail.append_column(lvcolumnDetail2)
        
        self.treeViewDetail.show()
        
        scroll_sortie = gtk.ScrolledWindow()
        scroll_sortie.set_size_request(1200, 800)
        scroll_sortie.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll_sortie.show()
        scroll_sortie.add(self.treeViewDetail)
        sortie_frame.add(scroll_sortie)
        self.vb_sortie.pack_start(sortie_frame, False, False, 0)
       
    
    #+---------------------------------------------- 
    #| button_press_on_treeview_groups :
    #|   operation when the user click on the treeview.
    #|   mainly to open a contextual menu
    #+----------------------------------------------
    def button_press_on_treeview_groups(self,obj,event):
        print "[DEBUG] User requested a contextual menu (treeview group)"
        
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_context_menu_for_groups(event)

    #+---------------------------------------------- 
    #| build_context_menu_for_groups :
    #|   Create a menu to display available operations
    #|   on the treeview groups
    #+----------------------------------------------
    def build_context_menu_for_groups(self, event):
        
        x = int(event.x)
        y = int(event.y)
        pthinfo = self.treeViewGroups.get_path_at_pos(x, y)
        if pthinfo is None:
            canWeDelete = 0
        else :
            canWeDelete = 1    
        entries =[        
                  (gtk.STOCK_ADD, self.displayPopupToCreateGroup,1),
                  (gtk.STOCK_REMOVE, self.displayPopupToRemoveGroup,canWeDelete)
        ]

        menu = gtk.Menu()
        for stock_id,callback,sensitivity in entries:
            item = gtk.ImageMenuItem(stock_id)
            if callback:
                item.connect("activate",callback)   
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        menu.popup(None,None,None,event.button,event.time)     

    #+---------------------------------------------- 
    #| displayPopupToCreateGroup_ResponseToDialog :
    #|   pygtk is so good ! arf :( 
    #+----------------------------------------------
    def displayPopupToCreateGroup_ResponseToDialog(self, entry, dialog, response):
        dialog.response(response)
    
    #+---------------------------------------------- 
    #| displayPopupToCreateGroup :
    #|   Display a form to create a new group.
    #|   Based on the famous dialogs
    #+----------------------------------------------
    def displayPopupToCreateGroup(self, event):
        print "[DEBUG] Display a popup to create a group"
        #base this on a message dialog
        dialog = gtk.MessageDialog(
                                   None,
                                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_QUESTION,
                                   gtk.BUTTONS_OK,
                                   None)
        dialog.set_markup('Please enter the <b>new group name</b>:')
        #create the text input field
        entry = gtk.Entry()
        #allow the user to press enter to do ok
        entry.connect("activate", self.displayPopupToCreateGroup_ResponseToDialog, dialog, gtk.RESPONSE_OK)
        #create a horizontal box to pack the entry and a label
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("Group Name :"), False, 5, 5)
        hbox.pack_end(entry)
        #some secondary text
        dialog.format_secondary_markup("<b>Warning Grand'Ma</b> : Be sure not to create two groups with the same name.")
        #add it and show it
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()
        #go go go
        dialog.run()
        newGroupName = entry.get_text()
        dialog.destroy()
        
        if (len(newGroupName)>0) :
            print "[DEBUG] a new group will created with the given name : {0}".format(newGroupName)
            
            newGroup = MessageGroup.MessageGroup(newGroupName, [])
            self.groups.append(newGroup)
            #Update Left and Right
            self.updateTreeStoreGroup()
            self.updateTreeStoreMessage()
        
        
        
        
        
        
    
    def displayPopupToRemoveGroup(self, event):
        print "on delete"
        
    #+---------------------------------------------- 
    #| drop_fromDND :
    #|   defines the operation executed when a message is
    #|   is dropped out current group to the selected group 
    #+----------------------------------------------
    def drop_fromDND(self, treeview, context, x, y, selection, info, etime):
        modele = treeview.get_model()
        donnees = selection.data
        info_depot = treeview.get_dest_row_at_pos(x, y)
        
        if info_depot :
            chemin, position = info_depot
            iter = modele.get_iter(chemin)
            new_grp_name = str(modele.get_value(iter, 1))
        
            found = False
            for tmp_group in self.groups :
                if (tmp_group.getName() == new_grp_name) :
                    new_grp = tmp_group
                for tmp_message in tmp_group.getMessages() :
                    if (str(tmp_message.getID()) == donnees) :
                        msg = tmp_message
                        old_grp = tmp_group
                        found = True
        
        if (found) :
            print "[DEBUG] The message {0} must be moved out its current group {1} to the new group {2}".format(msg.getID(), old_grp.getName(), new_grp.getName())
            #Removing from its old group
            old_grp.removeMessage(msg)
            #Adding to its new group
            new_grp.addMessage(msg)
            
            #Update Left and Right
            self.updateTreeStoreGroup()
            self.updateTreeStoreMessage()
          
        return
   
   

   
    #+---------------------------------------------- 
    #| drag_fromDND :
    #|   defines the operation executed when a message is
    #|   is dragged out current group 
    #+----------------------------------------------
    def drag_fromDND(self, treeview, contexte, selection, info, dateur):
      treeselection = treeview.get_selection()
      modele, iter = treeselection.get_selected()
      texte = str(modele.get_value(iter, 2))

      selection.set(selection.target, 8, texte)
      return
    
    
    #+---------------------------------------------- 
    #| Update the content of the tree store for groups
    #+----------------------------------------------
    def updateTreeStoreGroup(self):
        self.treestoreGroup.clear()
        for group in self.groups :
            #
            iter = self.treestoreGroup.append(None, ["Group", group.getName(), '#000000', '#FF00FF'])
            for message in group.getMessages() :
                self.treestoreGroup.append(iter, ["Message", message.getID(), '#000000', '#FF00FF'])
        
    #+---------------------------------------------- 
    #| Update the content of the tree store for messages
    #+----------------------------------------------
    def updateTreeStoreMessage(self):
        self.treestoreMessage.clear()
        if (self.selectedGroup != "") :
            for group in self.groups :
                if (group.getName() == self.selectedGroup) :
                    for message in group.getMessages() :
                        print group.getRegex()
                        self.treestoreMessage.append(None, [message.getPangoData(group.getRegex()), group.getRegex(), message.getID()])
   
       
#+---------------------------------------------- 
#| CALLBACKS 
#+----------------------------------------------

    #+---------------------------------------------- 
    #| Called when user click on a group or on a message
    #+----------------------------------------------
    def messageChanged(self, treeview):
        (modele, iter) = self.treeViewGroups.get_selection().get_selected()
        if(iter):
            if(modele.iter_is_valid(iter)):
                
                type = modele.get_value(iter, 0)
                name = modele.get_value(iter, 1)
                
                if (type == "Group") :
                    print "Group : {0}".format(name)
                    self.selectedGroup = name
                    self.updateTreeStoreMessage()
                    
                if (type == "Message") :
                    print "Message : {0}".format(name)    
