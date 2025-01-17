## Try parse 2
import xml.etree.ElementTree as ET

def get_element_text(element, xpath, ns):
    """
    Helper function to safely get text from XML elements
    
    Args:
        element: XML element to search in
        xpath: XPath to search for
        ns: Namespace dictionary
    
    Returns:
        Text content of element or None if not found
    """
    found = element.find(xpath, ns)
    return found.text if found is not None else None


file_path = 'snowpits_200_MT/snowpits-66387-caaml.xml'
tree = ET.parse(file_path)
root = tree.getroot()

# Define the namespace
ns = {'caaml': 'http://caaml.org/Schemas/V5.0/Profiles/SnowProfileIACS'}

# Find all layers
layers = root.findall('.//caaml:stratProfile/caaml:Layer', ns)


# Process each layer
for i, layer in enumerate(layers, 1):
    print('made it here')
    print(f"\nLayer {i}:")
    
    # Basic properties
    print(f"Depth from surface: {get_element_text(layer, './/caaml:depthTop', ns )} cm")
    print(f"Thickness: {get_element_text(layer, './/caaml:thickness', ns)} cm")
    
    # Grain properties
    print(f"Primary grain form: {get_element_text(layer, './/caaml:grainFormPrimary', ns)}")
    print(f"Secondary grain form: {get_element_text(layer, './/caaml:grainFormSecondary', ns)}")
    print(f"Grain size avg: {get_element_text(layer, './/caaml:grainSize/caaml:Components/caaml:avg', ns)} mm")
    print(f"Grain size max: {get_element_text(layer, './/caaml:grainSize/caaml:Components/caaml:max', ns)} mm")
    
    # Physical properties
    print(f"Hardness: {get_element_text(layer, './/caaml:hardness', ns)}")
    print(f"Wetness: {get_element_text(layer, './/caaml:wetness', ns)}")
    
    # Optional density if available
    density = layer.find('.//caaml:density', ns)
    if density is not None:
        print(f"Density: {get_element_text(layer, './/caaml:density', ns)} kg/m³")