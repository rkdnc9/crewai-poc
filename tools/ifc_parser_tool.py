"""
IFC Parser Tool - Extracts wall panel data from IFC files
"""
import json
from typing import Dict, List, Any
from crewai.tools import tool
import ifcopenshell
from tools.deterministic_checker import PanelData, Stud, Opening, Duct


@tool("IFC Parser")
def parse_ifc_file(ifc_file_path: str) -> str:
    """
    Parses IFC building model files and extracts wall panel information
    including stud locations, openings, ducts, and panel dimensions.
    Returns structured JSON data for validation.

    Args:
        ifc_file_path: Path to the IFC file to parse

    Returns:
        JSON string with wall panel data
    """
    try:
        # Open IFC file
        ifc_file = ifcopenshell.open(ifc_file_path)

        # Extract wall panels
        panels = _extract_wall_panels(ifc_file)

        result = {
            "status": "success",
            "file_path": ifc_file_path,
            "panels": panels,
            "total_panels": len(panels)
        }

        return json.dumps(result, indent=2)

    except FileNotFoundError:
        return json.dumps({
            "status": "error",
            "message": f"IFC file not found: {ifc_file_path}"
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error parsing IFC file: {str(e)}"
        })


def parse_ifc_file_to_panel_data(ifc_file_path: str) -> PanelData:
    """
    Parse IFC file and return structured PanelData object for deterministic checking.
    
    Args:
        ifc_file_path: Path to the IFC file
        
    Returns:
        PanelData object with parsed information
    """
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        
        # Extract first wall panel (in production, could handle multiple)
        walls = ifc_file.by_type("IfcWall")
        if not walls:
            raise ValueError("No walls found in IFC file")
        
        wall = walls[0]
        
        # Extract panel metadata
        panel_id = wall.GlobalId if hasattr(wall, 'GlobalId') else "PANEL_001"
        panel_name = wall.Name if hasattr(wall, 'Name') else f"Panel_{panel_id}"
        
        # Extract properties from IFC
        dimensions = _extract_dimensions(wall)
        studs_data = _extract_studs_data(wall, ifc_file)
        openings_data = _extract_openings_data(wall, ifc_file)
        ducts_data = _extract_ducts_data(wall, ifc_file)
        seismic_zone = _extract_seismic_zone(wall, ifc_file)
        
        # Create PanelData object
        panel = PanelData(
            panel_id=str(panel_id),
            name=str(panel_name),
            width_mm=dimensions.get('width_mm', 3660),
            height_mm=dimensions.get('height_mm', 2440),
            studs=studs_data,
            openings=openings_data,
            ducts=ducts_data,
            seismic_zone=seismic_zone
        )
        
        return panel
        
    except Exception as e:
        print(f"Error parsing IFC file to PanelData: {e}")
        raise


def _extract_studs_data(wall, ifc_file) -> List[Stud]:
    """Extract studs as Stud objects"""
    studs = []
    studs_raw = _extract_studs(wall, ifc_file)
    
    for stud in studs_raw:
        studs.append(Stud(
            stud_id=stud.get('stud_id', 'UNKNOWN'),
            position_mm=float(stud.get('position_mm', 0)),
            width_mm=float(stud.get('width_mm', 89)),
            depth_mm=float(stud.get('depth_mm', 89))
        ))
    
    return studs


def _extract_openings_data(wall, ifc_file) -> List[Opening]:
    """Extract openings as Opening objects"""
    openings = []
    openings_raw = _extract_openings(wall, ifc_file)
    
    for opening in openings_raw:
        openings.append(Opening(
            opening_id=opening.get('opening_id', 'UNKNOWN'),
            opening_type=opening.get('type', 'window'),
            position_mm=float(opening.get('position_mm', 0)),
            width_mm=float(opening.get('width_mm', 900)),
            height_mm=float(opening.get('height_mm', 1200)),
            has_jack_studs=opening.get('has_jack_studs', False),
            has_header=opening.get('has_header', False),
            is_corner=opening.get('is_corner', False)
        ))
    
    return openings


def _extract_ducts_data(wall, ifc_file) -> List[Duct]:
    """Extract ducts as Duct objects"""
    ducts = []
    ducts_raw = _extract_ducts(wall, ifc_file)
    
    for duct in ducts_raw:
        ducts.append(Duct(
            duct_id=duct.get('duct_id', 'UNKNOWN'),
            position_mm=float(duct.get('position_mm', 0)),
            diameter_mm=float(duct.get('diameter_mm', 150)),
            clearance_from_stud_mm=float(duct.get('clearance_from_stud_mm', 30))
        ))
    
    return ducts


def _extract_seismic_zone(wall, ifc_file) -> int:
    """Extract seismic zone from wall properties"""
    try:
        if hasattr(wall, 'IsDefinedBy'):
            for definition in wall.IsDefinedBy:
                if definition.is_a('IfcRelDefinesByProperties'):
                    property_set = definition.RelatingPropertyDefinition
                    if hasattr(property_set, 'HasProperties'):
                        for prop in property_set.HasProperties:
                            if hasattr(prop, 'Name') and 'seismic' in prop.Name.lower():
                                return int(prop.NominalValue.wrappedValue)
    except:
        pass
    
    return 1  # Default to seismic zone 1


def _extract_wall_panels(ifc_file) -> List[Dict[str, Any]]:
    """Extract wall panel information from IFC file"""
    panels = []

    # Get all walls from IFC
    walls = ifc_file.by_type("IfcWall")

    for idx, wall in enumerate(walls):
        print(f"extracting wall: {idx}")
        panel_data = {
            "panel_id": f"panel_{idx + 1:02d}",
            "name": wall.Name if hasattr(wall, 'Name') else f"Wall_{idx + 1}",
            "global_id": wall.GlobalId if hasattr(wall, 'GlobalId') else "",
            "dimensions": _extract_dimensions(wall),
            "studs": _extract_studs(wall, ifc_file),
            "openings": _extract_openings(wall, ifc_file),
            "ducts": _extract_ducts(wall, ifc_file)
        }

        panels.append(panel_data)

    return panels


def _extract_dimensions(wall) -> Dict[str, float]:
    """Extract wall dimensions"""
    dimensions = {
        "height_mm": 2440.0,  # Default 8ft
        "width_mm": 3000.0,   # Default
        "thickness_mm": 140.0  # Default
    }

    try:
        # Try to get actual dimensions from IFC properties
        if hasattr(wall, 'IsDefinedBy'):
            for definition in wall.IsDefinedBy:
                if definition.is_a('IfcRelDefinesByProperties'):
                    property_set = definition.RelatingPropertyDefinition
                    if hasattr(property_set, 'HasProperties'):
                        for prop in property_set.HasProperties:
                            if prop.Name == 'Height':
                                dimensions['height_mm'] = float(prop.NominalValue.wrappedValue)
                            elif prop.Name == 'Width' or prop.Name == 'Length':
                                dimensions['width_mm'] = float(prop.NominalValue.wrappedValue)
                            elif prop.Name == 'Thickness':
                                dimensions['thickness_mm'] = float(prop.NominalValue.wrappedValue)
    except:
        pass  # Use defaults

    return dimensions


def _extract_studs(wall, ifc_file) -> List[Dict[str, Any]]:
    """Extract stud locations and dimensions from IFC file"""
    studs = []

    # Try to extract studs from IFC file (IfcMember or IfcBuildingElementProxy)
    try:
        # Get all members (structural elements like studs)
        members = ifc_file.by_type("IfcMember")
        proxies = ifc_file.by_type("IfcBuildingElementProxy")

        # Combine potential stud elements
        potential_studs = list(members) + list(proxies)

        # Filter studs that are related to this wall
        wall_studs = []
        for element in potential_studs:
            # Check if element is associated with this wall
            # This can be done through spatial containment, aggregation, or naming
            is_wall_stud = False

            # Method 1: Check if element name contains "stud" (case-insensitive)
            if hasattr(element, 'Name') and element.Name and 'stud' in element.Name.lower():
                is_wall_stud = True

            # Method 2: Check spatial relationships (if element is contained in same space as wall)
            if hasattr(element, 'ContainedInStructure'):
                for rel in element.ContainedInStructure:
                    if hasattr(wall, 'ContainedInStructure'):
                        for wall_rel in wall.ContainedInStructure:
                            if rel.RelatingStructure == wall_rel.RelatingStructure:
                                is_wall_stud = True
                                break

            if is_wall_stud:
                wall_studs.append(element)

        # Extract dimensions and position from each stud
        for idx, stud_element in enumerate(wall_studs):
            stud_data = {
                "stud_id": stud_element.GlobalId if hasattr(stud_element, 'GlobalId') else f"stud_{idx + 1:02d}",
                "position_mm": 0.0,  # Default
                "height_mm": 2440.0,  # Default
                "width_mm": 38.0,    # Default
                "depth_mm": 89.0     # Default
            }

            # Extract dimensions from IFC properties
            try:
                if hasattr(stud_element, 'IsDefinedBy'):
                    for definition in stud_element.IsDefinedBy:
                        if definition.is_a('IfcRelDefinesByProperties'):
                            property_set = definition.RelatingPropertyDefinition
                            if hasattr(property_set, 'HasProperties'):
                                for prop in property_set.HasProperties:
                                    prop_name = prop.Name.lower() if hasattr(prop, 'Name') else ''

                                    if 'height' in prop_name or 'length' in prop_name:
                                        stud_data['height_mm'] = float(prop.NominalValue.wrappedValue)
                                    elif 'width' in prop_name:
                                        stud_data['width_mm'] = float(prop.NominalValue.wrappedValue)
                                    elif 'depth' in prop_name or 'thickness' in prop_name:
                                        stud_data['depth_mm'] = float(prop.NominalValue.wrappedValue)
                                    elif 'position' in prop_name or 'location' in prop_name:
                                        stud_data['position_mm'] = float(prop.NominalValue.wrappedValue)

                # Try to extract position from object placement
                if hasattr(stud_element, 'ObjectPlacement'):
                    placement = stud_element.ObjectPlacement
                    if hasattr(placement, 'RelativePlacement'):
                        rel_placement = placement.RelativePlacement
                        if hasattr(rel_placement, 'Location'):
                            location = rel_placement.Location
                            if hasattr(location, 'Coordinates'):
                                coords = location.Coordinates
                                if len(coords) >= 1:
                                    # Assuming X coordinate represents position along wall
                                    stud_data['position_mm'] = float(coords[0]) if coords[0] is not None else stud_data['position_mm']
            except Exception as e:
                # If extraction fails, keep defaults
                pass

            studs.append(stud_data)

    except Exception as e:
        # If stud extraction fails, log but continue
        pass

    # If no studs found in IFC, return empty list (don't generate)
    # This ensures we only use data from IFC file
    if not studs:
        print(f"Warning: No studs found in IFC for wall {wall.Name if hasattr(wall, 'Name') else 'Unknown'}")

    return studs


def _extract_openings(wall, ifc_file) -> List[Dict[str, Any]]:
    """Extract door and window openings"""
    openings = []

    # Get openings that void this wall
    if hasattr(wall, 'HasOpenings'):
        for rel_void in wall.HasOpenings:
            opening = rel_void.RelatedOpeningElement

            opening_data = {
                "opening_id": opening.GlobalId if hasattr(opening, 'GlobalId') else f"opening_{len(openings) + 1}",
                "type": "window",  # Default
                "position_mm": 1000.0,  # Default position
                "width_mm": 900.0,
                "height_mm": 1200.0,
                "has_jack_studs": False,  # To be checked
                "has_header": False,      # To be checked
                "is_corner": False        # Default
            }

            # Try to determine if it's a door or window and extract properties
            try:
                # Check if there's a related door or window
                filled_by = ifc_file.get_inverse(opening)
                for rel in filled_by:
                    if rel.is_a('IfcRelFillsElement'):
                        element = rel.RelatedBuildingElement
                        if element.is_a('IfcDoor'):
                            opening_data['type'] = 'door'
                        elif element.is_a('IfcWindow'):
                            opening_data['type'] = 'window'
                        
                        # Extract opening properties
                        if hasattr(element, 'IsDefinedBy'):
                            for definition in element.IsDefinedBy:
                                if definition.is_a('IfcRelDefinesByProperties'):
                                    property_set = definition.RelatingPropertyDefinition
                                    if hasattr(property_set, 'HasProperties'):
                                        for prop in property_set.HasProperties:
                                            prop_name = prop.Name if hasattr(prop, 'Name') else ''
                                            if prop_name == 'Position':
                                                opening_data['position_mm'] = float(prop.NominalValue.wrappedValue)
                                            elif prop_name == 'Width':
                                                opening_data['width_mm'] = float(prop.NominalValue.wrappedValue)
                                            elif prop_name == 'Height':
                                                opening_data['height_mm'] = float(prop.NominalValue.wrappedValue)
                                            elif prop_name == 'HasJackStuds':
                                                opening_data['has_jack_studs'] = bool(prop.NominalValue.wrappedValue)
                                            elif prop_name == 'HasHeader':
                                                opening_data['has_header'] = bool(prop.NominalValue.wrappedValue)
                                            elif prop_name == 'IsCorner':
                                                opening_data['is_corner'] = bool(prop.NominalValue.wrappedValue)
            except:
                pass

            openings.append(opening_data)

    return openings


def _extract_ducts(wall, ifc_file) -> List[Dict[str, Any]]:
    """Extract duct and MEP penetrations"""
    ducts = []

    # Look for IfcFlowSegment or IfcDuctSegment near this wall
    try:
        flow_segments = ifc_file.by_type("IfcFlowSegment")
        duct_segments = ifc_file.by_type("IfcDuctSegment")

        all_ducts = list(flow_segments) + list(duct_segments)

        # For POC, create sample duct data
        # In production, would calculate intersection with wall
        for idx, duct in enumerate(all_ducts[:2]):  # Limit to 2 for demo
            ducts.append({
                "duct_id": duct.GlobalId if hasattr(duct, 'GlobalId') else f"duct_{idx + 1}",
                "position_mm": 1500.0 + (idx * 500),
                "diameter_mm": 150.0,
                "clearance_from_stud_mm": 30.0  # To be validated
            })
    except:
        pass  # No ducts found

    return ducts
