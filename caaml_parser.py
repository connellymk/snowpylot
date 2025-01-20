from xml.dom import minidom
import os
from Layer import Layer
def parse_caaml(folder_path):
    layersList = [] # Initialize list of layer objects

    # Create a list of all CAAML files in the folder
    caaml_files = [f for f in os.listdir(folder_path) if f.endswith('.xml')] # List of all CAAML files in the folder

    # Iterate through each file
    for file in caaml_files:
        
        # Initialize layer object parameters
        depthTop = None
        thickness = None
        grainFormPrimary = None
        grainFormSecondary = None
        hardness = None
        wetness = None

        # Parse the file

        file_path = folder_path + '/' + file
        doc = minidom.parse(file_path)
        root = doc.documentElement

        # Get all Layer nodes
        layers = root.getElementsByTagName('caaml:Layer')

        # Process each layer
        for i, layer in enumerate(layers, 1):
            print(f"\nLayer {i}:")

        
    return layersList

