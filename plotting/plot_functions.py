#def getObjectFromFile (file, object_name, file_path):
#    if not file:
#        print 'Failed to open %s' % file
#        exit(0)
#    object = ROOT.TObject() 
#    object = file.Get(file_path.join("/", object_name)
#    if not hist:
#        print 'Failed to get %s from file' % object_name
#        exit(0)
#    hist.SetDirectory(ROOT.gROOT) # detach "hist" from the file
#    return hist
import ROOT

def getHistFromFile(root_file, name_in_file, rename, path_to_hist):
    if not root_file:
        print 'Failed to open %s' % file
        exit(0)
    hist = ROOT.TH1F()   
    if path_to_hist != "":
        name_in_file = path_to_hist.join(["/", name_in_file]) 
    hist = root_file.Get(name_in_file)
    print hist
    if not hist:
        print 'Failed to get hist %s from file' % name_in_file
        exit(0)
    hist.SetDirectory(ROOT.gROOT) # detach "hist" from the file
    if rename != "":
        hist.SetName(rename)
    return hist
def loadHistFromTree(hist, root_file, path_to_tree, branch_name, 
                     cut_string, append=False):
    if not root_file:
        print 'Failed to open %s' % root_file
        exit(0)
    tree = root_file.Get(path_to_tree)
    if not tree:
        print 'Failed to get tree from file'
        exit(0)
    hist.GetDirectory().cd() 
    hist_name = "".join(["+ " if append else "", hist.GetName()])
    print "name is %s" % hist_name
    old_num = hist.GetEntries()
    num = tree.Draw(branch_name + ">>" + hist_name, cut_string)
    print "Draw Comand is %s" % branch_name + ">>" + hist_name
    print "With cut string %s" % cut_string
    if append:
        if num < old_num:
            print "Failed to append to hist"
    #else:
    #    hist.SetDirectory(ROOT.gROOT) # detach "hist" from the file
    print hist.GetEntries()

