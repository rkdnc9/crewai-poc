#!/usr/bin/env python3
"""
Generate IFC files from programmatically defined panel data.

This script creates IFC files that contain all the structural details
(studs, openings, dimensions) from the panel definitions in demo.py.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import ifcopenshell
import ifcopenshell.api
from tools.deterministic_checker import PanelData, Stud, Opening


def create_ifc_from_panel(panel: PanelData, output_path: str):
    """
    Create an IFC file from PanelData object.
    
    Args:
        panel: PanelData object with all structural information
        output_path: Path where IFC file will be saved
    """
    # Create IFC file
    ifc = ifcopenshell.file(schema="IFC4")
    
    # Create basic project structure
    project = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject", name=panel.panel_id)
    
    # Create units (millimeters)
    length_unit = ifc.create_entity("IfcSIUnit", UnitType="LENGTHUNIT", Prefix="MILLI", Name="METRE")
    units = ifc.create_entity("IfcUnitAssignment", Units=[length_unit])
    project.UnitsInContext = units
    
    # Create geometric representation context
    origin = ifc.createIfcCartesianPoint((0.0, 0.0, 0.0))
    axis_z = ifc.createIfcDirection((0.0, 0.0, 1.0))
    axis_x = ifc.createIfcDirection((1.0, 0.0, 0.0))
    
    geom_context = ifc.create_entity(
        "IfcGeometricRepresentationContext",
        ContextType="Model",
        CoordinateSpaceDimension=3,
        Precision=0.01,
        WorldCoordinateSystem=ifc.createIfcAxis2Placement3D(origin, axis_z, axis_x),
        TrueNorth=axis_z
    )
    project.RepresentationContexts = [geom_context]
    
    # Create site, building, and storey
    site = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcSite", name="Site")
    building = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcBuilding", name="Building")
    storey = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcBuildingStorey", name="Level 1")
    
    ifcopenshell.api.run("aggregate.assign_object", ifc, products=[site], relating_object=project)
    ifcopenshell.api.run("aggregate.assign_object", ifc, products=[building], relating_object=site)
    ifcopenshell.api.run("aggregate.assign_object", ifc, products=[storey], relating_object=building)
    
    # Create wall panel
    wall_placement = ifc.createIfcAxis2Placement3D(origin, axis_z, axis_x)
    wall = ifc.create_entity(
        "IfcWall",
        GlobalId=ifcopenshell.guid.new(),
        Name=panel.name,
        ObjectPlacement=ifc.createIfcLocalPlacement(RelativePlacement=wall_placement)
    )
    
    # Add wall to storey
    ifcopenshell.api.run("spatial.assign_container", ifc, relating_structure=storey, products=[wall])
    
    # Add wall properties
    pset = ifc.create_entity("IfcPropertySet", GlobalId=ifcopenshell.guid.new(), Name="PanelProperties")
    
    properties = [
        ifc.create_entity("IfcPropertySingleValue", Name="PanelID", NominalValue=ifc.create_entity("IfcLabel", panel.panel_id)),
        ifc.create_entity("IfcPropertySingleValue", Name="Width", NominalValue=ifc.create_entity("IfcLengthMeasure", float(panel.width_mm))),
        ifc.create_entity("IfcPropertySingleValue", Name="Height", NominalValue=ifc.create_entity("IfcLengthMeasure", float(panel.height_mm))),
        ifc.create_entity("IfcPropertySingleValue", Name="SeismicZone", NominalValue=ifc.create_entity("IfcInteger", panel.seismic_zone)),
        ifc.create_entity("IfcPropertySingleValue", Name="StudCount", NominalValue=ifc.create_entity("IfcInteger", len(panel.studs))),
        ifc.create_entity("IfcPropertySingleValue", Name="OpeningCount", NominalValue=ifc.create_entity("IfcInteger", len(panel.openings))),
    ]
    
    pset.HasProperties = properties
    
    # Link property set to wall
    rel_defines = ifc.create_entity(
        "IfcRelDefinesByProperties",
        GlobalId=ifcopenshell.guid.new(),
        RelatedObjects=[wall],
        RelatingPropertyDefinition=pset
    )
    
    # Add studs as IfcMember entities
    for stud in panel.studs:
        stud_origin = ifc.createIfcCartesianPoint((float(stud.position_mm), 0.0, 0.0))
        stud_placement = ifc.createIfcAxis2Placement3D(stud_origin, axis_z, axis_x)
        
        stud_element = ifc.create_entity(
            "IfcMember",
            GlobalId=ifcopenshell.guid.new(),
            Name=f"Stud_{stud.stud_id}",
            ObjectPlacement=ifc.createIfcLocalPlacement(RelativePlacement=stud_placement)
        )
        
        # Add stud to storey
        ifcopenshell.api.run("spatial.assign_container", ifc, relating_structure=storey, products=[stud_element])
        
        # Add stud properties
        stud_pset = ifc.create_entity("IfcPropertySet", GlobalId=ifcopenshell.guid.new(), Name=f"Stud_{stud.stud_id}_Properties")
        stud_props = [
            ifc.create_entity("IfcPropertySingleValue", Name="StudID", NominalValue=ifc.create_entity("IfcLabel", stud.stud_id)),
            ifc.create_entity("IfcPropertySingleValue", Name="Position", NominalValue=ifc.create_entity("IfcLengthMeasure", float(stud.position_mm))),
            ifc.create_entity("IfcPropertySingleValue", Name="Width", NominalValue=ifc.create_entity("IfcLengthMeasure", float(stud.width_mm))),
            ifc.create_entity("IfcPropertySingleValue", Name="Depth", NominalValue=ifc.create_entity("IfcLengthMeasure", float(stud.depth_mm))),
        ]
        stud_pset.HasProperties = stud_props
        
        ifc.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=[stud_element],
            RelatingPropertyDefinition=stud_pset
        )
    
    # Add openings (windows/doors)
    for opening in panel.openings:
        opening_origin = ifc.createIfcCartesianPoint((float(opening.position_mm), 0.0, 0.0))
        opening_placement = ifc.createIfcAxis2Placement3D(opening_origin, axis_z, axis_x)
        
        # Create opening element that voids the wall
        opening_element = ifc.create_entity(
            "IfcOpeningElement",
            GlobalId=ifcopenshell.guid.new(),
            Name=f"Opening_{opening.opening_id}",
            ObjectPlacement=ifc.createIfcLocalPlacement(RelativePlacement=opening_placement)
        )
        
        # Create the void relationship
        rel_voids = ifc.create_entity(
            "IfcRelVoidsElement",
            GlobalId=ifcopenshell.guid.new(),
            RelatingBuildingElement=wall,
            RelatedOpeningElement=opening_element
        )
        
        # Create window/door that fills the opening
        if opening.opening_type.lower() == "window":
            filling_element = ifc.create_entity(
                "IfcWindow",
                GlobalId=ifcopenshell.guid.new(),
                Name=f"Window_{opening.opening_id}",
                ObjectPlacement=ifc.createIfcLocalPlacement(RelativePlacement=opening_placement)
            )
        else:
            filling_element = ifc.create_entity(
                "IfcDoor",
                GlobalId=ifcopenshell.guid.new(),
                Name=f"Door_{opening.opening_id}",
                ObjectPlacement=ifc.createIfcLocalPlacement(RelativePlacement=opening_placement)
            )
        
        # Add to storey
        ifcopenshell.api.run("spatial.assign_container", ifc, relating_structure=storey, products=[filling_element])
        
        # Fill the opening
        rel_fills = ifc.create_entity(
            "IfcRelFillsElement",
            GlobalId=ifcopenshell.guid.new(),
            RelatingOpeningElement=opening_element,
            RelatedBuildingElement=filling_element
        )
        
        # Add opening properties
        opening_pset = ifc.create_entity("IfcPropertySet", GlobalId=ifcopenshell.guid.new(), Name=f"Opening_{opening.opening_id}_Properties")
        opening_props = [
            ifc.create_entity("IfcPropertySingleValue", Name="OpeningID", NominalValue=ifc.create_entity("IfcLabel", opening.opening_id)),
            ifc.create_entity("IfcPropertySingleValue", Name="Type", NominalValue=ifc.create_entity("IfcLabel", opening.opening_type)),
            ifc.create_entity("IfcPropertySingleValue", Name="Position", NominalValue=ifc.create_entity("IfcLengthMeasure", float(opening.position_mm))),
            ifc.create_entity("IfcPropertySingleValue", Name="Width", NominalValue=ifc.create_entity("IfcLengthMeasure", float(opening.width_mm))),
            ifc.create_entity("IfcPropertySingleValue", Name="Height", NominalValue=ifc.create_entity("IfcLengthMeasure", float(opening.height_mm))),
            ifc.create_entity("IfcPropertySingleValue", Name="HasJackStuds", NominalValue=ifc.create_entity("IfcBoolean", opening.has_jack_studs)),
            ifc.create_entity("IfcPropertySingleValue", Name="HasHeader", NominalValue=ifc.create_entity("IfcBoolean", opening.has_header)),
            ifc.create_entity("IfcPropertySingleValue", Name="IsCorner", NominalValue=ifc.create_entity("IfcBoolean", opening.is_corner)),
        ]
        opening_pset.HasProperties = opening_props
        
        ifc.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=[filling_element],
            RelatingPropertyDefinition=opening_pset
        )
    
    # Save IFC file
    ifc.write(output_path)
    print(f"✅ Generated IFC file: {output_path}")
    print(f"   Panel: {panel.name}")
    print(f"   Studs: {len(panel.studs)}")
    print(f"   Openings: {len(panel.openings)}")
    print(f"   Dimensions: {panel.width_mm}mm x {panel.height_mm}mm")
    print(f"   Seismic Zone: {panel.seismic_zone}")


def main():
    """Generate IFC files from demo.py panel definitions"""
    # Import panel creation functions
    from scripts.demo import create_good_panel, create_bad_panel
    
    output_dir = Path(__file__).parent.parent / "test_data"
    output_dir.mkdir(exist_ok=True)
    
    print("\n" + "="*70)
    print("GENERATING IFC FILES FROM PROGRAMMATIC PANEL DEFINITIONS")
    print("="*70 + "\n")
    
    # Generate good panel IFC
    good_panel = create_good_panel()
    good_panel_path = output_dir / "good_panel.ifc"
    create_ifc_from_panel(good_panel, str(good_panel_path))
    
    print()
    
    # Generate bad panel IFC
    bad_panel = create_bad_panel()
    bad_panel_path = output_dir / "bad_panel.ifc"
    create_ifc_from_panel(bad_panel, str(bad_panel_path))
    
    print("\n" + "="*70)
    print("IFC GENERATION COMPLETE")
    print("="*70)
    print(f"\nFiles saved to: {output_dir}")
    print("  • good_panel.ifc")
    print("  • bad_panel.ifc")
    print("\nThese files contain all structural data (studs, openings, dimensions)")
    print("and can now be used as input to demo.py\n")


if __name__ == "__main__":
    main()
