from twisted.internet import protocol
from cStringIO import StringIO
import sys

class PdfWriter(protocol.ProcessProtocol):
    def __init__(self, data, d):
        self.data = data
        self.encoded = StringIO()
        self.d = d
    
    def connectionMade(self):
        self.transport.write(self.data)
        self.transport.closeStdin()


    def outReceived(self, data):
        self.encoded.write(data)

    def outConnectionLost(self):
        self.transport.loseConnection()
        self.d.callback(self.encoded.getvalue())

    def processEnded(self, reason):
        pass

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate

def main():

    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']
    story = []
    # add some flowables
    story.append(Paragraph("This is a Heading",styleH))
    story.append(Paragraph("This is a paragraph in <i>Normal</i> style.",
                           styleN))
    doc = SimpleDocTemplate(sys.stdout,pagesize = letter)
    doc.build(story)

    # sys.stdout.write('Hellow!')
    sys.exit(0)

if __name__ == "__main__":
    main()
