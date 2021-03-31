import sys
import argparse
import re
from typing import Dict, List, Tuple

# Parser
parser = argparse.ArgumentParser(description='Create an SVG file containing a bead plane of a bead crochet bracelet pattern written in a .bead file')
parser.add_argument('patternfile', metavar='patternfile', help='input file written as a .bead pattern')
parser.add_argument('-s', '--size', choices=['small', 'medium', 'large'], default='medium', help="choose between three sizes: small, medium or large")
parser.add_argument('-d', '--diagram', action='store_true', help="create SVG file of the crochet diagram")
parser.add_argument('-p', '--plane', action='store_true', help="create SVG file of the bead plane")
parser.add_argument('-w', '--width', type=int, metavar='N', default=0, help="custom width in number of beads")
parser.add_argument('-H', '--height', type=int, metavar='N', default=0, help="custom height in number of beads")
args = parser.parse_args()


def getSize() -> Tuple[int, int]:
    """Determines plane size

    Returns
    -------
    rowLength : int
    rowNumber : int
    """
    rowLength: int = 6 * around
    if args.size == 'small':
        rowLength = 3 * around
    elif args.size == 'medium':
        rowLength = 24
    rowNumber: int = int(round((2*rowLength - 2)/1.732050808 + 1))
    if args.width > 0:
        rowLength = args.width
    if args.height > 0:
        rowNumber = args.height
    return rowLength, rowNumber


def getPlaneMatrix(rowLength: int, rowNumber: int) -> List[List[str]]:
    """Makes a plane matrix of color codes

    Parameters
    ----------
    rowLength : int
    rowNumber : int

    Returns
    -------
    colorMatrix : List[List[str]]
    """
    colorMatrix: List[List[str]] = []
    patternCounter = 0
    odd = 0
    for i in range(rowNumber):
        row = [pattern[(patternCounter + j) % len(pattern)] for j in range(rowLength + odd)]
        colorMatrix.append(row)
        odd = -1 if i % 2 == 0 else 0
        patternCounter = (patternCounter + around - odd) % len(pattern)
    return colorMatrix


def makeImage(colorMatrix: List[List[str]], diagram: bool) -> None:
    """Makes SVG image from color matrix

    Parameters
    ----------
    colorMatrix : List[List[str]]
    diagram : bool
    """
    diagramStr = ''
    if diagram:
        diagramStr = '-diagram'
    with open(filename[:filename.find('.')] + diagramStr + '.svg', 'w+') as image:
        image.write(f"<svg viewBox=\"-0.015 {(-1)*(len(colorMatrix)-1)*0.866025405 -1.015} {len(colorMatrix[0]) + 0.03} {((len(colorMatrix)-1)*0.866025405 + 1.03)}\"  xmlns=\"http://www.w3.org/2000/svg\">\n")
        for i in range(len(colorMatrix)):
            for j in range(len(colorMatrix[i])):
                odd = 0 if i % 2 == 0 else 0.5
                try:
                    image.write(f"<circle cx=\"{0.5 + j + odd}\" cy=\"{-0.5 - 0.866025404*i}\" r=\"0.5\" fill=\"{colors[colorMatrix[i][j]]}\" stroke=\"black\" stroke-width=\"0.03\"/>\n")
                except KeyError:
                    print("Error: Color code in pattern lines not recognized")
                    sys.exit()
        image.write(f"</svg>")


def makePlane() -> None:
    """Makes a plane"""
    rowLength, rowNumber = getSize()
    colorMatrix = getPlaneMatrix(rowLength, rowNumber)
    makeImage(colorMatrix, False)


def makeDiagramMatrix() -> List[List[str]]:
    """Makes a diagram matrix of color codes

    Returns
    -------
    colorMatrix : List[List[str]]
    """
    colorMatrix: List[List[str]] = []
    patternCounter = 0
    even = 1
    for i in range(int(len(pattern) / (around + 0.5)) + 1):
        row: List[str] = []
        for j in range(around + even):
            row.append(pattern[patternCounter])
            patternCounter += 1
            if patternCounter >= len(pattern):
                break
        colorMatrix.append(row)
        even = 0 if i % 2 == 0 else 1
    return colorMatrix

def makeDiagram() -> None:
    """Makes a diagram"""
    colorMatrix = makeDiagramMatrix()
    makeImage(colorMatrix, True)


if __name__ == '__main__':
    with open(args.patternfile) as file:
        filename = file.name
        pattern: List[str] = []
        colors: Dict[str, str] = {}
        lines = file.readlines()
        for line in lines:
            if 'around' in line:
                try:
                    around = int(re.search(r'\d+', line).group())  # type: ignore
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
                    for i in range(int(re.search(r'\d+', c).group())):  # type: ignore
                        pattern.append(re.search(r'[a-zA-Z]+', c).group())  # type: ignore

    # Decide which images to produce
    if args.diagram:
        makeDiagram()
        if args.plane:
            makePlane()
    else:
        makePlane()
