import sys
import argparse
import re

# Parser
parser = argparse.ArgumentParser(description='Create an SVG file containing a bead plane of a bead crochet bracelet pattern written in a .bead file')
parser.add_argument('patternfile', metavar='patternfile', help='input file written as a .bead pattern')
parser.add_argument('-s', '--size', choices=['small', 'medium', 'large'], default='medium', help="choose between three sizes: small, medium or large")
parser.add_argument('-d', '--diagram', action='store_true', help="create SVG file of the crochet diagram")
parser.add_argument('-p', '--plane', action='store_true', help="create SVG file of the bead plane")
parser.add_argument('-w', '--width', type=int, metavar='N', default=0, help="custom width in number of beads")
parser.add_argument('-H', '--height', type=int, metavar='N', default=0, help="custom height in number of beads")
args = parser.parse_args()

# Determine plane size
def getSize():
    if args.size == 'small':
        rowLength = 3 * around
    elif args.size == 'medium':
        rowLength = 24
    else:
        rowLength = 6 * around
    rowNumber = int(round((2*rowLength - 2)/1.732050808 + 1))
    if args.width > 0:
        rowLength = args.width
    if args.height > 0:
        rowNumber = args.height
    return rowLength, rowNumber

# Make plane matrix of color codes
def getPlaneMatrix(rowLength, rowNumber):
    colorMatrix = []
    patternCounter = 0
    odd = 0
    for i in range(rowNumber):
        row = []
        for j in range(rowLength + odd):
            row.append(pattern[(patternCounter + j) % len(pattern)])
        colorMatrix.append(row)
        if i % 2 == 0:
            odd = -1
            patternCounter = (patternCounter + around + 1) % len(pattern)
        else:
            odd = 0
            patternCounter = (patternCounter + around) % len(pattern)
    return colorMatrix

# Make SVG image from color matrix
def makeImage(colorMatrix, diagram):
    if diagram:
        diagramStr = '-diagram'
    else:
        diagramStr = ''
    with open(filename[:filename.find('.')]+diagramStr+'.svg', 'w+') as image:
        image.write(f"<svg viewBox=\"-0.015 {(-1)*(len(colorMatrix)-1)*0.866025405 -1.015} {len(colorMatrix[0]) + 0.03} {((len(colorMatrix)-1)*0.866025405 + 1.03)}\"  xmlns=\"http://www.w3.org/2000/svg\">\n")
        for i in range(len(colorMatrix)):
            for j in range(len(colorMatrix[i])):
                if i % 2 == 0:
                    odd = 0
                else:
                    odd = 0.5
                try:
                    image.write(f"<circle cx=\"{0.5 + j + odd}\" cy=\"{-0.5 - 0.866025404*i}\" r=\"0.5\" fill=\"{colors[colorMatrix[i][j]]}\" stroke=\"black\" stroke-width=\"0.01\"/>\n")
                except KeyError:
                    print("Error: Color code in pattern lines not recognized")
                    sys.exit()
        image.write(f"</svg>")

def makePlane():
    rowLength, rowNumber = getSize()
    colorMatrix = getPlaneMatrix(rowLength, rowNumber)
    makeImage(colorMatrix, False)

# Make diagram matrix of color codes
def makeDiagramMatrix():
    colorMatrix = []
    patternCounter = 0
    even = 1
    for i in range(int(len(pattern) / (around + 0.5)) + 1):
        row = []
        for j in range(around + even):
            row.append(pattern[patternCounter])
            patternCounter += 1
            if patternCounter >= len(pattern):
                break
        colorMatrix.append(row)
        if i % 2 == 0:
            even = 0
        else:
            even = 1
    return colorMatrix

def makeDiagram():
    colorMatrix = makeDiagramMatrix()
    makeImage(colorMatrix, True)

# Read file
with open(args.patternfile) as file:
    filename = file.name
    pattern = []
    colors = {}
    lines = file.readlines()
    for line in lines:
        if 'around' in line:
            try:
                around = int(re.search(r'\d+', line).group())
            except AttributeError:
                print(f'Error: No \'around\' value in {file.name}')
                sys.exit()
        # Color
        elif 'color' in line:
            name = line[5:(line.find('='))].strip(' ')
            color = line[line.find('=')+1:].strip(' ')
            colors[name] = color
        elif '=' not in line:
            for c in line.split(' '):
                for i in range(int(re.search(r'\d+', c).group())):
                    pattern.append(re.search(r'[a-zA-Z]+', c).group())

# Decide which images to produce
if args.diagram:
    makeDiagram()
    if args.plane:
        makePlane()
else:
    makePlane()
