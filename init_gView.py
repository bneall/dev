try:
  import gView.gViewer as gViewer
  gViewerWidget = gViewer.GView()
  mari.app.addTab('gView', gViewerWidget)
  print '##----------------------------'
  print 'gView 0.5.3 Loaded Succesfuly '
  print '##----------------------------'
except:
    print 'Unable to load gView, please check install'
